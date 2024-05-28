import functions_framework
from eth_account import Account
from eth_account.signers.local import LocalAccount
from flask import jsonify
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants
from msgspec.json import decode as json_decode

from exchange.hyperliquid import Hyperliquid
from order.order import Order
from order.position import Position


@functions_framework.http
def entrypoint(request):
    """
    "Business Logic" like canceling orders when going flat, or setting reduce_only,
    is kept here to keep exchange implementations simple.
    """
    json = request.get_json(silent=True)
    body = request.get_data()
    if not json:
        return jsonify(success=False)

    print(f"Received HTTP Request: {json}")
    exchange = Hyperliquid(secret_file="secret.txt")
    order = json_decode(body, type=Order)

    # If going flat, ensure we don't overshoot and reverse the position
    # Conditional below handles exiting early if we don't need to place an order.
    reduce_only = order.is_close_position()

    # If going flat, cancel existing orders.
    # If we don't have an existing position return early.
    if order.is_close_position():
        exchange.cancel_existing_orders(order.ticker)
        if exchange.has_open_position(order.ticker) == Position.FLAT:
            return jsonify(success=True)

    if order.is_reverse_position():
        # Check reversing position matches up with the exchange
        position = exchange.has_open_position(order.ticker)
        print(f"In position for {order.ticker} - Exchange: {position}")
        if position != Position.FLAT and position != order.position:
            print(f"Moving to {order.position}. Doubling size to reverse position.")
            order.contracts = order.contracts * 2

    print(f"Placing order: {order.to_str()} reduce={reduce_only}")
    order_response = exchange.place_order(order, reduce_only=reduce_only)

    print(f"Order response: {order_response}")
    return jsonify(success=True)
