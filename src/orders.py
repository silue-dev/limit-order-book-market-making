from time import time
from sortedcontainers import SortedDict

class Order:
    """
    An order.

    Arguments
    ---------
    side (str):         The side of the order ('bid' or 'ask').
    price (float):      The price of the order.
    quantity (float):   The quantity of the order.
    order_type (str):   The type of the order ('limit' or 'ioc').

    """
    def __init__(self, side, price, quantity, order_type, order_list):
        self.side = side
        self.price = round(price, 1)
        self.quantity = round(quantity, 1)
        self.order_type = order_type
        self.timestamp = None
        
        self.next_order = None
        self.prev_order = None
        self.order_list = order_list
    
    def __str__(self):
        return "{} {} for {} units @ ${} [t={}]".format(self.order_type,
                                                        self.side,
                                                        self.quantity,
                                                        self.price,
                                                        self.timestamp)

class OrderList:
    """
    A (doubly linked) list of orders, representing one price level 
    of the order book.

    """
    def __init__(self):
        self.head_order = None
        self.tail_order = None
        self.length = 0
        self.volume = 0
    
    def add_order(self, order):
        order.timestamp = time()
        if self.length == 0:
            order.next_order = None
            order.prev_order = None
            self.head_order = order
            self.tail_order = order
        else:
            order.next_order = None
            order.prev_order = self.tail_order
            self.tail_order.next_order = order
            self.tail_order = order
        self.length += 1
        self.volume += order.quantity
    
    def del_order(self, order):
        if self.length == 0:
            return
        else:
            self.length -= 1
            self.volume -= order.quantity
            if order.next_order != None and order.prev_order != None:
                order.next_order.prev_order = order.prev_order
                order.prev_order.next_order = order.next_order
            elif order.next_order != None and order.prev_order == None:
                order.next_order.prev_order = None
                self.head_order = order.next_order
            elif order.next_order == None and order.prev_order != None:
                order.prev_order.next_order = None
                self.tail_order = order.prev_order
    
class OrderTree:
    """
    An entire side of the order book, composed of all order lists
    (i.e., price levels) on that side. As the name suggests, this
    entire side is structured as a (red-black) tree. 
    
    To total order book is composed of two order trees, one for 
    the bid side and one for the ask side.

    """
    def __init__(self):
        self.price_map = SortedDict()           # price : OrderList
        self.prices = self.price_map.keys()
        self.order_map = {}                     # order_id : Order
        self.depth = 0
        self.volume = 0
        self.num_orders = 0
    
    def add_price(self, price):
        new_order_list = OrderList()
        self.price_map[price] = new_order_list
        self.depth += 1

    def del_price(self, price):
        del self.price_map[price]
        self.depth -= 1
    
    def price_exists(self, price):
        return price in self.price_map
    
    def order_exists(self, order):
        return order in self.order_map

    def min_price(self):
        if self.depth > 0:
            return self.prices[0]
        else:
            return None
        
    def max_price(self):
        if self.depth > 0:
            return self.prices[-1]
        else:
            return None
        
    def get_order_list(self, price):
        return self.price_map[price]

    def max_price_order_list(self):
        if self.depth > 0:
            return self.get_order_list(self.max_price())
        else:
            return None

    def max_price_order_list(self):
        if self.depth > 0:
            return self.get_order_list(self.min_price())
        else:
            return None
    
    def add_order(self, order):
        # TODO #
        pass

    def del_order(self, order_id):
        order = self.order_map[order_id]
        order.order_list.remove_order(order)
        if len(order.order_list) == 0:
            self.remove_price(order.price)
        del self.order_map[order_id]
        self.num_orders -= 1
        self.volume -= order.quantity