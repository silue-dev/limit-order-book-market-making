from orders import OrderTree

class OrderBook:
    def __init__(self):
        self.bids = OrderTree()
        self.asks = OrderTree()
