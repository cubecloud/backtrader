#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime

from testcommon import getdatadir
import backtrader as bt
from backtrader.strategies.bar_recorder import assert_bar


def _get_trading_calendar(open_hour, close_hour, close_minute):
    cal = bt.TradingCalendar(open=datetime.time(hour=open_hour), close=datetime.time(hour=close_hour, minute=close_minute))
    return cal


def _run_cerebro(use_tcal, open_hour=None, close_hour=None, close_minute=None, tickedgestart=False):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(bt.strategies.BarRecorderStrategy)

    if use_tcal:
        cerebro.addcalendar(_get_trading_calendar(open_hour=open_hour,
                                                  close_hour=close_hour,
                                                  close_minute=close_minute))

    data = bt.feeds.GenericCSVData(
        dataname=getdatadir('ticksample_more.csv'),
        dtformat='%Y-%m-%dT%H:%M:%S.%f',
        timeframe=bt.TimeFrame.Ticks,
    )

    cerebro.resampledata(data, timeframe=bt.TimeFrame.Days, compression=1, tickedgestart=tickedgestart)

    return cerebro.run()[0].bars


def test_no_tcal(main=False):
    bars = _run_cerebro(use_tcal=False, tickedgestart=False)

    assert len(bars) == 4

    assert_bar(bars[0], datetime.datetime(2015, 9, 23, 23, 59, 59, 999989), close=3072)
    assert_bar(bars[1], datetime.datetime(2015, 9, 24, 23, 59, 59, 999989), close=3600)
    assert_bar(bars[2], datetime.datetime(2015, 9, 25, 23, 59, 59, 999989), close=3075)
    assert_bar(bars[3], datetime.datetime(2015, 9, 26, 23, 59, 59, 999989), close=3078)


def test_tcal_8_to_20(main=False):
    """Read tick data and resample to 1 day bars according to trading calendar."""
    bars = _run_cerebro(use_tcal=True,
                       open_hour=8,
                       close_hour=20,
                       close_minute=0,
                       tickedgestart=False,
                       )

    assert len(bars) == 3

    assert_bar(bars[0], datetime.datetime(2015, 9, 24, 20, 0, 0), close=3500)
    assert_bar(bars[1], datetime.datetime(2015, 9, 25, 20, 0, 0), close=3074)
    assert_bar(bars[2], datetime.datetime(2015, 9, 26, 20, 0, 0), close=3078)


def test_tcal_8_to_20_30(main=False):
    """Trading calenadar times are a bit longer and contain some more ticks that would be filtered otherwise."""
    bars = _run_cerebro(use_tcal=True,
                        open_hour=8,
                        close_hour=20,
                        close_minute=30,
                        tickedgestart=False)

    assert len(bars) == 3

    assert_bar(bars[0], datetime.datetime(2015, 9, 24, 20, 30, 0), close=3600)
    assert_bar(bars[1], datetime.datetime(2015, 9, 25, 20, 30, 0), close=3074)
    assert_bar(bars[2], datetime.datetime(2015, 9, 26, 20, 30, 0), close=3078)


def test_tcal_8_to_20_startedge():
    """Data on the edge should be now in following bar instead of current bar"""
    bars = _run_cerebro(use_tcal=True,
                        open_hour=8,
                        close_hour=20,
                        close_minute=0,
                        tickedgestart=True)

    assert len(bars) == 3

    assert_bar(bars[0], datetime.datetime(2015, 9, 24, 20, 0, 0), close=3072)
    assert_bar(bars[1], datetime.datetime(2015, 9, 25, 20, 0, 0), close=3074)
    assert_bar(bars[2], datetime.datetime(2015, 9, 26, 20, 0, 0), close=3078)
