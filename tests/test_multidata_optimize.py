import datetime

import backtrader as bt

import pickle

class TestStrategy(bt.Strategy):
    params = (
        ('period', 15),
        ('printdata', True),
        ('printops', True),
    )


if __name__ == '__main__':
    #f = pickle.load(open('c:/temp/test.pkl', 'rb'))

    cerebro = bt.Cerebro(maxcpus=1, optreturn=False)

    cerebro.optstrategy(TestStrategy, period=[5, 6, 7])

    data = bt.feeds.YahooFinanceCSVData(
        dataname=r"..\datas\nvda-1999-2014.txt",
        fromdate=datetime.datetime(2000, 1, 1),
        todate=datetime.datetime(2002, 12, 31),
        reverse=False,
        swapcloses=True,
    )
    cerebro.adddata(data)

    data = bt.feeds.YahooFinanceCSVData(
        dataname=r"..\datas\orcl-1995-2014.txt",
        fromdate=datetime.datetime(2000, 1, 1),
        todate=datetime.datetime(2002, 12, 31),
        reverse=False,
        swapcloses=True,
    )
    cerebro.adddata(data)

    cerebro.run()

    with open('c:/temp/test.pkl', 'wb') as f:
        dt = cerebro.runstrats[0][0].observers[1]
        print(dt)
        pickle.dump(dt, f)



