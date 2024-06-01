use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, Serialize, Deserialize, PartialEq)]
pub enum Position {
    Long,
    Short,
    Flat,
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub enum Action {
    Buy,
    Sell,
}

#[derive(Serialize, Deserialize)]
pub struct Order {
    id: String,
    action: Action,
    contracts: f64,
    ticker: String,
    position: Position,
    previous_position: Position,
    position_size: f64,
    price: f64,
}

impl Order {
    fn normalise_ticker(&self, ticker: &str) -> String {
        if !ticker.contains("USD") {
            panic!("Ticker must be denominated in USD");
        }

        ticker.replace(".P", "")
              .replace("USDC", "")
              .replace("USDT", "")
              .replace("USD", "")
              .replace("-", "")
              .replace("/", "")
    }

    fn is_buy(&self) -> bool {
        matches!(self.action, Action::Buy)
    }

    fn is_reverse_position(&self) -> bool {
        matches!((self.previous_position, self.position), (Position::Short, Position::Long) | (Position::Long, Position::Short))
    }

    fn is_close_position(&self) -> bool {
        self.previous_position != Position::Flat && self.position == Position::Flat
    }

    fn is_open_position(&self) -> bool {
        self.previous_position == Position::Flat && self.position != Position::Flat
    }
}

impl std::fmt::Debug for Order {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        f.debug_struct("Order")
            .field("id", &self.id)
            .field("action", &self.action)
            .field("contracts", &self.contracts)
            .field("ticker", &self.ticker)
            .field("position", &self.position)
            .field("previous_position", &self.previous_position)
            .field("position_size", &self.position_size)
            .field("price", &self.price)
            .finish()
    }
}