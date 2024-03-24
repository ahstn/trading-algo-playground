import eth_account
import functions_framework
from eth_account import Account
from eth_account.signers.local import LocalAccount
from flask import jsonify
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

asset_sizing: dict[str, float] = {
    "SOL": 1,
    "ETH": 0.1,
    "ATOM": 12,
    "ALT": 300,
    "ARB": 70,
    "APT": 10,
    "RNDR": 14,
    "NEAR": 27,
    "SUI": 96,
    "OP": 39,
    "TIA": 9.5,
    "SEI": 170,
    "INJ": 3.5,
}


@functions_framework.http
def hyper_http(request):
    request_json = request.get_json(silent=True)

    if not request_json:
        return jsonify(success=False)

    print(f"Received HTTP Request: {request_json}")
    Account.enable_unaudited_hdwallet_features()
    with open("secret.txt", "r") as f:
        secret = f.read().strip()
    account: LocalAccount = Account.from_mnemonic(secret)
    exchange = Exchange(account, constants.TESTNET_API_URL)

    [asset, size] = determine_asset_and_size(request_json["ticker"])

    if request_json["position"] == "flat":
        cancel_existing_orders(account, asset)

    is_buy = True if request_json["action"] == "buy" else False

    [price, _] = normalize_price_size(request_json["price"], asset)
    print(f"Placing {'Buy' if is_buy else 'Sell'} order: {size} x {asset} @ ${price}")

    order_result = exchange.order(asset, is_buy, size, price, {"limit": {"tif": "Gtc"}})
    print(f"Order response: {order_result}")

    return jsonify(success=True)


def determine_asset_and_size(ticker: str) -> [str, float]:
    """
    Determines the asset and size to trade based on the ticker.
    Static sizing makes closing existing positions easier for now.
    """

    if "USD" not in ticker:
        raise Exception("Ticker must be denominated in USD")

    # Remove USDC, USDT and USD suffixes from ticker
    ticker = ticker.replace("USDC", "").replace("USDT", "").replace("USD", "").replace("-", "").replace("/", "")

    if ticker not in asset_sizing:
        raise Exception("Invalid ticker")

    return ticker, asset_sizing[ticker]


def normalize_price_size(price: float, ticker: str) -> [float, float]:
    """
    Normalizes the price and size to the correct number of decimal places.
    For HL, Prices should be the lesser of 5 significant figures or 6 decimals.
    e.g. 1234.5 is valid but 1234.56 is not. 0.001234 is valid, but 0.0012345 is not.
    """
    target_order_value = 150
    price = round(float(f"{price:.5g}"), 6)
    if "ETH" in ticker:
        size = round(target_order_value / price, 4)
        return price, size
    else:
        size = round(target_order_value / price, 1)
        return price, size


def stop_loss_price(price: float, asset: str, is_buy: bool) -> float:
    """
    Calculates the stop loss price for the given asset and price.
    """
    percent = 0.02  # 20% / 10x leverage
    price = price - (price * percent) if is_buy else price + (price * percent)
    return round(float(f"{price:.5g}"), 6)


def cancel_existing_orders(account: LocalAccount, asset: str):
    """
    When going flat, we want to ensure no other resting orders exist before closing out our position.
    """
    info = Info(constants.MAINNET_API_URL, skip_ws=True)
    open_orders = info.open_orders(account.address)
    for order in open_orders:
        if order["coin"] == asset:
            try:
                info.cancel_order(order["oid"])
                print(f"- canceling order {order['side']} {order['oid']} for {order['coin']}")
            except Exception as e:
                print(f"- failed to cancel order {order['side']} {order['oid']} for {order['coin']} : {e}")
