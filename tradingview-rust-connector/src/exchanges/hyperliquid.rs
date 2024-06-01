use hyperliquid_rust_sdk::{
    BaseUrl, ExchangeClient, InfoClient
};
use ethers::signers::{LocalWallet, Signer};

use crate::exchanges::exchange::Exchange;
use crate::types::Position;


enum asset {
  SOL

}

struct Hyperliquid {
    client: ExchangeClient,
    info: InfoClient,
    wallet: LocalWallet,
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
}

impl Exchange for Hyperliquid {
    

    fn place_order(&self, asset: &str, order: crate::types::Order, reduce_only: bool) -> std::collections::HashMap<String, String> {
        todo!()
    }

    fn cancel_existing_orders(&self, asset: &str) -> bool {
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
