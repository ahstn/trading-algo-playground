use tracing::info;
use axum::routing::get;
use tokio::net::TcpListener;


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