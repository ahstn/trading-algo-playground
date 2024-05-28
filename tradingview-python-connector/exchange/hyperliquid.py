from eth_account import Account
from eth_account.signers.local import LocalAccount
from hyperliquid.exchange import Exchange as HyperliquidExchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

from exchange.exchange import Exchange
from order.order import Order
from order.position import Position


class Hyperliquid(Exchange):
    """
    Implementation of the Exchange interface for the Hyperliquid exchange.
    Uses: https://github.com/hyperliquid-dex/hyperliquid-python-sdk

    See parent class for method descriptions.
    """

    account: Account
    exchange: HyperliquidExchange
    info: Info
    instance: str
    size_decimals = {
        "SOL": 2,
        "AVAX": 2,
        "INJ": 1,
        "SUI": 1,
        "STX": 1,
        "RNDR": 1,
        "FTM": 0,
        "APT": 2,
        "SEI": 0,
        "TIA": 1,
        "PENDLE": 0,
        "NEAR": 1,
        "NTRN": 0,
        "WIF": 0,
        "ONDO": 0,
        "ALT": 0,
        "TAO": 3,
    }

    def __init__(self, secret_file: str, instance_url=constants.MAINNET_API_URL):
        with open(secret_file, "r") as f:
            secret = f.read().strip()

        Account.enable_unaudited_hdwallet_features()
        self.instance = instance_url
        self.account: LocalAccount = Account.from_mnemonic(secret)
        self.exchange = HyperliquidExchange(self.account, instance_url)
        self.info = Info(instance_url, skip_ws=True)

    def asset_contract_rounding_size(self, asset: str) -> int:
        try:
            meta = self.info.meta()
            for asset_info in meta["universe"]:
                if asset_info["name"] == asset:
                    return asset_info["szDecimals"]

            return 0
        except Exception as e:
            print(f"Failed to get asset contract rounding size: {e}")
            return 0

    def place_order(self, order: Order, reduce_only: bool = False, market: bool = False) -> dict:
        contracts = order.contracts

        # Hyperliquid requires contracts to be rounded to a specific decimal place
        # `self.size_decimals` acts as local cache as the API can timeout,
        # worst case we round to 0 which works for all assets, but does oversize
        if order.ticker in self.size_decimals:
            rounding = self.size_decimals[order.ticker]
            contracts = round(order.contracts, self.size_decimals[order.ticker])
            print(f"Using local size decimals for {order.ticker} - {rounding}")
        else:
            rounding = self.asset_contract_rounding_size(order.ticker) or 0
            contracts = round(order.contracts, rounding)
            print(f"Using API size decimals for {order.ticker} - {rounding}")

        if market:
            return self.exchange.market_open(order.ticker, order.is_buy(), order.contracts, None, slippage=0.01)
        else:
            return self.exchange.order(
                order.ticker,
                order.is_buy(),
                contracts,
                order.price,
                {"limit": {"tif": "Gtc"}},
                reduce_only=reduce_only,
            )

    def cancel_existing_orders(self, asset: str) -> list[str]:
        orders: list[str] = []
        try:
            open_orders = self.info.open_orders(self.account.address)
            for order in open_orders:
                if order["coin"] == asset:
                    print(f"- canceling order {order['side']} {order['oid']} for {order['coin']}")
                    self.exchange.cancel(order["coin"], order["oid"])
                    orders.append(order["oid"])
            return orders
        except Exception as e:
            print(f"Failed to get user state, or cancel order: {e}")
            return orders

    def close_positions(self, asset: str) -> bool:
        # Implement position closing logic for Hyperliquid
        pass

    def has_open_position(self, asset: str) -> Position:
        try:
            user_state = self.info.user_state(self.account.address)
            for position in user_state["assetPositions"]:
                if position["position"]["coin"] == asset and position["position"]["szi"]:
                    # HL manages Position direction by positive/negative sizing
                    # Return JSON has it as a string for some reason
                    size = float(position["position"]["szi"])
                    return Position.LONG if size > 0 else Position.SHORT

            return Position.FLAT
        except Exception as e:
            print(f"Failed to get user state: {e}")
            return Position.FLAT

    def open_positions(self) -> dict[str, Position]:
        user_state = self.info.user_state(self.account.address)
        open_positions = {}

        for position in user_state["assetPositions"]:
            direction = Position.LONG if float(position["position"]["szi"]) > 0 else Position.SHORT
            open_positions[position["position"]["coin"]] = direction

        return open_positions
