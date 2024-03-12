from collections import deque
from orders import OrderTree

class OrderBook:
    """
    The order book.
    
    """
    def __init__(self):
        self.bids = OrderTree()
        self.asks = OrderTree()
        self.tape = deque()
        self.order_num = 0
    
    def add_order(self, order):
        if order.type == 'market':
            self.add_market_order(order)
        elif order.type == 'limit':
            self.add_limit_order(order)
        elif order.type == 'ioc':
            self.add_ioc_order(order)
    
    def add_market_order(self, order):
        pass

    def add_limit_order(self, order):
        pass

    def add_ioc_order(self, order):
        pass

    def del_order():
        pass

    def get_best_bid(self):
        return self.bids.max_price()

    def get_best_ask(self):
        return self.asks.min_price()
    
    def update_order_num(self):
        self.order_num += 1
        return self.order_num