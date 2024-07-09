# Limit Order Book Market Making
This project implements a limit order book matching engine and a market maker agent in Python. The limit order book matching engine runs on a server that functions as an exchange and simulates a dynamic market environment by processing randomly incoming limit orders, market orders, and optionally IOC orders. The resulting mid-price exhibits behavior similar to a Brownian motion. Meanwhile, the market maker agent continuously sends order requests to the exchange, placing quotes around the mid-price to provide liquidity and generate a steady profit. The agent adjusts these quotes to neutralize their inventory position and maintain a non-directional strategy.

<p align="center">
    <img src="img/result.gif" alt="result" width="500"/>
</p>

## How to Run

Make sure to have both Python (e.g., version 3.12.3) and `pip` installed. Open the root directory of this project in your terminal and run the following command to install all required packages:

```sh
pip install -r requirements.txt
```

Next, to run the simulation along with the market maker, run the following command:

```sh
python src/main.py
```

Finally, open the link to your local server (http://localhost:5001) in a browser to see the market simulation in action.

## Project Structure
The project source code is structured as follows:

- `src/orderbook.py`: Contains the implementation of a limit order book matching engine.

- `src/exchange.py`: Contains the implementation of the market simulation server that runs the limit order book matching engine.

- `src/marketmaker.py`: Contains the implementation of the market maker agent.

- `src/main.py`: Runs both the market simulator and the market maker simultaneously.

