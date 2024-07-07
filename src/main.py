# main.py
import time
from threading import Thread
from exchange import Server
from marketmaker import MarketMaker

def run_market_simulator(
    init_price: float = 100.0,
    bid_prob: float = 0.5,
    take_volume: float = 25.0,
    make_volume: float = 10.0,
    max_order_volume: float = 100.0,
    max_tree_volume: float = 1000.0,
    sleep: float = 0.05) -> None:
    """
    Initializes and starts the market simulation server.

    Arguments
    ---------
    init_price       :  The initial price for the market simulator.
    bid_prob         :  The probability of adding a bid order.
    take_volume      :  The base taker (i.e., market order) volume.
    make_volume      :  The base maker (i.e., limit order) volume.
    max_order_volume :  The maximum volume of a single order.
    max_tree_volume  :  The approximate maximum volume of an order tree.
    sleep            :  The time to sleep between steps in seconds.

    """
    server = Server(
        init_price=init_price,
        bid_prob=bid_prob,
        take_volume=take_volume,
        make_volume=make_volume,
        max_order_volume=max_order_volume,
        max_tree_volume=max_tree_volume,
        sleep=sleep
    )
    server.start()

def run_market_maker(
    user: str = 'basic-market-maker',
    server_url: str = 'http://localhost:5001',
    spread: float = 0.1,
    max_volume: float = 5.0,
    max_delta: float = 100.0,
    sleep: float = 1.0,
    start_delay: float = 5.0) -> None:
    """
    Initializes and starts the market maker agent.

    Arguments
    ---------
    user        :  The username of the market maker agent.
    server_url  :  The URL of the server the market maker connects to.
    spread      :  The spread of the quote.
    max_volume  :  The maximum volume of the quote orders.
    max_delta  :  The maximum (absolute) inventory position size. 
    sleep       :  The time to wait in seconds before deleting the quotes.
    start_delay :  The initial delay before starting the market maker.

    """
    time.sleep(start_delay)
    agent = MarketMaker(user=user, 
                        server_url=server_url)
    agent.run(spread=spread, 
              max_volume=max_volume, 
              max_delta=max_delta,
              sleep=sleep)


if __name__ == '__main__':
    simulator_params = {
        'init_price': 100.0,
        'bid_prob': 0.5,
        'take_volume': 25.0,
        'make_volume': 10.0,
        'max_order_volume': 100.0,
        'max_tree_volume': 1000.0,
        'sleep': 0.05
    }
    market_maker_params = {
        'user': 'basic-market-maker',
        'server_url': 'http://localhost:5001',
        'spread': 0.1,
        'max_volume': 10.0,
        'max_delta': 100.0,
        'sleep': 1.0,
        'start_delay': 1.0
    }

    server_thread: Thread = Thread(target=run_market_simulator, 
                                   kwargs=simulator_params)
    client_thread: Thread = Thread(target=run_market_maker, 
                                   kwargs=market_maker_params)
    server_thread.start()
    client_thread.start()

    server_thread.join()
    client_thread.join()
