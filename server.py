# !/usr/bin/env python3
# encoding: utf-8

"""
Module for the cryptocurrency price dashboard, built with streamlit.
The dashboard gives the following options to the user:
    - select the crypto currency
    - see the minutely price for last 24 hours"
    - see the price for last 7 days
    - Manual Refresh
"""

import time
from datetime import datetime, timedelta
import pandas as pd
from requests import HTTPError
import streamlit as st
from pycoingecko import CoinGeckoAPI

__author__ = 'Rajat Dev Sharma'


class CryptoBoard:

    def __init__(self):
        """
        Constructor
        """
        self.coin_map = None
        self.retry_limit = 1
        self.sleep_limit = 60
        self.init_coin_map()

    def init_coin_map(self):
        """
        Create a MAP of coins and the Ids
        :return:
        """
        print('Collecting List of available coins')
        retry = self.retry_limit
        while retry >= 0:
            try:
                self.coin_map = {
                    f"{v['symbol']} [{v['id']}]": v['id'] for v in cg.get_coins_list()
                }
                break
            except HTTPError as h_err:
                print('Retrying in 1 min')
                time.sleep(self.sleep_limit)
            retry -= 1

    @staticmethod
    def curate_response_to_dataframe(data):
        """
        Cureate market data to date, proce dataframe suitable for line graph
        :param data: Tuple (date, price)
        :return: Dataframe
        """
        dates = []
        prices = []
        for x, y in data:
            dates.append(x)
            prices.append(y)
        df = pd.DataFrame({"Prices": prices, "Dates": dates})
        df['Dates'] = pd.to_datetime(df['Dates'], unit='ms', origin='unix')

        return df

    @staticmethod
    def get_minutely_data(coin_id):
        """
        Get minutely data from past 1 day
        :param coin_id: String Id of the coin
        :return: Dataframe with price and dates
        """
        historical_prices = cg.get_coin_market_chart_by_id(
            id=coin_id, vs_currency="usd", days=1
        )['prices']
        return CryptoBoard.curate_response_to_dataframe(data=historical_prices)

    @staticmethod
    def get_historic_data(coin_id, from_timestamp=None, to_timestamp=datetime.utcnow().now()):
        """
        Get historic data for the coin
        :param coin_id: String Id of the coin
        :param from_timestamp: From UTC Datetime
        :param to_timestamp: To UTC Datetime
        :return: Dataframe with prices and dates
        """
        historical_prices = cg.get_coin_market_chart_range_by_id(
            id=coin_id, vs_currency="usd", from_timestamp=from_timestamp.timestamp(),
            to_timestamp=to_timestamp.timestamp()
        )['prices']
        return CryptoBoard.curate_response_to_dataframe(data=historical_prices)


def main():
    """
    Main Function which build the dashboard components and does the work
    :return: None
    """

    st.write("""
    # CRYPTOBOARD 
    *vBeta*
    
    **To start, select the crypto currency**
    """)
    st.selectbox('Select the crypto currency', key='crypto',
                 options=list(cb.coin_map.keys()))

    st.markdown("""---""")

    coin_id = cb.coin_map[st.session_state.crypto]

    historic_hours = cb.get_minutely_data(coin_id=coin_id)
    st.write(f"## LAST *24* HOURS MINUTELY PRICE CHART FOR *{st.session_state.crypto}*")
    st.line_chart(historic_hours.rename(columns={"Dates": "index"}).set_index("index"))

    historic_week = cb.get_historic_data(coin_id=coin_id, from_timestamp=datetime.utcnow().now()-timedelta(days=7))
    st.write(f"## LAST WEEKS PRICE CHART FOR *{st.session_state.crypto}*")
    st.line_chart(historic_week.rename(columns={"Dates": "index"}).set_index("index"))


if __name__ == '__main__':

    cg = CoinGeckoAPI()
    cb = CryptoBoard()
    main()
