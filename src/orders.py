from time import time
from sortedcontainers import SortedDict

class Order:
    """
    An order.

    Arguments
    ---------
    side:        The side of the order ('bid' or 'ask').
    price:       The price of the order.
    quantity:    The quantity of the order.
    type:        The type of the order ('market', 'limit', or 'ioc').
    order_list:  The list of orders at the price level this order is in.

    """
    def __init__(self, 
                 side: str, 
                 price: float, 
                 quantity: float, 
                 type: str, 
                 order_list: 'OrderList'):
        self.side = side
        self.price = round(price, 1)
        self.quantity = round(quantity, 1)
        self.type = type
        self.timestamp = None
        
        self.id = None
        self.next_order = None
        self.prev_order = None
        self.order_list = order_list
    
    def __str__(self):
        return '{} {} for {} units @ ${} [t={}]'.format(self.type,
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
        self.last = None  # helper for iteration
    
    def add_order(self, order: Order):
        """
        Adds a given order to the order list.

        """
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
    
    def del_order(self, order: Order):
        """
        Deletes a given order from the order list.
        
        """
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
    
    def __iter__(self):
        self.last = self.head_order
        return self

    def __next__(self):
        if self.last == None:
            raise StopIteration
        else:
            return_value = self.last
            self.last = self.last.next_order
            return return_value
    
class OrderTree:
    """
    An entire side of the order book, composed of all order lists
    (i.e., price levels) on that side. As the name suggests, this
    entire side is structured as a (red-black) tree. 
    
    The total order book is composed of two order trees, one for 
    the bid side and one for the ask side.

    """
    def __init__(self) -> None:
        self.price_map = SortedDict()           # price : OrderList
        self.prices = self.price_map.keys()
        self.order_map = {}                     # id : Order
        self.depth = 0
        self.volume = 0
        self.num_orders = 0
    
    def add_price(self, price: float) -> None:
        """
        Adds a new given price level to the order tree.
        
        """
        new_order_list = OrderList()
        self.price_map[price] = new_order_list
        self.depth += 1

    def del_price(self, price: float) -> None:
        """
        Deletes a given price level from the order tree.
        
        """
        del self.price_map[price]
        self.depth -= 1
    
    def price_exists(self, price: float) -> bool:
        """
        Checks if a given price level exists in the order tree.
        
        """
        return price in self.price_map
    
    def order_exists(self, order: Order) -> bool:
        """
        Checks if a given order exists in the order tree.
        
        """
        return order in self.order_map

    def min_price(self) -> float | None:
        """"
        Returns the lowest price in the order tree.

        """
        if self.depth > 0:
            return self.prices[0]
        else:
            return None
        
    def max_price(self) -> float | None:
        """"
        Returns the highest price in the order tree.

        """
        if self.depth > 0:
            return self.prices[-1]
        else:
            return None
        
    def get_order_list(self, price: float) -> OrderList:
        """
        Returns the order list associated with the given price level.

        """
        return self.price_map[price]

    def max_price_order_list(self) -> OrderList:
        """
        Returns the order list associated with the highest price level.

        """
        if self.depth > 0:
            return self.get_order_list(self.max_price())
        else:
            return None

    def min_price_order_list(self) -> OrderList:
        """
        Returns the order list associated with the lowest price level.

        """
        if self.depth > 0:
            return self.get_order_list(self.min_price())
        else:
            return None
    
    def add_order(self, order: Order) -> None:
        """
        Adds a given order to the order tree.

        """
        if self.order_exists(order.id):
            self.del_order(order.id)
        self.num_orders += 1
        if order.price not in self.price_map:
            self.add_price(order.price)
        self.price_map[order.price].append_order(order)
        self.order_map[order.id] = order
        self.volume += order.quantity

    def del_order(self, id: any) -> None:
        """
        Deletes an order from the order tree, given its order id.
        """
        order = self.order_map[id]
        order.order_list.remove_order(order)
        if len(order.order_list) == 0:
            self.del_price(order.price)
        del self.order_map[id]
        self.num_orders -= 1
        self.volume -= order.quantity