from datetime import datetime
import json
from binance import Client
import collections
from matplotlib.animation import FuncAnimation
import matplotlib.dates as md
import matplotlib.pyplot as plt

CONFIG_JSON = 'configs/keys.json'
SYMBOL = 'BTCBUSD'
DATES = collections.deque()
PRICES = collections.deque()


def price_function(i):

    if len(PRICES) > 120:
        # get data
        DATES.popleft()
        PRICES.popleft()

    DATES.append(datetime.now())

    current_price = float(client.get_symbol_ticker(symbol=SYMBOL)['price'])
    PRICES.append(current_price)

    print(current_price)

    # clear axis
    ax.cla()

    # Modify Dates
    datenums = md.date2num(DATES)

    # plot PRICES-vs-DATES
    ax.plot(datenums, PRICES)

    plt.ylim(min(PRICES) - 10, max(PRICES) + 10)
    ax.xaxis.set_major_formatter(xfmt)
    plt.xticks(rotation=60)

    return ax


if __name__ == '__main__':

    with open(CONFIG_JSON, 'r') as f:
        data = json.load(f)
    client = Client(api_key=data['apiKey'], api_secret=data['secretKey'])
    # define and adjust figure
    fig = plt.figure(figsize=(10, 5), facecolor='#DEDEDE')
    ax = plt.subplot()
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ani = FuncAnimation(fig=fig, func=price_function, frames=360, interval=30*1000)
    plt.show()