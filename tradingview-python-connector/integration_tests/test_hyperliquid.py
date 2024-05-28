import msgspec
import pytest
from hyperliquid.utils import constants

from exchange.hyperliquid import Hyperliquid
from order.action import Action
from order.order import Order
from order.position import Position

"""
These are integration tests and thus depend on Hyperliquid's Testnet API.
See: https://app.hyperliquid-testnet.xyz/

Being a Testnet, there's no uptime guarantee
"""


def test_place_order():
    """
    Price shouldn't matter here given we're trying to market order in.
    """
    order = Order(
        **{
            "id": "Test Order",
            "action": Action.BUY,
            "contracts": 1,
            "position": Position.LONG,
            "previous_position": Position.FLAT,
            "ticker": "SOLUSD",
            "position_size": 0,
            "price": 197.8,
        }
    )

    exchange = Hyperliquid("secret.txt", constants.TESTNET_API_URL)
    response = exchange.place_order(order, market=True)
    print(f"Response: {response}")

    assert response["status"] == "ok"
    assert exchange.has_open_position(order.ticker) == Position.LONG


def test_cancelling_orders():
    """
    Price for this has to be high enough to not trigger an immediate fill.
    """
    order = Order(
        **{
            "id": "Test Order",
            "action": Action.SELL,
            "contracts": 10,
            "position": Position.FLAT,
            "previous_position": Position.LONG,
            "ticker": "NEARUSD",
            "position_size": 0,
            "price": 6.89,
        }
    )

    exchange = Hyperliquid("secret.txt", constants.TESTNET_API_URL)
    response = exchange.place_order(order)
    assert response["status"] == "ok"

    orders_cancelled = exchange.cancel_existing_orders(order.ticker)
    assert len(orders_cancelled) > 0
    assert exchange.has_open_position(order.ticker) == Position.FLAT


@pytest.mark.parametrize("ticker,expected", [("SOL", 2), ("BTC", 5), ("NOT_FOUND", 0)])
def test_asset_contract_rounding_size(ticker: str, expected: int):
    exchange = Hyperliquid("secret.txt", constants.TESTNET_API_URL)
    assert exchange.asset_contract_rounding_size(ticker) == expected
