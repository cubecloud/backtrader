import logging

import backtrader as bt

_logger = logging.getLogger(__name__)


def assert_bar(bar, time, open=None, high=None, low=None, close=None):
    assert (bar['time'] == time)

    lables = ['open', 'high', 'low', 'close']
    for l in lables:
        val = locals()[l]
        if val is None:
            continue
        assert (bar[l] == val)


class BarRecorderStrategy(bt.Strategy):
    def __init__(self):
        self.bars = []

    def next(self):
        self.bars.append(dict(time=bt.num2date(self.data.datetime[0]),
                              close=self.data.close[0],
                              open=self.data.open[0],
                              high=self.data.high[0],
                              low=self.data.low[0]))
        _logger.info(f"Recorded bar: {self.bars[-1]}")
