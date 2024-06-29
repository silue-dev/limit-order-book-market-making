from time import time
from decimal import Decimal
from collections import deque
from orders import Order, OrderList, OrderTree

class OrderBook:
    """
    The order book.
    
    """
    def __init__(self) -> None:
        self.bids = OrderTree('bid')
        self.asks = OrderTree('ask')
        self.tape = deque()
        self.event_num = 0
    
    def add_order(self, order_dict: dict) -> None:
        """
        Adds an order to the order book.

        Arguments
        ---------
        order_dict :  The order to be added, in dictionary form.

        """
        order = self.to_order_object(order_dict)

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
        quantity_remaining = order.quantity

        if order.side == 'bid':
            while quantity_remaining > 0 and self.asks:
                best_ask_order_list = self.asks.get_min_price_order_list()
                quantity_remaining = self.execute_trade(best_ask_order_list, 
                                                        quantity_remaining)
        elif order.side == 'ask':
            while quantity_remaining > 0 and self.bids:
                best_bid_order_list = self.bids.get_max_price_order_list()
                quantity_remaining = self.execute_trade(best_bid_order_list, 
                                                        quantity_remaining)
        else:
            error_msg = f'Invalid order side "{order.side}". '
            requirement_msg = 'Order side must be either "bid" or "ask". '
            raise ValueError(error_msg + requirement_msg)

    def execute_trade(self, 
                      order_list: OrderList, 
                      quantity: Decimal) -> Decimal:
        """
        Executes a trade of a given quantity on a given order list.

        Arguments
        ---------
        order_list :  The order list on which to perform the trade.
        quantity   :  The volume to trade.

        Returns
        -------
        quantity_remaining :  The volume left to trade.

        """
        quantity_remaining = quantity
        while len(order_list > 0 and quantity_remaining > 0):
            head_order = order_list.head_order
            
            if quantity_remaining < head_order.quantity:
                new_head_order_quantity = head_order.quantity - quantity_remaining
                head_order.update_quantity(new_head_order_quantity)
                quantity_traded = quantity_remaining
                self.add_trade_to_tape(order_list, quantity_traded)
                quantity_remaining = 0

            if quantity_remaining >= head_order.quantity:
                order_list.del_order(order_list.head_order)
                quantity_traded = quantity_remaining
                self.add_trade_to_tape(order_list, quantity_traded)
                quantity_remaining = quantity_remaining - head_order.quantity

        return quantity_remaining
    
    def add_trade_to_tape(self,
                          order_list: OrderList, 
                          quantity_traded: Decimal) -> None:
        """
        Adds a trade to the tape given the trade details.
        
        Arguments
        ---------
        order_list      :  The order list (i.e., price level) at which the trade occurs.
        quantity_traded :  The quantity (i.e., volume) traded.
        
        """
        self.event_num += 1
        trade = {
            'id': self.event_num,
            'price': order_list.price,
            'quantity': quantity_traded,
            'time': time()
        }
        self.tape.append(trade)

    def add_limit_order(self, order: Order):
        """
        Adds a limit order to the order book.

        Arguments
        ---------
        order :  The limit order to be added.

        """
        quantity_remaining = order.quantity

        if order.side == 'bid':
            while quantity_remaining > 0:
                best_bid_order_list = self.bids.get_max_price_order_list()
                if order.price < best_ask_order_list.price:
                    target_bid_order_list = self.bids.get_order_list(order.price)
                    target_bid_order_list.add_order(order)
                    quantity_remaining = 0
                else:
                    while order.price >= best_ask_order_list.price and self.asks:
                        quantity_remaining = self.execute_trade(best_ask_order_list, 
                                                                quantity_remaining)

        elif order.side == 'ask':
            best_ask_order_list = self.asks.get_min_price_order_list()
            if order.price > best_bid_order_list.price:
                target_ask_order_list = self.asks.get_order_list(order.price)
                target_ask_order_list.add_order(order)

        else:
            error_msg = f'Invalid order side "{order.side}". '
            requirement_msg = 'Order side must be either "bid" or "ask". '
            raise ValueError(error_msg + requirement_msg)


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
        return self.bids.get_max_price()

    def get_best_ask(self) -> Decimal:
        """
        Returns the best ask price.

        """
        return self.asks.get_min_price()
    
    def to_order_object(self, order_dict: dict) -> Order:
        """
        Converts an order in dictionary form into an Order object.

        Arguments
        ---------
        order_dict :  The order in dictionary form.

        Returns
        -------
        order :  The order object.

        """
        side = order_dict['side'] 
        price = order_dict['price']
        quantity = order_dict['quantity'] 
        type = order_dict['type']
        
        self.event_num += 1
        id = self.event_num

        order = Order(id=id,
                      side=side,
                      price=price,
                      quantity=quantity,
                      type=type)

        return order