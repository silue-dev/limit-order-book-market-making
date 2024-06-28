from time import time
from decimal import Decimal
from sortedcontainers import SortedDict

class Order:
    """
    An order.

    Arguments
    ---------
    id         :  The id of the order.
    side       :  The side of the order ('bid' or 'ask').
    price      :  The price of the order.
    quantity   :  The quantity of the order.
    type       :  The type of the order ('market', 'limit', or 'ioc').

    """
    def __init__(self, 
                 id: str,
                 side: str, 
                 price: float, 
                 quantity: float, 
                 type: str,
                 precision: str = '0.1') -> None:
        self.id = id
        self.side = side
        self.precision = precision
        self.price = Decimal(price).quantize(Decimal(precision))
        self.quantity = Decimal(quantity).quantize(Decimal(precision))
        self.type = type
        self.timestamp = None
        
        self.next_order = None
        self.prev_order = None
        self.order_list = None

    def update_quantity(self, new_quantity: Decimal) -> None:
        """
        Updates the quantity of the order.

        Arguments
        ---------
        new_quantity :  The new quantity to assign to the order.

        """
        self.quantity = Decimal(new_quantity).quantize(Decimal(self.precision))
    
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

    Arguments
    ---------
    side  :  The side of the tree w.r.t. the order book ('bid' or 'ask').
    price :  The price level of the order list.

    """
    def __init__(self, side: str, price: Decimal) -> None:
        self.side = side
        self.price = price
        self.head_order = None
        self.tail_order = None
        self.length = 0
        self.volume = 0
        self.last = None  # helper for iteration

    def get_head_order(self) -> Order:
        """
        Returns the head order.

        """
        return self.head_order
    
    def add_order(self, order: Order) -> None:
        """
        Adds a given order to the order list.

        Arguments
        ---------
        order :  The order to be added.

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
    
    def del_order(self, order: Order) -> None:
        """
        Deletes a given order from the order list.

        Arguments
        ---------
        order :  The order to be deleted.
        
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
    An entire side of the order book, composed of all order lists (i.e., 
    price levels) on that side. As the name suggests, this entire side 
    is structured as a (red-black) tree. 
    
    The total order book is composed of two order trees, one for the 
    bid side and one for the ask side.

    Arguments
    ---------
    side :  The side of the tree w.r.t. the order book ('bid' or 'ask').

    """
    def __init__(self, side: str) -> None:
        self.side = side
        self.price_map = SortedDict()  # a sorted dictionary of price levels
        self.prices = self.price_map.keys()  
        self.order_map = {}            # a dictionary of orders by id
        self.depth = 0
        self.volume = 0
        self.num_orders = 0
    
    def add_price(self, price: Decimal) -> None:
        """
        Adds a new given price level to the order tree.

        Arguments
        ---------
        price :  The price level to be added.
        
        """
        new_order_list = OrderList(self.side, price)
        self.price_map[price] = new_order_list
        self.depth += 1

    def del_price(self, price: Decimal) -> None:
        """
        Deletes a given price level from the order tree.

        Arguments
        ---------
        price :  The price level to be deleted.
        
        """
        del self.price_map[price]
        self.depth -= 1
    
    def price_exists(self, price: Decimal) -> bool:
        """
        Checks if a given price level exists in the order tree.

        Arguments
        ---------
        price :  The price level to be checked.

        Returns
        -------
        Whether or not the price level exists.
        
        """
        return price in self.price_map
    
    def order_exists(self, order: Order) -> bool:
        """
        Checks if a given order exists in the order tree.

        Arguments
        ---------
        order :  The order to be checked.

        Returns
        -------
        Whether or not the order exists.
        
        """
        return order in self.order_map

    def get_min_price(self) -> Decimal | None:
        """"
        Returns the lowest price in the order tree.

        """
        if self.depth > 0:
            return self.prices[0]
        else:
            return None
        
    def get_max_price(self) -> Decimal | None:
        """"
        Returns the highest price in the order tree.

        """
        if self.depth > 0:
            return self.prices[-1]
        else:
            return None
        
    def get_order_list(self, price: Decimal) -> OrderList:
        """
        Returns the order list associated with the given price level.

        Arguments
        ---------
        price :  The price level.

        Returns
        -------
        The associated order list.

        """
        return self.price_map[price]

    def get_max_price_order_list(self) -> OrderList:
        """
        Returns the order list associated with the highest price level.

        """
        if self.depth > 0:
            return self.get_order_list(self.max_price())
        else:
            return None

    def get_min_price_order_list(self) -> OrderList:
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

        Arguments
        ---------
        order :  The order to be added.

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

        Arguments
        ---------
        id :  The id of the order to be deleted.
        
        """
        order = self.order_map[id]
        order.order_list.remove_order(order)
        if len(order.order_list) == 0:
            self.del_price(order.price)
        del self.order_map[id]
        self.num_orders -= 1
        self.volume -= order.quantity
