use hyperliquid_rust_sdk::{
    BaseUrl, ClientOrder, ClientLimit, ClientOrderRequest, ExchangeClient, InfoClient, ExchangeResponseStatus
};
use round::round;
use ethers::signers::{LocalWallet, Signer};
use serde_json::json;

use crate::exchanges::exchange::Exchange;
use crate::types::{Order, Position};


enum asset_precision {
  SOL(u32),
  BTC(u32),
  ETH(u32),
  USDT(u32),
}

struct Hyperliquid {
    client: ExchangeClient,
    info: InfoClient,
    wallet: LocalWallet,
}

impl From<Order> for ClientOrderRequest {
    fn from(order: Order) -> ClientOrderRequest {
        ClientOrderRequest {
            sz: order.position_size,
            limit_px: order.price,
            is_buy: order.is_buy(),
            asset: order.ticker.clone(),
            cloid: None,
            order_type: ClientOrder::Limit(ClientLimit { tif: "Gtc".to_string() }),
            reduce_only: order.is_close_position(),
        }
    }
}

impl Hyperliquid {
    /// Creates a new Hyperliquid client
    ///
    /// # Arguments
    ///
    /// * `wallet` - The wallet to use for the client
    /// * `testnet` - Whether to use the testnet URL
    pub async fn new(wallet: LocalWallet, testnet: bool) -> anyhow::Result<Self> {
        let url = if testnet {
            BaseUrl::Testnet
        } else {
            BaseUrl::Mainnet
        };

        let client = ExchangeClient::new(None, wallet.clone(), Some(url), None, None).await?;
        let info = InfoClient::new(None, Some(url)).await?;

        Ok(Hyperliquid { client, info, wallet })
    }

    /// Hyperliquid requires contracts to be rounded to a specific decimal place
    /// worst case we round to 0 which works for all assets, but does oversize
    pub async fn asset_contract_rounding_size(&self, asset: String) -> i32 {
        match self.info.meta().await {
            Ok(meta) => {
                for asset_info in meta.universe {
                    if asset_info.name == asset {
                        return asset_info.sz_decimals.try_into().unwrap_or(0);
                    }
                }
                0
            }
            Err(e) => {
                eprintln!("Failed to get asset contract rounding size: {}", e);
                0
            }
        }
    }
}

impl Exchange for Hyperliquid {
    async fn place_order(&self, order: Order) -> anyhow::Result<serde_json::Value> {
        let mut request: ClientOrderRequest = order.clone().into();
        let precision = self.asset_contract_rounding_size(order.ticker).await;
        request.sz = round(request.sz, precision);

        let response = self.client.order(request, Some(&self.wallet)).await?;
        match response {
            ExchangeResponseStatus::Ok(_response) => Ok(json!({"message": "Order placed"})),
            ExchangeResponseStatus::Err(e) => Err(anyhow::anyhow!("Failed to place order: {}", e)),
        }
    }

    fn cancel_existing_orders(&self, asset: &str) -> bool {
        // let mut orders = Vec::new();
        // match self.info.open_orders(&self.account.address) {
        //     Ok(open_orders) => {
        //         for order in open_orders.as_array().unwrap() {
        //             if order["coin"].as_str().unwrap() == asset {
        //                 println!("- canceling order {} {} for {}", order["side"].as_str().unwrap(), order["oid"].as_str().unwrap(), order["coin"].as_str().unwrap());
        //                 self.exchange.cancel(order["coin"].as_str().unwrap(), order["oid"].as_str().unwrap());
        //                 orders.push(order["oid"].as_str().unwrap().to_string());
        //             }
        //         }
        //     }
        //     Err(e) => {
        //         eprintln!("Failed to get user state, or cancel order: {}", e);
        //     }
        // }
        // orders
        todo!()
    }

    fn close_positions(&self, asset: &str) -> bool {
        todo!()
    }

    async fn has_open_position(&self, asset: &str) -> anyhow::Result<Position> {
        let user_state = self.info.user_state(self.wallet.address()).await?;
        
        for user_position in user_state.asset_positions {
            if user_position.position.coin == asset {
                let size: i32 = user_position.position.szi.parse()?;
                match size {
                    size if size > 0 => return Ok(Position::Long),
                    size if size < 0 => return Ok(Position::Short),
                    _ => return Ok(Position::Flat),
                }
            }
        }

        Ok(crate::types::Position::Flat)
    }
}
