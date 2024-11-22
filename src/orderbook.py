from time import time
from datetime import datetime
from decimal import Decimal
from collections import deque
from collections import defaultdict
from orders import Order, OrderLadder

class OrderBook:
    """
    The order book.

    Arguments
    ---------
    max_order_volume :  The maximum volume of a single order.
    
    """
    def __init__(self, max_order_volume: float = 100.0) -> None:
        self.max_order_volume = max_order_volume
        self.bids = OrderLadder('bid')
        self.asks = OrderLadder('ask')
        self.tape = deque()
        self.event_num = 0
        self.tick_size = Decimal('0.1')
        self.init_time = datetime.fromtimestamp(time()).isoformat()

        self.user_trades = defaultdict(list)
        self.user_positions = defaultdict(lambda: [(self.init_time, Decimal(0))])
        self.user_pnls = defaultdict(lambda: [(self.init_time, Decimal(0))])

        self.mid_prices = []
    
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
                      * 'kind' (str) : The kind of order (i.e., 'market', 'limit', or 'ioc').
                      * 'user' (str) : The name of the user who created the order.

        """
        order = self.to_order_object(order_dict)

        if order.kind == 'market':
            self.add_market_order(order)

        elif order.kind == 'limit':
            self.add_limit_order(order)

        elif order.kind == 'ioc':
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
                order, head_order, traded_price, traded_volume = self.asks.match_order(order)
                self.add_trade_to_tape(order, head_order, traded_price, traded_volume)

        elif order.side == 'ask':
            while order.volume > 0 and self.bids.volume > 0:
                order, head_order, traded_price, traded_volume = self.bids.match_order(order)
                self.add_trade_to_tape(order, head_order, traded_price, traded_volume)
    
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
                order, head_order, traded_price, traded_volume = self.asks.match_order(order)
                self.add_trade_to_tape(order, head_order, traded_price, traded_volume)
            if order.volume > 0:
                self.bids.add_order(order)
        
        elif order.side == 'ask':
            while self.bids.volume > 0 \
                  and order.volume > 0 \
                  and order.price <= self.bids.get_best_price():
                order, head_order, traded_price, traded_volume = self.bids.match_order(order)
                self.add_trade_to_tape(order, head_order, traded_price, traded_volume)
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
                order, head_order, traded_price, traded_volume = self.asks.match_order(order)
                self.add_trade_to_tape(order, head_order, traded_price, traded_volume)
        
        elif order.side == 'ask':
            while self.bids.volume > 0 \
                  and order.volume > 0 \
                  and order.price <= self.bids.get_best_price():
                order, head_order, traded_price, traded_volume = self.bids.match_order(order)
                self.add_trade_to_tape(order, head_order, traded_price, traded_volume)
    
    def add_trade_to_tape(self,
                          order: Order,
                          head_order: Order,
                          price: Decimal, 
                          volume_traded: Decimal) -> None:
        """
        Adds a trade to the tape given the trade details.
        Also updates the user's trades and position.
        
        Arguments
        ---------
        order         :  The incoming order being traded.
        head_order    :  The head order being matched in the order book.
        price         :  The price at which the trade occurs.
        volume_traded :  The volume (i.e., volume) traded.
        
        """
        self.event_num += 1
        trade_time = datetime.fromtimestamp(time()).isoformat()

        order_trade = {
            'id': self.event_num,
            'side': order.side,
            'price': price,
            'volume': volume_traded,
            'time': trade_time,
            'taker': order.user,
            'maker': head_order.user
        }
        head_order_trade = {
            'id': self.event_num,
            'side': head_order.side,
            'price': price,
            'volume': volume_traded,
            'time': trade_time,
            'taker': order.user,
            'maker': head_order.user
        }

        # Update the tape.
        self.tape.append(order_trade)

        # Update the user trades so far.
        if order.user != None: self.user_trades[order.user].append(order_trade)
        if head_order.user != None: self.user_trades[head_order.user].append(head_order_trade)

        # Update all user positions.
        for user in self.user_trades.keys():
            if user not in [order.user, head_order.user]:
                self.user_positions[user].append((trade_time, self.user_positions[user][-1][1]))
            else:
                if order.side == 'bid':
                    if order.user != None: self.user_positions[order.user].append(
                        (trade_time, self.user_positions[order.user][-1][1] + volume_traded)
                        )
                    if head_order.user != None: self.user_positions[head_order.user].append(
                        (trade_time, self.user_positions[head_order.user][-1][1] - volume_traded)
                        )
                elif order.side == 'ask':
                    if order.user != None: self.user_positions[order.user].append(
                        (trade_time, self.user_positions[order.user][-1][1] - volume_traded)
                        )
                    if head_order.user != None: self.user_positions[head_order.user].append(
                        (trade_time, self.user_positions[head_order.user][-1][1] + volume_traded)
                        )
        
        # Update all user pnls.
        for user in self.user_trades.keys():
            self.user_pnls[user].append((trade_time, self.get_pnl(user)))

        # Update the stored mid prices their timestamps.
        self.mid_prices.append((trade_time, self.get_mid_price()))

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

    def get_best_bid(self) -> Decimal | None:
        """
        Returns the best bid price.
        
        """
        return self.bids.get_best_price()

    def get_best_ask(self) -> Decimal | None:
        """
        Returns the best ask price.

        """
        return self.asks.get_best_price()
    
    def get_mid_price(self) -> Decimal | None:
        """
        Returns the mid price.

        """
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        if best_bid and best_ask:
            mid_price = Decimal((best_bid + best_ask) / 2).quantize(Decimal('0.01'))
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
                      * 'price' (float) : The price at which to place the order.
                      * 'volume' (float) : The volume of the order (limited to 100).
                      * 'kind' (str) : The kind of order (i.e., 'market', 'limit', or 'ioc').
                      * 'user' (str) : The name of the user who created the order.

        Returns
        -------
        order :  The order object.

        """
        # Check if the dictionary keys are valid.
        required_keys = ['side', 'price', 'volume', 'kind', 'user']
        if not all(key in order_dict for key in required_keys):
            error_msg = 'Order dictionary must contain the following keys: '
            error_msg += '"side", "price", "volume", "kind", and "user". '
            raise KeyError(error_msg)
        
        # Check if the side is valid.
        side = order_dict['side'] 
        if side not in ['bid', 'ask']:
            error_msg = f'Invalid order side "{order.side}". '
            requirement_msg = 'Order side must be either "bid" or "ask". '
            raise ValueError(error_msg + requirement_msg)
        
        # Get the order details.
        price = order_dict['price']
        volume = max(0, Decimal(order_dict['volume']))
        volume = min(volume, Decimal(self.max_order_volume))
        kind = order_dict['kind']
        user = order_dict['user']
        
        self.event_num += 1
        id = self.event_num

        # Create the order object.
        order = Order(id=id,
                      side=side,
                      price=price,
                      volume=volume,
                      kind=kind,
                      user=user)

        return order
    
    def get_pnl(self, user: str) -> Decimal:
        """
        Returns the PnL of a given user. The PnL is calculated
        as a sum of the realized PnL and the unrealized PnL.

        Arguments
        ---------
        user :  The user.

        Returns
        -------
        The current PnL of the user.

        """
        unrealized_pnl = self.user_positions[user][-1][1] * self.get_mid_price()

        trades = self.user_trades[user]
        realized_pnl = Decimal(0)
        for trade in trades:
            price = Decimal(trade['price'])
            volume = Decimal(trade['volume'])
            if trade['side'] == 'bid':
                realized_pnl -= volume * price
            elif trade['side'] == 'ask':
                realized_pnl += volume * price

        return unrealized_pnl + realized_pnl
    
    def get_visualization_data(self, depth: int = 10) -> dict:
        """
        Returns the order book data for visualization.

        Arguments
        ---------
        depth :  The depth of the order book to return.

        Returns
        -------
        A dictionary with bid and ask prices, and their cumulative volumes.

        """
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        mid_price = Decimal(0)

        if best_bid and best_ask:
            mid_price = (best_bid + best_ask) / 2
            mid_price = mid_price.quantize(Decimal(self.tick_size))
        elif best_bid:
            mid_price = best_bid
        elif best_ask:
            mid_price = best_ask

        bids = []
        asks = []
        cumulative_bid_volume = 0
        cumulative_ask_volume = 0

        for i in range(1, depth + 1):
            bid_price = mid_price - self.tick_size * i
            ask_price = mid_price + self.tick_size * i
            bid_volume = self.bids.price_map[bid_price].volume if bid_price in self.bids.price_map else 0
            ask_volume = self.asks.price_map[ask_price].volume if ask_price in self.asks.price_map else 0

            cumulative_bid_volume += bid_volume
            cumulative_ask_volume += ask_volume

            bids.append((float(bid_price), float(cumulative_bid_volume)))
            asks.append((float(ask_price), float(cumulative_ask_volume)))

        return {'bids': bids, 'asks': asks}
