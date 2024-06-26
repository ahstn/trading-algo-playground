use crate::types::Order;
use crate::types::Position;

pub trait Exchange {
    /// Place an order on the exchange.
    ///
    /// # Arguments
    ///
    /// * `asset` - The asset symbol to trade.
    /// * `reduce_only` - Whether the order should only reduce a position, not increase/reverse it.
    /// * `order` - Order object containing price and size info.
    ///
    /// # Returns
    ///
    /// A dictionary containing the result of the order placement.
    async fn place_order(&self, order: Order) -> anyhow::Result<serde_json::Value>;

    /// Cancel existing orders for the given asset.
    ///
    /// # Arguments
    ///
    /// * `asset` - The asset symbol for which to cancel orders.
    ///
    /// # Returns
    ///
    /// `true` if orders were successfully canceled, `false` otherwise.
    async fn cancel_existing_orders(&self, asset: &str) -> anyhow::Result<bool>;

    /// Close existing positions for the given asset.
    ///
    /// # Arguments
    ///
    /// * `asset` - The asset symbol for which to close positions.
    ///
    /// # Returns
    ///
    /// `true` if positions were successfully closed, `false` otherwise.
    fn close_positions(&self, asset: &str) -> bool;

    /// Check if there is an open position for the given asset.
    ///
    /// # Arguments
    ///
    /// * `asset` - The asset symbol to check.
    ///
    /// # Returns
    ///
    /// `true` if there is an open position, `false` otherwise.
    async fn has_open_position(&self, asset: &str) -> anyhow::Result<Position>;
}