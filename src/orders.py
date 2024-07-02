from time import time
from decimal import Decimal
from typing import Iterator
from sortedcontainers import SortedDict

class Order:
    """
    An order.

    Arguments
    ---------
    id     :  The id of the order.
    side   :  The side of the order ('bid' or 'ask').
    price  :  The price of the order.
    volume :  The volume of the order.
    kind   :  The kind of the order ('market', 'limit', or 'ioc').

    """
    def __init__(self, 
                 id: str,
                 side: str, 
                 price: float, 
                 volume: float, 
                 kind: str) -> None:
        self.id = id
        self.side = side
        self.tick_size = '0.1'
        if price:
            self.price = Decimal(price).quantize(Decimal(self.tick_size))
        else:
            self.price = None
        self.volume = Decimal(volume).quantize(Decimal(self.tick_size))
        self.kind = kind
        self.timestamp = None
        
        self.next_order = None
        self.prev_order = None
        self.order_list = None

    def add_volume(self, amount: Decimal) -> None:
        """
        Adds a volume amount to the order.

        Arguments
        ---------
        new_volume :  The new volume to assign to the order.

        """
        amount = Decimal(amount).quantize(Decimal(self.tick_size))
        self.volume += amount
        self.order_list.volume += amount
        self.order_list.tree.volume += amount
    
    def __str__(self) -> str:
        """
        Returns a string representation of the order.
        
        """
        return '{} {} for {} units @ ${} [id={}, t={}]'.format(self.kind,
                                                               self.side,
                                                               self.volume,
                                                               self.price,
                                                               self.id,
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
    def __init__(self, tree: 'OrderTree', price: Decimal) -> None:
        self.tree = tree
        self.side = tree.side
        self.price = price
        self.head_order = None
        self.tail_order = None
        self.length = 0
        self.volume = 0
        self.last = None  # helper for iteration

    def get_head_order(self) -> Order:
        """
        Returns the head order of the order list.

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
        order.order_list = self

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
        self.volume += order.volume
    
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
            self.volume -= order.volume
            if order.next_order != None and order.prev_order != None:
                order.next_order.prev_order = order.prev_order
                order.prev_order.next_order = order.next_order
            # If the order is the head order
            elif order.next_order != None and order.prev_order == None:
                order.next_order.prev_order = None
                self.head_order = order.next_order
            # If the order is the tail order
            elif order.next_order == None and order.prev_order != None:
                order.prev_order.next_order = None
                self.tail_order = order.prev_order
    
    def __iter__(self) -> Iterator['OrderList']:
        """
        Initializes the iterator by setting the starting point to 
        the head order of the list and returns the instance itself 
        as an iterator object.

        """
        self.last = self.head_order
        return self

    def __next__(self) -> Order:
        """
        Returns the next order in the list during an iteration.

        """
        if self.last is None:
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
    
    def add_price(self, price: Decimal) -> None:
        """
        Adds a new given price level to the order tree.

        Arguments
        ---------
        price :  The price level to be added.
        
        """
        new_order_list = OrderList(self, price)
        self.price_map[price] = new_order_list
        self.depth += 1

    def del_price(self, price: Decimal) -> None:
        """
        Deletes a given price level from the order tree if it exists.

        Arguments
        ---------
        price :  The price level to be deleted.
        
        """
        if self.price_exists(price):
            del self.price_map[price]
            self.depth -= 1
    
    def get_best_price(self) -> Decimal | None:
        """"
        Returns the best price in the order tree. For a tree 
        of side 'bid', this is the highest price. For a tree 
        of side 'ask', this is the lowest price.

        """
        if self.depth > 0:
            if self.side == 'bid':
                return self.prices[-1]
            elif self.side == 'ask':
                return self.prices[0]
        
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
        
    def get_order_list(self, price: Decimal) -> OrderList:
        """
        Returns the order list associated with the given price level.
        For a tree of side 'bid', this is the order list at the highest price. 
        For a tree of side 'ask', this is the order list at the lowest price.

        Arguments
        ---------
        price :  The price level.

        Returns
        -------
        The associated order list.

        """
        if self.price_exists(price):
            return self.price_map[price]
    
    def get_best_priced_order_list(self) -> OrderList:
        """
        Returns the order list associated with the best price level.

        """
        if self.depth > 0:
            return self.get_order_list(self.get_best_price())
    
    def add_order(self, order: Order) -> None:
        """
        Adds a given order to the order tree. If the order (id) already exists,
        performs an update by simply removing the existing order and adding the new one.

        Arguments
        ---------
        order :  The order to be added.

        """
        if self.order_exists(order.id):
            self.del_order(order.id)

        self.num_orders += 1
        if not self.price_exists(order.price):
            self.add_price(order.price)
        self.price_map[order.price].add_order(order)
        self.order_map[order.id] = order
        self.volume += order.volume

    def del_order(self, id: str) -> bool:
        """
        Deletes an order from the order tree, given its order id.

        Arguments
        ---------
        id :  The id of the order to be deleted.

        Returns
        -------
        Whether or not the deletion took place.
        
        """
        if id in self.order_map:
            order = self.order_map[id]
            order.order_list.del_order(order)

            if order.order_list.length == 0:
                self.del_price(order.price)
            del self.order_map[id]

            self.num_orders -= 1
            self.volume -= order.volume
            return True
        else:
            return False

    def get_head_order(self) -> Order:
        """
        Returns the head order of the order tree.

        """
        if self.volume > 0:
            return self.price_map[self.get_best_price()].get_head_order()
    
    def match_order(self, 
                    order: Order) -> tuple[Order, Decimal, Decimal]:
        """
        Matches the given order on the order tree, executing a trade.

        Arguments
        ---------
        order :  The order to trade.

        Returns
        -------
        updated_order :  The order, with updated volume.
        trade_price   :  The price at which the trade occurred.
        trade_volume  :  The volume that has been traded.

        """
        if self.volume > 0:
            head_order = self.get_head_order()

            trade_price = head_order.price
            trade_volume = min(order.volume, head_order.volume)

            order.volume -= trade_volume
            head_order.add_volume(-trade_volume)

            if head_order.volume <= 0:
                self.del_order(head_order.id)

            return order, trade_price, trade_volume
