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
        self.time = 0
    
    def add_limit_order():
        pass
    
    def add_market_order():
        pass
    
    def del_order():
        pass

    def cancel_order():
        pass

    def get_best_bid():
        pass

    def get_best_ask():
        pass