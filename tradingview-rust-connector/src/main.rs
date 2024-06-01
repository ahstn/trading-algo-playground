use tracing::info;
use axum::{routing::get, Json};
use tokio::net::TcpListener;

use tradingview_rust_connector::types::Order;


#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let app = axum::Router::new()
        .route("/", get(root));

    let listener = TcpListener::bind("0.0.0.0:3000").await.unwrap();
    info!("Listening on 0.0.0.0:3000");
    axum::serve(listener, app).await.unwrap();
}


async fn root() -> &'static str {
    "Hello World!"
}

async fn handle_order(Json(req): Json<Order>) -> &'static str {
    "Hello World!"
}