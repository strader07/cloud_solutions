
import threading
import time
from datetime import datetime
from pytz import timezone
import pandas as pd
# import sys
# from datetime import timedelta

from config import *
from ib_insync import *

import warnings
warnings.simplefilter("ignore")


class LongShort:
    def __init__(self):
        self.ib = IB()

        self.long = []
        self.short = []
        self.qShort = None
        self.qLong = None
        self.adjustedQLong = None
        self.adjustedQShort = None
        self.blacklist = set()
        self.longAmount = 0
        self.shortAmount = 0
        self.timeToClose = None
        self.equity = 0

    def run(self):
        self.ib.connect('127.0.0.1', 7497, clientId=23)

        orders = self.ib.reqAllOpenOrders()
        for _order in orders:
            self.ib.cancelOrder(_order)

        print("Waiting for market to open...")
        tAMO = threading.Thread(target=self.awaitMarketOpen)
        tAMO.start()
        tAMO.join()
        print("Market opened.")

        while True:
            self.rebalance()

            time.sleep(60)
            break

    def awaitMarketOpen(self):
        estern = timezone("US/Eastern")
        while True:
            timenow = datetime.now(estern)
            print(f"Estern time now: {timenow}")
            hour = str(timenow.hour).zfill(2)
            minute = str(timenow.minute).zfill(2)
            timestr = hour+":"+minute
            print(timestr)

            if timestr >= "09:30":
                break
            # break
            time.sleep(60)


    def rebalance(self):
        self.rerank()

        orders = self.ib.reqAllOpenOrders()
        for _order in orders:
            self.ib.cancelOrder(_order)

        print("We are taking a long position in: " + str(self.long))
        print("We are taking a short position in: " + str(self.short))

        long_symbols = [pos[0] for pos in self.long]
        short_symbols = [pos[0] for pos in self.short]
        self.ib.reqExecutions()
        positions = self.ib.positions(account=ACCOUNT_NUMBER)
        self.blacklist.clear()
        for position in positions:
            if position.contract.symbol not in long_symbols:
                if position.contract.symbol not in short_symbols:
                    if position.position > 0:
                        side = "sell"
                    else:
                        side = "buy"
                    self.submitOrder(abs(int(float(position.position))), position.contract.symbol, side)
                else:
                    if position.position > 0:
                        side = "sell"
                        self.submitOrder(abs(int(float(position.position))), position.contract.symbol, side)
                    else:
                        new_qty = self.short[short_symbols.index(position.contract.symbol)][1]
                        if abs(int(float(position.position))) == new_qty:
                            pass
                        else:
                            diff = abs(int(float(position.position))) - new_qty
                            if diff > 0:
                                side = "buy"
                            else:
                                side = "sell"
                            self.submitOrder(abs(diff), position.contract.symbol, side)
                        self.blacklist.add(position.contract.symbol)
            else:
                if position.position < 0:
                    self.submitOrder(abs(int(float(position.position))), position.contract.symbol, "buy")
                else:
                    new_qty = self.long[long_symbols.index(position.contract.symbol)][1]
                    if abs(int(float(position.position))) == new_qty:
                        pass
                    else:
                        diff = abs(int(float(position.position))) - new_qty
                        if diff > 0:
                            side = "sell"
                        else:
                            side = "buy"
                        self.submitOrder(abs(diff), position.contract.symbol, side)
                    self.blacklist.add(position.contract.symbol)

        self.sendBatchOrder(self.long, "buy")
        self.sendBatchOrder(self.short, "sell")

    def get_market_price(self, symbol):
        contracts = [Stock(symbol, "SMART", "USD")]
        self.ib.qualifyContracts(*contracts)
        self.ib.reqMarketDataType(4)
        self.ib.reqMktData(contracts[0], '', False, False)
        self.ib.sleep(1)
        tick = self.ib.ticker(contracts[0])
        price = float(tick.marketPrice())

        return price

    def rerank(self):
        df = pd.read_csv("trades/StockRank.csv")

        longShortAmount = df.shape[0] // 4
        self.long = []
        self.short = []
        for i in range(df.shape[0]):
            if i < longShortAmount:
                self.short.append([df.iloc[i]["Symbol"], 0])
            elif i > (df.shape[0] - 1 - longShortAmount):
                self.long.append([df.iloc[i]["Symbol"], 0])
            else:
                continue

        self.set_position_size()

    def set_position_size(self):
        accountValue = [v for v in self.ib.accountValues() if v.tag == 'NetLiquidationByCurrency' and v.currency == 'BASE'][0]
        equity = int(float(accountValue.value))

        trade_amount = equity * TRADE_EQUITY_PERCENT / 100
        self.shortAmount = trade_amount * LONG_PERCENT / 100
        self.longAmount = trade_amount * SHORT_PERCENT / 100

        long_amount = self.longAmount / len(self.long)
        short_amount = self.shortAmount / len(self.short)
        long_positions = self.long.copy()
        short_positions = self.short.copy()

        long_temp_amount = 0
        short_temp_amount = 0
        for i, position in enumerate(long_positions):
            symbol = position[0]
            last_price = self.get_market_price(symbol)
            print(symbol, last_price)
            try:
                qty = int(round(long_amount / last_price))
            except:
                continue
            if qty == 0:
                qty = 1
            long_temp_amount += qty * last_price
            self.long[i][1] = qty
        for i, position in enumerate(short_positions):
            symbol = position[0]
            last_price = self.get_market_price(symbol)
            print(symbol, last_price)
            try:
                qty = int(round(short_amount / last_price))
            except:
                continue
            if qty == 0:
                qty = 1
            short_temp_amount += qty * last_price
            self.short[i][1] = qty

        self.longAmount = long_temp_amount
        self.shortAmount = short_temp_amount

        print(self.long)
        print(self.short)
        print(self.longAmount, self.shortAmount)

    def sendBatchOrder(self, positions, side):
        incomplete = []
        symbols = [pos[0] for pos in positions]
        for i, symbol in enumerate(symbols):
            if self.blacklist.isdisjoint({symbol}):
                qty = positions[i][1]
                self.submitOrder(qty, symbol, side)

    def submitOrder(self, qty, symbol, side):
        if qty > 0:
            try:
                _order = MarketOrder(side.upper(), qty)
                contracts = [Stock(symbol, "SMART", "USD")]
                self.ib.qualifyContracts(*contracts)
                self.ib.placeOrder(contracts[0], _order)
                self.ib.sleep(2)
                print("Market order of | " + str(qty) + " " + symbol + " " + side + " | completed.")
            except Exception as e:
                print(e)
                print("Order of | " + str(qty) + " " + symbol + " " + side + " | did not go through.")
        else:
            print("Quantity is 0, order of | " + str(qty) + " " + symbol + " " + side + " | not completed.")


ls = LongShort()
ls.run()
