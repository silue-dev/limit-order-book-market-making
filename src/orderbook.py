from collections import deque
from orders import OrderTree

class OrderBook:
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