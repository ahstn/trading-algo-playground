from enum import Enum

import msgspec

from order.action import Action
from order.position import Position


class Order(msgspec.Struct):
    """
    Represents an order for buying or selling a specific instrument.

    It `msgspec.Struct` and defines the structure of an expected order JSON object.
    Helper methods exist to determine the state of the order compared to previous orders.

    TODO: Support pyramiding (or not) orders

    Attributes:
        id (str): The unique identifier for the order.
        action (Action): The type of action for the order (buy or sell).
        contracts (float): The number of contracts or units for the order.
        ticker (str): The ticker symbol of the cryptocurrency.
        position (Position): The current position of the order (flat, short, or long).
        previous_position (Position): The previous position of the order.
        position_size (float): The size of the current position.
        price (float): The price at which the order was executed.
    """

    id: str
    action: Action
    contracts: float
    ticker: str
    position: Position
    previous_position: Position
    position_size: float
    price: float

    def __post_init__(self):
        # Normalizes the price and size to the correct number of decimal places.
        # For HL, Prices should be the lesser of 5 significant figures or 6 decimals.
        # e.g. 1234.5 is valid but 1234.56 is not. 0.001234 is valid, but 0.0012345 is not.
        self.price = round(float(f"{self.price:.5g}"), 6)

        # Normalize contract precision, although this can be exchange and asset specific.
        self.contracts = round(float(f"{self.contracts:.5g}"), 4)

        # Normalise the ticker to remove any suffixes and denominated asset (usually USD)
        self.ticker = self.normalise_ticker(self.ticker)

    def normalise_ticker(self, ticker: str) -> str:
        if "USD" not in ticker:
            raise Exception("Ticker must be denominated in USD")

        # Remove USDC, USDT and USD suffixes from ticker
        return (
            ticker.replace(".P", "")
            .replace("USDC", "")
            .replace("USDT", "")
            .replace("USD", "")
            .replace("-", "")
            .replace("/", "")
        )

    def stop_loss_price(self) -> float:
        """
        Calculates the stop loss price for the given asset and price.
        """
        percent = 0.02  # 20% / 10x leverage
        price: float
        if self.is_buy():
            price = self.price - (self.price * percent)
        else:
            price = self.price + (self.price * percent)

        return round(float(f"{price:.5g}"), 6)

    def to_str(self) -> str:
        return f"{self.action} {self.contracts} {self.ticker} @ {self.price}"

    def is_buy(self) -> bool:
        return self.action == Action.BUY

    def is_reverse_position(self) -> bool:
        return (self.previous_position == Position.SHORT and self.position == Position.LONG) or (
            self.previous_position == Position.LONG and self.position == Position.SHORT
        )

    def is_close_position(self) -> bool:
        return self.previous_position != Position.FLAT and self.position == Position.FLAT

    def is_open_position(self) -> bool:
        return self.previous_position == Position.FLAT and self.position != Position.FLAT
