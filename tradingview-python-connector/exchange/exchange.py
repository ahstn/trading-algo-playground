from abc import ABC, abstractmethod

from order.order import Order
from order.position import Position


class Exchange(ABC):
    """
    An abstract base class representing an exchange interface.
    """

    @abstractmethod
    def place_order(
        self,
        asset: str,
        order: Order,
        reduce_only: bool = False,
    ) -> dict:
        """
        Place an order on the exchange.

        Args:
            asset (str): The asset symbol to trade.
            reduce_only (dict): Whether the order should only reduce a position, not increase/reverse it.
            order (Order): Order object containing price and size info.

        Returns:
            dict: The result of the order placement.
        """
        pass

    @abstractmethod
    def cancel_existing_orders(self, asset: str) -> bool:
        """
        Cancel existing orders for the given asset.

        Args:
            asset (str): The asset symbol for which to cancel orders.

        Returns:
            bool: True if orders were successfully canceled, False otherwise.
        """
        pass

    @abstractmethod
    def close_positions(self, asset: str) -> bool:
        """
        Close existing positions for the given asset.

        Args:
            asset (str): The asset symbol for which to close positions.

        Returns:
            bool: True if positions were successfully closed, False otherwise.
        """
        pass

    @abstractmethod
    def has_open_position(self, asset: str) -> Position:
        """
        Check if there is an open position for the given asset.

        Args:
            asset (str): The asset symbol to check.

        Returns:
            bool: True if there is an open position, False otherwise.
        """
        pass
