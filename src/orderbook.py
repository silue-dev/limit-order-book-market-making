from time import time
from decimal import Decimal
from collections import deque
from orders import Order, OrderTree

class OrderBook:
    """
    The order book.
    
    """
    def __init__(self) -> None:
        self.bids = OrderTree('bid')
        self.asks = OrderTree('ask')
        self.tape = deque()
        self.event_num = 0
        self.tick_size = Decimal('0.1')
    
    def reset(self) -> None:
        """
        Resets the order book.

        """
        self.__init__()
    
    def add_order(self, order_dict: dict) -> None:
        """
        Adds an order to the order book.

        Arguments
        ---------
        order_dict :  The order to be added, in dictionary form. The 
                      dictionary should contain the following keys:
                      * 'side' (str) : The side of the order (i.e., 'bid' or 'ask').
                      * 'price' (Decimal) : The price at which to place the order.
                      * 'volume' (Decimal) : The volume of the order.
                      * 'type' : The type of order (i.e., 'market', 'limit', or 'ioc').

        """
        order = self.to_order_object(order_dict)

        if order.type == 'market':
            self.add_market_order(order)

        elif order.type == 'limit':
            self.add_limit_order(order)

        elif order.type == 'ioc':
            self.add_ioc_order(order)

        return order.id
    
    def add_market_order(self, order: Order) -> None:
        """
        Adds a makert order to the order book.

        Arguments
        ---------
        order :  The market order to be added.

        """
        if order.side == 'bid':
            while order.volume > 0 and self.asks.volume > 0:
                order, traded_price, traded_volume = self.asks.match_order(order)
                self.add_trade_to_tape(traded_price, traded_volume)

        elif order.side == 'ask':
            while order.volume > 0 and self.bids.volume > 0:
                order, traded_price, traded_volume = self.bids.match_order(order)
                self.add_trade_to_tape(traded_price, traded_volume)
    
    def add_limit_order(self, order: Order) -> None:
        """
        Adds a limit order to the order book.

        Note that if the order is so aggressive that it can be matched 
        immediately, we fill the order until either the order price is 
        reached or the entire order volume has been filled. Any remaining 
        order volume is added as liquidity to the limit order book.

        Arguments
        ---------
        order :  The limit order to be added.

        """

        if order.side == 'bid':
            while self.asks.volume > 0 \
                  and order.volume > 0 \
                  and order.price >= self.asks.get_best_price():
                order, traded_price, traded_volume = self.asks.match_order(order)
                self.add_trade_to_tape(traded_price, traded_volume)
            if order.volume > 0:
                self.bids.add_order(order)
        
        elif order.side == 'ask':
            while self.bids.volume > 0 \
                  and order.volume > 0 \
                  and order.price <= self.bids.get_best_price():
                order, traded_price, traded_volume = self.bids.match_order(order)
                self.add_trade_to_tape(traded_price, traded_volume)
            if order.volume > 0:
                self.asks.add_order(order)
    
    def add_ioc_order(self, order: Order) -> None:
        """
        Adds an IOC order to the order book.

        Arguments
        ---------
        order :  The IOC order to be added.

        """
        if order.side == 'bid':
            while self.asks.volume > 0 \
                  and order.volume > 0 \
                  and order.price >= self.asks.get_best_price():
                order, traded_price, traded_volume = self.asks.match_order(order)
                self.add_trade_to_tape(traded_price, traded_volume)
        
        elif order.side == 'ask':
            while self.bids.volume > 0 \
                  and order.volume > 0 \
                  and order.price <= self.bids.get_best_price():
                order, traded_price, traded_volume = self.bids.match_order(order)
                self.add_trade_to_tape(traded_price, traded_volume)
    
    def add_trade_to_tape(self,
                          price: Decimal, 
                          volume_traded: Decimal) -> None:
        """
        Adds a trade to the tape given the trade details.
        
        Arguments
        ---------
        price         :  The price at which the trade occurs.
        volume_traded :  The volume (i.e., volume) traded.
        
        """
        self.event_num += 1
        trade = {
            'id': self.event_num,
            'price': price,
            'volume': volume_traded,
            'time': time()
        }
        self.tape.append(trade)

    def del_order(self, id: str) -> bool:
        """
        Deletes an order from the order book, given its order id.

        Arguments
        ---------
        id :  The id of the order to be deleted.

        Returns
        -------
        Whether or not the deletion took place.

        """
        bid_deletion = self.bids.del_order(id)
        ask_deletion = self.asks.del_order(id)
        return True if bid_deletion or ask_deletion else False

    def get_best_bid(self) -> Decimal:
        """
        Returns the best bid price.
        
        """
        return self.bids.get_best_price()

    def get_best_ask(self) -> Decimal:
        """
        Returns the best ask price.

        """
        return self.asks.get_best_price()
    
    def get_mid_price(self) -> Decimal:
        """
        Returns the mid price.

        """
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        if best_bid and best_ask:
            mid_price = (best_bid + best_ask) / 2
        else:
            mid_price = None
        return mid_price
    
    def to_order_object(self, order_dict: dict) -> Order:
        """
        Converts an order in dictionary form into an Order object.

        Arguments
        ---------
        order_dict :  The order in dictionary form. The dictionary should contain 
                      the following keys:
                      * 'side' (str) : The side of the order (i.e., 'bid' or 'ask').
                      * 'price' (Decimal) : The price at which to place the order.
                      * 'volume' (Decimal) : The volume (i.e., volume) of the order.
                      * 'type' : The type of order (i.e., 'market', 'limit', or 'ioc').

        Returns
        -------
        order :  The order object.

        """
        # Check if the dictionary keys are valid
        required_keys = ['side', 'price', 'volume', 'type']
        if not all(key in order_dict for key in required_keys):
            error_msg = 'Order dictinoary must contain the following keys: '
            error_msg += '"side", "price", "volume", and "type". '
            raise KeyError(error_msg)
        
        # Check if the side is valid
        side = order_dict['side'] 
        if side not in ['bid', 'ask']:
            error_msg = f'Invalid order side "{order.side}". '
            requirement_msg = 'Order side must be either "bid" or "ask". '
            raise ValueError(error_msg + requirement_msg)
        
        # Get the order details
        price = order_dict['price']
        volume = max(0, order_dict['volume'])
        type = order_dict['type']
        
        self.event_num += 1
        id = self.event_num

        # Create the order object
        order = Order(id=id,
                      side=side,
                      price=price,
                      volume=volume,
                      type=type)

        return order
    
    def __str__(self, 
                depth: int = 10, 
                col_width: int = 8) -> str:
        """
        Returns a string representation of the order book.

        """
        # Setup output string and get best prices
        output = '\n'
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()

        # Create order book header
        header_bid_col = 'bid' + ' ' * (col_width - 3)
        header_mid_col = 'price'
        header_ask_col = ' ' * (col_width - 3) + 'ask'
        header_ruler = '|' + '-' * ((col_width * 2) + 15) + '|'
        output += '|  ' + header_bid_col \
                + ' | ' + header_mid_col \
                + ' | ' + header_ask_col \
                + '  |\n'
        output += header_ruler + '\n'

        # Set middle (price) of the order book
        if best_bid and best_ask:
            mid_price = (best_bid + best_ask) / 2
            mid_price = mid_price.quantize(Decimal(self.tick_size))

        elif best_bid and not best_ask:
            mid_price = best_bid

        elif best_ask and not best_bid:
            mid_price = best_ask

        # Return an empty order book if there are no orders
        else:
            return output
        
        # Create the order book ask block
        for i in reversed(range(1, depth)):
            price = mid_price + self.tick_size * (i)
            if price in self.asks.price_map:
                volume = self.asks.price_map[price].volume
                bid_col = ' ' * col_width
                mid_col = str(price) + ' ' * (5 - len(str(price)))
                ask_col = ' ' * (col_width - len(str(volume))) + str(volume)
            else:
                bid_col = ask_col = ' ' * col_width
                mid_col = str(price) + ' ' * (5 - len(str(price)))

            output += '|  ' + bid_col \
                    + ' | ' + mid_col \
                    + ' | ' + ask_col \
                    + '  |\n'
        
        # Create order book mid price level
        price = mid_price
        if price in self.bids.price_map:
            volume = self.bids.price_map[price].volume
            bid_col = str(volume) + ' ' * (col_width - len(str(volume)))
            mid_col = str(price) + ' ' * (5 - len(str(price)))
            ask_col = ' ' * col_width
        elif price in self.asks.price_map:
            volume = self.asks.price_map[price].volume
            bid_col = ' ' * col_width
            mid_col = str(price) + ' ' * (5 - len(str(price)))
            ask_col = ' ' * (col_width - len(str(volume))) + str(volume)
        else:
            bid_col = ask_col = ' ' * col_width
            mid_col = str(price) + ' ' * (5 - len(str(price)))
        
        output += '|  ' + bid_col \
                + ' | ' + mid_col \
                + ' | ' + ask_col \
                + '  |\n'
        
        # Create order book bid block
        for i in range(1, depth + 1):
            price = mid_price - self.tick_size * (i)
            if price in self.bids.price_map:
                volume = self.bids.price_map[price].volume
                bid_col = str(volume) + ' ' * (col_width - len(str(volume)))
                mid_col = str(price) + ' ' * (5 - len(str(price)))
                ask_col = ' ' * col_width
            else:
                bid_col = ask_col = ' ' * col_width
                mid_col = str(price) + ' ' * (5 - len(str(price)))
            
            output += '|  ' + bid_col \
                    + ' | ' + mid_col \
                    + ' | ' + ask_col \
                    + '  |\n'

        return output