import time
import requests
from decimal import Decimal

class MarketMaker:
    """
    The market maker agent.

    Arguments
    ---------
    user       :  The user name of the agent.
    server_url :  The URL of the server.
    volume     :  The base order volume.
    noise      :  The noise added to the order volumes.

    """
    def __init__(self, 
                 user: str, 
                 server_url: str = 'http://localhost:5001',
                 volume: float = 100.0, 
                 noise: float = 10.0) -> None:
        self.user = user
        self.server_url = server_url
        self.volume = volume
        self.noise = noise
        self.precision = Decimal('0.1')

    def get_mid_price(self) -> Decimal:
        """
        Retrieves the current mid price from the server.

        Returns
        -------
        mid_price :  The current mid price as a Decimal.

        """
        response = requests.get(f'{self.server_url}/mid_price')
        if response.status_code == 200:
            price_data = response.json()
            mid_price = price_data['prices'][-1]
            return Decimal(mid_price)
        else:
            raise Exception(f'Failed to retrieve mid price: {response.json()}')
        
    def get_position(self) -> Decimal:
        """
        Retrieves the current inventory position from the server.

        Returns
        -------
        position : The current position as a Decimal.

        """
        response = requests.get(f'{self.server_url}/positions/{self.user}')
        if response.status_code == 200:
            position_data = response.json()
            position = position_data['positions'][-1]
            return Decimal(position)
        else:
            raise Exception(f'Failed to retrieve position: {response.json()}')

    def add_quote(self, 
                  indiff_price: Decimal,
                  spread: Decimal,
                  bid_volume: Decimal,
                  ask_volume: Decimal) -> tuple[str, str]:
        """
        Places a quote (i.e., one limit bid and one limit ask order)
        around the current mid price.

        Arguments
        ---------
        indiff_price :  The price at which the market maker is indifferent
                        to buy or sell. This is also called the fair value
                        price or the reservation price.
        spread       :  The spread between the limit bid and the limit ask.
        bid_volume   :  The volume of the bid limit order.
        ask_volume   :  The volume of the ask limit order.

        Returns
        -------
        The bid and ask order IDs.

        """
        bid_price = (indiff_price - spread / 2)\
            .quantize(self.precision)
        ask_price = (indiff_price + spread / 2)\
            .quantize(self.precision)

        bid_order_dict = {'side': 'bid', 
                          'price': float(bid_price), 
                          'volume': float(bid_volume), 
                          'kind': 'limit',
                          'user': self.user}
        ask_order_dict = {'side': 'ask', 
                          'price': float(ask_price), 
                          'volume': float(ask_volume), 
                          'kind': 'limit',
                          'user': self.user}

        bid_order_id = self.add_order(bid_order_dict)
        ask_order_id = self.add_order(ask_order_dict)
        
        return bid_order_id, ask_order_id
    
    def del_quote(self, 
                  order_ids: tuple[str, str]) -> str:
        """
        Deletes the standing quote in the order book.

        Arguments
        ---------
        order_ids :  The IDs of the orders to be deleted.

        """
        bid_order_id, ask_order_id = order_ids
        self.del_order(bid_order_id)
        self.del_order(ask_order_id)

    def add_order(self, order_dict: dict) -> str:
        """
        Sends an order addition request to the exchange server.

        Arguments
        ---------
        order_dict :  The order dictionary.

        Returns
        -------
        order_id :  The order id.

        """
        response = requests.post(f'{self.server_url}/add_order', 
                                 json=order_dict)
        if response.status_code != 200:
            print(f'Order addition failed: {response.json()}')
        else:
            print(f'Order addition successful: {response.json()}')
        order_id = response.json().get('order_dict').get('id')
        return order_id
    
    def del_order(self, order_id: str) -> None:
        """
        Sends an order deletion request to the exchange server.

        Arguments
        ---------
        order_id :  The order id.

        """
        response = requests.post(f'{self.server_url}/del_order', 
                                 json={'order_id': order_id})
        if response.status_code != 200:
            print(f'Order deletion failed: {response.json()}')
        else:
            print(f'Order deletion successful: {response.json()}')


    def run(self, 
            spread: float,
            max_volume: float,
            max_delta: float,
            sleep: float) -> None:
        """
        Runs the market making strategy. This involves continuously computing 
        the indifference price and placing a quote around that price.

        Arguments
        ---------
        spread     :  The spread of the quote.
        max_volume :  The maximum volume of the quote orders.
        max_delta  :  The maximum (absolute) inventory position size. 
        sleep      :  The time to wait in seconds before deleting the quotes.

        """
        while True:
            try:
                mid_price = self.get_mid_price()
                position = self.get_position()

                # Convert all values to Decimal for accurate computations.
                spread = Decimal(spread)
                max_volume = Decimal(max_volume)
                max_delta = Decimal(max_delta)

                # Calculate the shift based on the position and maximum delta.
                price_shift = (position / max_delta) * spread

                # Adjust indifference price based on position.
                indiff_price = mid_price - price_shift

                # Calculate bid and ask volumes based on position.
                if position >= 0:
                    bid_volume = max_volume * (1 - (position / max_delta))
                    ask_volume = max_volume
                else:
                    bid_volume = max_volume
                    ask_volume = max_volume * (1 + (position / max_delta))

                order_ids = self.add_quote(indiff_price=indiff_price,
                                           spread=spread,
                                           bid_volume=bid_volume,
                                           ask_volume=ask_volume)
                time.sleep(sleep)
                self.del_quote(order_ids)
                
            except Exception as e:
                print(f'An error occurred: {e}')

