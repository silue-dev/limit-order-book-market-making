import random
from decimal import Decimal
from scipy.stats import norm
from collections import deque
import matplotlib.pyplot as plt
from orderbook import OrderBook

class MarketSimulator:
    """
    A market simulator executing trades in a given order book.

    Arguments
    ---------
    ob :  The order book to simulate the trading on.

    """
    def __init__(self, ob: OrderBook) -> None:
        self.ob = ob
        self.bid_id_history = deque()
        self.ask_id_history = deque()
        self.max_volume = 1000
        self.mid_prices = []
    
    def add_random_limit_orders(self,
                                mid_price: Decimal, 
                                scale: float = 100.0,
                                std: float = 0.10, 
                                noise: float = 10.0) -> tuple[deque, deque]:
        """
        Adds random limit orders around a given mid price, distributing them 
        according to a normal distribution influenced by Gaussian noise. 

        Arguments
        ---------
        mid_price :  The reference mid price for placing limit orders.
        scale     :  The scaling factor for order volumes.
        std       :  The standard deviation for normal distribution of volumes.
        noise     :  The noise factor for volume randomness.

        Returns
        -------
        The updated history of bid and ask order IDs.

        """
        mid_price = float(mid_price)
        bid_ids = []
        ask_ids = []

        for i in range(10):
            # Select bid and ask order prices
            bid_price = mid_price - i * 0.1
            ask_price = mid_price + i * 0.1
            
            # Set the order volumes
            bid_volume = scale * norm.pdf(bid_price, 
                                          mid_price - 4 * std, std) \
                                          + random.gauss(0, noise)
            ask_volume = scale * norm.pdf(ask_price, 
                                          mid_price + 4 * std, std) \
                                          + random.gauss(0, noise)
            bid_volume = max(0, bid_volume)
            ask_volume = max(0, ask_volume)

            # Create the order dictionaries
            bid_order_dict = {'side': 'bid', 
                              'price': bid_price, 
                              'volume': bid_volume, 
                              'kind': 'limit'}
            ask_order_dict = {'side': 'ask', 
                              'price': ask_price, 
                              'volume': ask_volume, 
                              'kind': 'limit'}
            
            # Add the orders to the order book and track their IDs
            if bid_price == ask_price:
                if random.random() < 0.5:
                    bid_ids.append(self.ob.add_order(bid_order_dict))
                else:
                    ask_ids.append(self.ob.add_order(ask_order_dict))
            else:
                bid_ids.append(self.ob.add_order(bid_order_dict))
                ask_ids.append(self.ob.add_order(ask_order_dict))

        return deque(bid_ids), deque(ask_ids)

    def add_random_market_order(self, bid_prob: float = 0.5) -> None:
        """
        Adds a random market order to the order book.

        Arguments
        ---------
        bid_prob :  The probability of the order being a bid.

        """
        side = 'bid' if random.random() < bid_prob else 'ask'
        take_volume = 10 + random.gauss(0, 5)
        take_order_dict = {'side': side, 
                           'price': None, 
                           'volume': take_volume, 
                           'kind': 'market'}
        
        self.ob.add_order(take_order_dict)

    def del_old_orders(self) -> None:
        """
        Deletes old orders to maintain a maximum volume in the order book,
        which is dynamically adjusted using Gaussian noise for added realism.

        """
        while self.ob.bids.volume > self.max_volume \
              + abs(random.gauss(0, self.max_volume / 100)):
            bid_id = self.bid_id_history.popleft()
            self.ob.del_order(bid_id)

        while self.ob.asks.volume > self.max_volume \
              + abs(random.gauss(0, self.max_volume / 100)):
            ask_id = self.ask_id_history.popleft()
            self.ob.del_order(ask_id)

    def run(self, steps: int = 10_000, bid_prob: float = 0.5) -> None:
        """
        Runs the market trading simulation for a given number of steps.

        Arguments
        ---------
        steps    :  The number of simulation steps to execute.
        bid_prob :  The probability of a market order being a bid.

        """
        # Initialize the order book
        bid_ids, ask_ids = self.add_random_limit_orders(mid_price=Decimal(100))

        # Track the orders and the price
        self.bid_id_history += bid_ids
        self.ask_id_history += ask_ids
        self.mid_prices.append(self.ob.get_mid_price())
        
        # Simulate market trading
        for _ in range(steps):
            # Add a market order and compute the (new) mid price
            self.add_random_market_order(bid_prob=bid_prob)
            mid_price = self.ob.get_mid_price()
            self.mid_prices.append(mid_price)

            # Set limit orders around the mid price
            bid_ids, ask_ids = self.add_random_limit_orders(mid_price=mid_price, 
                                                            scale=10)
            
            # Track the orders so far
            self.bid_id_history += bid_ids
            self.ask_id_history += ask_ids

            # Delete old orders
            self.del_old_orders()

            print(self.ob)
        
        self.plot_mid_prices()

    def plot_mid_prices(self) -> None:
        """
        Plots the mid prices collected during the simulation.

        """
        plt.plot(self.mid_prices)
        plt.xlabel('Time Steps', fontweight='bold')
        plt.ylabel('Mid Price', fontweight='bold')
        plt.title('Mid Price over Time', fontweight='bold')
        plt.show()


if __name__ == '__main__':
    ob = OrderBook()
    sim = MarketSimulator(ob)
    sim.run(steps=10_000, bid_prob=0.5)
