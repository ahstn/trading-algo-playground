import msgspec
import pytest

from order.action import Action
from order.order import Order
from order.position import Position

order_data = {
    "id": "Test Order",
    "action": Action.BUY,
    "contracts": 22.222,
    "position": Position.LONG,
    "previous_position": Position.FLAT,
    "ticker": "NEARUSDT",
    "position_size": 0,
    "price": 6.96,
}


def test_decode_success():
    order = msgspec.json.decode(
        b"""{ 
            "id": "Test Order",
            "action": "BUY",
            "contracts": 22.222,
            "position": "LONG",
            "previous_position": "FLAT",
            "ticker": "NEARUSDT",
            "position_size": 0,
            "price": 6.96
        }""",
        type=Order,
    )

    assert order.id == "Test Order"
    assert order.action == Action.BUY
    assert order.contracts == 22.22
    assert order.position == Position.LONG
    assert order.previous_position == Position.FLAT


def test_decode_failure():
    with pytest.raises(Exception) as e:
        msgspec.json.decode(
            b"""{ 
                "contracts": 22.222,
                "previous_position": "FLAT",
                "ticker": "NEARUSDT",
                "position_size": 0,
                "price": 6.96
            }""",
            type=Order,
        )
    assert e.errisinstance(msgspec.ValidationError)
    assert "missing required field" in str(e.value)


@pytest.mark.parametrize(
    "ticker,expected",
    [
        ("ETHUSDT", "ETH"),
        ("ETHUSDT.P", "ETH"),
        ("SOL/USDT", "SOL"),
        ("SOL-USDT", "SOL"),
        ("ATOMUSD", "ATOM"),
        ("APTUSDC", "APT"),
        ("ARBUSDT", "ARB"),
        ("NEARUSDT", "NEAR"),
    ],
)
def test_normalize_ticker(ticker: str, expected: bool):
    order_data["ticker"] = ticker
    order = Order(**order_data)
    assert order.normalise_ticker(ticker) == expected


@pytest.mark.parametrize(
    "price,contracts,expected",
    [
        (float(3500), float(0.165112), float(0.1651)),
        (float(7), float(22.22222), float(22.2222)),
        (float(150), float(1.12345), float(1.1234)),
    ],
)
def test_init_size(price: float, contracts: float, expected: bool):
    order_data["price"] = price
    order_data["contracts"] = contracts
    order = Order(**order_data)
    assert order.contracts == expected


@pytest.mark.parametrize(
    "price,expected",
    [
        (float(3500.345), float(3500.3)),
        (float(197.5845), float(197.58)),
    ],
)
def test_init_price(price: float, expected: bool):
    order_data["price"] = price
    order = Order(**order_data)
    assert order.price == expected


@pytest.mark.parametrize(
    "action_value,expected",
    [
        (Action.BUY, True),
        (Action.SELL, False),
    ],
)
def test_is_buy(action_value: Action, expected: bool):
    order_data["action"] = action_value
    order = Order(**order_data)
    assert order.is_buy() == expected


@pytest.mark.parametrize(
    "previous_position,position,expected",
    [
        (Position.LONG, Position.SHORT, True),
        (Position.SHORT, Position.LONG, True),
        (Position.LONG, Position.LONG, False),
        (Position.SHORT, Position.SHORT, False),
        (Position.FLAT, Position.FLAT, False),
        (Position.FLAT, Position.LONG, False),
    ],
)
def test_is_reverse_position(previous_position: Position, position: Position, expected: bool):
    order_data["previous_position"] = previous_position
    order_data["position"] = position
    order = Order(**order_data)
    assert order.is_reverse_position() == expected


@pytest.mark.parametrize(
    "previous_position,position,expected",
    [
        (Position.FLAT, Position.LONG, True),
        (Position.FLAT, Position.SHORT, True),
        (Position.FLAT, Position.FLAT, False),
    ],
)
def test_is_open_position(previous_position: Position, position: Position, expected: bool):
    order_data["previous_position"] = previous_position
    order_data["position"] = position
    order = Order(**order_data)
    assert order.is_open_position() == expected
