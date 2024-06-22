use tracing::info;
use axum::{routing::get, routing::post, Json, Router};
use tokio::net::TcpListener;
use ethers::signers::LocalWallet;
use std::sync::Arc;
use tokio::sync::Mutex;

use tradingview_rust_connector::types::{Order, Position};
use tradingview_rust_connector::exchanges::hyperliquid::Hyperliquid;

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let wallet: LocalWallet = "your_wallet_private_key".parse().unwrap();
    let exchange = Arc::new(Mutex::new(Hyperliquid::new(wallet, true).await.unwrap()));

    let app = Router::new()
        .route("/", get(root))
        .route("/order", post(handle_order))
        .layer(axum::AddExtensionLayer::new(exchange));

    let listener = TcpListener::bind("0.0.0.0:3000").await.unwrap();
    info!("Listening on 0.0.0.0:3000");
    axum::Server::from_tcp(listener).unwrap().serve(app.into_make_service()).await.unwrap();
}

async fn root() -> &'static str {
    "Hello World!"
}

async fn handle_order(
    Json(order): Json<Order>,
    axum::extract::Extension(exchange): axum::extract::Extension<Arc<Mutex<Hyperliquid>>>,
) -> Json<serde_json::Value> {
    let exchange = exchange.lock().await;

    // If going flat, ensure we don't overshoot and reverse the position
    let reduce_only = order.is_close_position();

    // If going flat, cancel existing orders.
    // If we don't have an existing position return early.
    if order.is_close_position() {
        exchange.cancel_existing_orders(&order.ticker).await.unwrap();
        if exchange.has_open_position(&order.ticker).await.unwrap() == Position::Flat {
            return Json(serde_json::json!({ "success": true }));
        }
    }

    if order.is_reverse_position() {
        // Check reversing position matches up with the exchange
        let position = exchange.has_open_position(&order.ticker).await.unwrap();
        println!("In position for {} - Exchange: {:?}", order.ticker, position);
        if position != Position::Flat && position != order.position {
            println!("Moving to {:?}. Doubling size to reverse position.", order.position);
            order.contracts *= 2.0;
        }
    }

    println!("Placing order: {} reduce={}", order.to_str(), reduce_only);
    let order_response = exchange.place_order(order).await.unwrap();

    println!("Order response: {:?}", order_response);
    Json(serde_json::json!({ "success": true }))
}
