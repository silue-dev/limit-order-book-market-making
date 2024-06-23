from collections import deque
from orders import Order, OrderTree

class OrderBook:
    """
    The order book.
    
    """
    def __init__(self) -> None:
        self.bids = OrderTree()
        self.asks = OrderTree()
        self.tape = deque()
        self.order_num = 0
    
    def add_order(self, order: Order) -> None:
        """
        Adds an order to the order book.

        Arguments
        ---------
        order :  The order to be added.

        """
        if order.type == 'market':
            self.add_market_order(order)
        elif order.type == 'limit':
            self.add_limit_order(order)
        elif order.type == 'ioc':
            self.add_ioc_order(order)
    
    def add_market_order(self, order: Order):
        """
        Adds a makert order to the order book.

        Arguments
        ---------
        order :  The market order to be added.

        """
        pass

    def add_limit_order(self, order: Order):
        """
        Adds a limit order to the order book.

        Arguments
        ---------
        order :  The limit order to be added.

        """
        pass

    def add_ioc_order(self, order: Order):
        """
        Adds an IOC order to the order book.

        Arguments
        ---------
        order :  The IOC order to be added.

        """
        pass

    def del_order():
        pass

    def get_best_bid(self):
        """
        Returns the best bid price.
        
        """
        return self.bids.max_price()

    def get_best_ask(self) -> float:
        """
        Returns the best ask price.

        """
        return self.asks.min_price()
    
    def update_order_num(self) -> int:
        """
        Updates the number of orders so far by incrementing it.

        """
        self.order_num += 1
        return self.order_num
