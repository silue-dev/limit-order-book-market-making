import time
import random
import threading
from decimal import Decimal
from scipy.stats import norm
from collections import deque
from flask import Flask, render_template, jsonify, request
from orderbook import OrderBook

class MarketSimulator:
    """
    The market simulator.

    Arguments
    ---------
    ob              :  The order book to simulate the market on.
    max_tree_volume :  The approximate maximum volume of an order tree.
    
    """
    def __init__(self, 
                 ob: OrderBook, 
                 max_tree_volume: float = 1000.0) -> None:
        self.ob = ob
        self.max_tree_volume = max_tree_volume

        self.bid_id_history = deque()
        self.ask_id_history = deque()
        self.lock = threading.Lock()
        self.default_user = 'basic-market-maker'

    def add_random_limit_orders(self, 
                                mid_price: Decimal, 
                                volume: float = 100.0,
                                std: float = 0.10, 
                                noise: float = 10.0) -> tuple[deque[int], 
                                                              deque[int]]:
        """
        Adds random limit orders to the order book.

        Arguments
        ---------
        mid_price :  The current mid price.
        volume    :  The base order volume.
        std       :  The standard deviation for the price distribution.
        noise     :  The noise added to the order volumes.

        Returns
        -------
        bid_ids, ask_ids :  The IDs of the added bid and ask orders.

        """
        mid_price = float(mid_price)
        bid_ids = []
        ask_ids = []

        for i in range(10):
            bid_price = mid_price - i * 0.1
            ask_price = mid_price + i * 0.1

            bid_volume = volume * norm.pdf(bid_price, 
                                          mid_price - 4 * std, std) \
                                          + random.gauss(0, noise)
            ask_volume = volume * norm.pdf(ask_price, 
                                          mid_price + 4 * std, std) \
                                          + random.gauss(0, noise)
            bid_volume = max(0, bid_volume)
            ask_volume = max(0, ask_volume)

            bid_order_dict = {'side': 'bid', 
                              'price': bid_price, 
                              'volume': bid_volume, 
                              'kind': 'limit',
                              'user': None}
            ask_order_dict = {'side': 'ask', 
                              'price': ask_price, 
                              'volume': ask_volume, 
                              'kind': 'limit',
                              'user': None}

            if bid_price == ask_price:
                if random.random() < 0.5:
                    bid_ids.append(self.ob.add_order(bid_order_dict))
                else:
                    ask_ids.append(self.ob.add_order(ask_order_dict))
            else:
                bid_ids.append(self.ob.add_order(bid_order_dict))
                ask_ids.append(self.ob.add_order(ask_order_dict))

        return deque(bid_ids), deque(ask_ids)

    def add_random_market_order(self, 
                                user: str, 
                                volume: float = 10.0,
                                bid_prob: float = 0.5) -> None:
        """
        Adds a random market order to the order book.

        Arguments
        ---------
        user     :  The user placing the order.
        volume   :  The base order volume.
        bid_prob :  The probability of the order being a bid.

        """
        side = 'bid' if random.random() < bid_prob else 'ask'
        take_volume = volume + random.gauss(0, volume)
        take_order_dict = {'side': side, 
                           'price': None, 
                           'volume': take_volume, 
                           'kind': 'market',
                           'user': user}
        self.ob.add_order(take_order_dict)

    def del_old_orders(self) -> None:
        """
        Deletes old orders from the order book.

        """
        while self.ob.bids.volume > self.max_tree_volume \
                                    + abs(random.gauss(0, self.max_tree_volume / 100)):
            bid_id = self.bid_id_history.popleft()
            self.ob.del_order(bid_id)
        while self.ob.asks.volume > self.max_tree_volume \
                                    + abs(random.gauss(0, self.max_tree_volume / 100)):
            ask_id = self.ask_id_history.popleft()
            self.ob.del_order(ask_id)

    def run(self, 
            init_price: float = 100.0,
            steps: int = None, 
            take_volume: float = 10.0,
            make_volume: float = 10.0,
            bid_prob: float = 0.5,
            sleep: float = 0.1) -> None:
        """
        Runs the market simulator.

        Arguments
        ---------
        init_price  :  The initial price.
        steps       :  The number of steps to run. If None, runs indefinitely.
        take_volume :  The base taker (i.e., market order) volume.
        make_volume :  The base maker (i.e., limit order) volume.
        bid_prob    :  The probability of adding a bid order.
        sleep       :  The time to sleep between steps.

        """
        bid_ids, ask_ids = self.add_random_limit_orders(
            mid_price=Decimal(init_price)
        )
        self.ob.user_positions[self.default_user] = Decimal(0)

        self.bid_id_history += bid_ids
        self.ask_id_history += ask_ids

        step = 0
        while steps is None or step < steps:
            self.add_random_market_order(user=None, 
                                         volume=take_volume, 
                                         bid_prob=bid_prob)
            mid_price = self.ob.get_mid_price()
            bid_ids, ask_ids = self.add_random_limit_orders(mid_price=mid_price, 
                                                            volume=make_volume)
            self.bid_id_history += bid_ids
            self.ask_id_history += ask_ids
            self.del_old_orders()
            step += 1
            time.sleep(sleep)

class Server:
    """
    The server running the market simulator.

    Arguments
    ---------
    init_price       :  The initial price.
    steps            :  The number of steps to run. If None, runs indefinitely.
    take_volume      :  The base taker (i.e., market order) volume.
    make_volume      :  The base maker (i.e., limit order) volume.
    max_order_volume :  The maximum volume of a single order.
    max_tree_volume  :  The approximate maximum volume of an order tree.
    bid_prob         :  The probability of adding a bid order.
    sleep            :  The time to sleep between steps.
    
    """
    def __init__(self, 
                 init_price: float = 100.0,
                 steps: int = None, 
                 take_volume: float = 10.0,
                 make_volume: float = 10.0,
                 max_order_volume: float = 100.0,
                 max_tree_volume: float = 1000.0,
                 bid_prob: float = 0.5,
                 sleep: float = 0.1) -> None:
        self.init_price = init_price
        self.steps = steps
        self.take_volume = take_volume
        self.make_volume = make_volume
        self.max_order_volume = max_order_volume
        self.max_tree_volume = max_tree_volume
        self.bid_prob = bid_prob
        self.sleep = sleep
        self.app = Flask(__name__)
        self.sim = None

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/mid_price')
        def mid_price():
            with self.sim.lock:
                mid_price_data = {
                    'x': list(range(len(self.sim.ob.mid_prices))),
                    'y': self.sim.ob.mid_prices
                }
            return jsonify(mid_price_data)

        @self.app.route('/orderbook')
        def orderbook():
            with self.sim.lock:
                ob_data = self.sim.ob.get_visualization_data()
            return jsonify(ob_data)
        
        @self.app.route('/add_order', methods=['POST'])
        def add_order():
            """
            Adds an order.

            Arguments (from request.json)
            ---------
            side   :  The side of the order ('bid' or 'ask').
            price  :  The price of the order.
            volume :  The volume of the order.
            kind   :  The kind of order ('market', 'limit', or 'ioc').
            user   :  The user placing the order.

            """
            data = request.json

            side = data.get('side')
            price = data.get('price')
            volume = data.get('volume')
            kind = data.get('kind')
            user = data.get('user')
            if side not in ['bid', 'ask']:
                return jsonify({'error': 'Invalid order side'}), 400
            with self.sim.lock:
                order_dict = {'side': side, 
                              'price': price, 
                              'volume': volume, 
                              'kind': kind,
                              'user': user}
                order_id = self.sim.ob.add_order(order_dict)
                order_dict['id'] = order_id
            return jsonify({'order_dict': order_dict})
        
        @self.app.route('/del_order', methods=['POST'])
        def del_order():
            data = request.json
            order_id = data.get('order_id')
            with self.sim.lock:
                result = self.sim.ob.del_order(order_id)
            if result:
                return jsonify({'order_id': order_id})
            else:
                return jsonify({'order_id': str(order_id)}), 400
        
        @self.app.route('/users')
        def users():
            """
            Returns the list of users.

            Returns
            -------
            The list of users.

            """
            with self.sim.lock:
                users_list = list(self.sim.ob.user_positions.keys())
            return jsonify(users_list)

        @self.app.route('/pnl/<user>')
        def pnl(user):
            """
            Returns the PnL of a user.

            Arguments
            ---------
            user :  The user.

            Returns
            -------
            The PnL of the user.

            """
            with self.sim.lock:
                user_pnl = self.sim.ob.get_pnl(user)
            return jsonify({'user': user, 'pnl': str(user_pnl)})
        
        @self.app.route('/pnl_history/<user>')
        def pnl_history(user):
            """
            Returns the PnL history of a user.

            Arguments
            ---------
            user :  The user.

            Returns
            -------
            The PnL history of the user.

            """
            with self.sim.lock:
                pnl_history = self.sim.ob.user_pnls[user]
                pnl_data = list(map(float, pnl_history))
            return jsonify({'user': user, 'pnl': pnl_data})

    def run_simulation(self) -> None:
        """
        Runs the market simulation.
        
        """
        ob = OrderBook(max_order_volume=self.max_order_volume)
        self.sim = MarketSimulator(ob=ob,
                                   max_tree_volume=self.max_tree_volume)
        self.sim.run(init_price=self.init_price,
                     steps=self.steps, 
                     take_volume=self.take_volume,
                     make_volume=self.make_volume,
                     bid_prob=self.bid_prob,
                     sleep=self.sleep)

    def start(self) -> None:
        """
        Starts the server.

        """
        threading.Thread(target=self.run_simulation).start()
        self.app.run(debug=False, port=5001)


if __name__ == '__main__':
    server = Server(init_price=100.0,
                    bid_prob=0.5,
                    take_volume=25.0,
                    make_volume=10.0,
                    max_order_volume=100.0,
                    max_tree_volume=1000.0,
                    sleep=0.05)
    server.start()
