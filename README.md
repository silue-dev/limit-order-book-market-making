# Limit Order Book Matching Engine
This project implements a limit order book matching engine in Python. The engine simulates a dynamic market environment by processing randomly incoming limit orders, market orders, and optionally IOC orders. The resulting mid-price exhibits behavior similar to a Brownian motion.

## How to Run
Make sure to have both Python (e.g., version 3.12.3) and `pip` installed. Open the root directory of this project in your terminal and run the following command to install all required packages:

```
pip install -r requirements.txt
```

Next, to run the simulation, run the following command:
```
python src/main.py
```

In your terminal, you should now see a [link](http://localhost:5001) to your local server. Open it in a browser to see the market simulation in action.