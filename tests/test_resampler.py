from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime
import time

from testcommon import getdatadir
import backtrader as bt
from backtrader.strategies.bar_recorder import assert_bar
import logging
from freezegun import freeze_time


_logger = logging.getLogger(__name__)


def _run_resampler(data_timeframe,
                   data_compression,
                   resample_timeframe,
                   resample_compression,
                   runtime_seconds=27,
                   starting_value=200,
                   tick_interval=datetime.timedelta(seconds=25),
                   live=False,
                   backtest_number_of_bars=10,
                   tickedgestart=False,
                   use_tcal=False,
                   open_hour=None,
                   open_minute=None,
                   close_hour=None,
                   close_minute=None
                   ) -> bt.Strategy:
    _logger.info( "Constructing Cerebro")
    cerebro = bt.Cerebro(bar_on_exit=False)
    cerebro.addstrategy(bt.strategies.BarRecorderStrategy)

    if use_tcal:
        tcal = bt.TradingCalendar(open=datetime.time(hour=open_hour), close=datetime.time(hour=close_hour, minute=close_minute))
        cerebro.addcalendar(tcal)

    data = bt.feeds.LiveFake(timeframe=data_timeframe,
                             compression=data_compression,
                             run_duration=datetime.timedelta(seconds=runtime_seconds),
                             starting_value=starting_value,
                             tick_interval=tick_interval,
                             live=live,
                             backtest_number_of_bars=backtest_number_of_bars,
                             )

    cerebro.resampledata(data, timeframe=resample_timeframe, compression=resample_compression, tickedgestart=tickedgestart)

    # return the recorded bars attribute from the first strategy
    return cerebro.run()[0]


@freeze_time("Jan 1th, 2000", tick=True)
def test_ticks_to_m1_no_startedge():
    """Backtest ticks resampled to M1 bars using tickedgestart=False."""
    strat = _run_resampler(bt.TimeFrame.Ticks,
                           1,
                           resample_timeframe=bt.TimeFrame.Minutes,
                           resample_compression=1,
                           tick_interval=datetime.timedelta(seconds=20),
                           live=False,
                           backtest_number_of_bars=12
                           )

    bars = strat.bars

    assert len(bars) == 4

    assert_bar(bars[0], datetime.datetime(2000, 1, 1, 0, 1), open=200, close=202)
    assert_bar(bars[1], datetime.datetime(2000, 1, 1, 0, 2), open=203, close=205)
    assert_bar(bars[2], datetime.datetime(2000, 1, 1, 0, 3), open=206, close=208)
    assert_bar(bars[3], datetime.datetime(2000, 1, 1, 0, 4), open=209, close=211)


@freeze_time("Jan 1th, 2000", tick=True)
def test_ticks_to_m1_w_startedge():
    """Backtest ticks resampled to M1 bars using tickedgestart=True. Tick on edge should be open for next bar."""
    strat = _run_resampler(bt.TimeFrame.Ticks,
                           1,
                           resample_timeframe=bt.TimeFrame.Minutes,
                           resample_compression=1,
                           tick_interval=datetime.timedelta(seconds=20),
                           live=False,
                           backtest_number_of_bars=13,
                           tickedgestart=True,
                           )

    bars = strat.bars

    assert len(bars) == 4

    assert_bar(bars[0], datetime.datetime(2000, 1, 1, 0, 1), open=200, close=201)
    assert_bar(bars[1], datetime.datetime(2000, 1, 1, 0, 2), open=202, close=204)
    assert_bar(bars[2], datetime.datetime(2000, 1, 1, 0, 3), open=205, close=207)
    assert_bar(bars[3], datetime.datetime(2000, 1, 1, 0, 4), open=208, close=210)


@freeze_time("Jan 1th, 2000", tick=True)
def test_ticks_to_h1_w_startedge():
    """Backtest ticks resampled to H1 bars using tickedgestart=True. Tick on edge should be open for next bar."""
    strat = _run_resampler(bt.TimeFrame.Ticks,
                           1,
                           resample_timeframe=bt.TimeFrame.Minutes,
                           resample_compression=60,
                           tick_interval=datetime.timedelta(seconds=30),
                           live=False,
                           backtest_number_of_bars=370,
                           tickedgestart=True,
                           )

    bars = strat.bars

    assert len(bars) == 3

    assert_bar(bars[0], datetime.datetime(2000, 1, 1, 1, 0), open=200, close=318)
    assert_bar(bars[1], datetime.datetime(2000, 1, 1, 2, 0), open=319, close=438)
    assert_bar(bars[2], datetime.datetime(2000, 1, 1, 3, 0), open=439, close=558)


@freeze_time("Jan 1th, 2000", tick=True)
def test_ticks_to_d1_no_tcal():
    strat = _run_resampler(bt.TimeFrame.Ticks, 1,
                           resample_timeframe=bt.TimeFrame.Days, resample_compression=1,
                           tick_interval=datetime.timedelta(seconds=3600),
                           live=False,
                           backtest_number_of_bars=600,
                           tickedgestart=False,
                           )
    bars = strat.bars

    assert len(bars) == 25

    assert_bar(bars[0], datetime.datetime(2000, 1,  1, 23, 59, 59, 999989), open=200, close=222)
    assert_bar(bars[1], datetime.datetime(2000, 1,  2, 23, 59, 59, 999989), open=223, close=246)
    assert_bar(bars[2], datetime.datetime(2000, 1,  3, 23, 59, 59, 999989), open=247, close=270)
    assert_bar(bars[3], datetime.datetime(2000, 1,  4, 23, 59, 59, 999989), open=271, close=294)
    assert_bar(bars[24], datetime.datetime(2000, 1,  25, 23, 59, 59, 999989), open=775, close=798)


@freeze_time("Jan 1th, 2015", tick=True)
def test_ticks_to_d1_tcal_8_to_20_2015():
    strat = _run_resampler(bt.TimeFrame.Ticks, 1,
                           resample_timeframe=bt.TimeFrame.Days, resample_compression=1,
                           tick_interval=datetime.timedelta(seconds=540),
                           live=False,
                           backtest_number_of_bars=600,
                           tickedgestart=False,
                           use_tcal=True,
                           open_hour=8,
                           close_hour=20,
                           close_minute=0,
                           )
    bars = strat.bars
    assert len(bars) == 2

    assert_bar(bars[0], datetime.datetime(2015, 1, 1, 20, 0, 0), open=200, close=332)
    assert_bar(bars[1], datetime.datetime(2015, 1, 2, 20, 0, 0), open=333, close=492)


@freeze_time("Jan 1th, 2000", tick=True)
def test_ticks_to_d1_tcal_8_to_20_2000():
    """Same as test_ticks_to_d1_tcal_8_to_20_2015 but starting at 200. 1st and 2nd on January are Saturday and Sunday so first trading day is 3th."""
    strat = _run_resampler(bt.TimeFrame.Ticks, 1,
                           resample_timeframe=bt.TimeFrame.Days, resample_compression=1,
                           tick_interval=datetime.timedelta(seconds=540),
                           live=False,
                           backtest_number_of_bars=600,
                           tickedgestart=False,
                           use_tcal=True,
                           open_hour=8,
                           close_hour=20,
                           close_minute=0,
                           )
    bars = strat.bars
    assert len(bars) == 1

    assert_bar(bars[0], datetime.datetime(2000, 1, 3, 20, 0, 0), open=200, close=652)


@freeze_time("Jan 1th, 2015", tick=True)
def test_ticks_to_d1_tcal_8_to_20_30_2015():
    strat = _run_resampler(bt.TimeFrame.Ticks, 1,
                           resample_timeframe=bt.TimeFrame.Days, resample_compression=1,
                           tick_interval=datetime.timedelta(seconds=540),
                           live=False,
                           backtest_number_of_bars=600,
                           tickedgestart=False,
                           use_tcal=True,
                           open_hour=8,
                           close_hour=20,
                           close_minute=30,
                           )
    bars = strat.bars
    assert len(bars) == 2

    assert_bar(bars[0], datetime.datetime(2015, 1, 1, 20, 30, 0), open=200, close=335)
    assert_bar(bars[1], datetime.datetime(2015, 1, 2, 20, 30, 0), open=336, close=495)


@freeze_time("Jan 1th, 2015", tick=True)
def test_ticks_to_d1_tcal_8_to_20_startedge():
    strat = _run_resampler(bt.TimeFrame.Ticks, 1,
                           resample_timeframe=bt.TimeFrame.Days, resample_compression=1,
                           tick_interval=datetime.timedelta(seconds=600),
                           live=False,
                           backtest_number_of_bars=600,
                           tickedgestart=True,
                           use_tcal=True,
                           open_hour=8,
                           close_hour=20,
                           close_minute=0,
                           )
    bars = strat.bars
    assert len(bars) == 2

    assert_bar(bars[0], datetime.datetime(2015, 1, 1, 20, 0, 0), open=200, close=318)
    assert_bar(bars[1], datetime.datetime(2015, 1, 2, 20, 0, 0), open=319, close=462)


@freeze_time("Jan 1th, 2015", tick=True)
def test_ticks_to_d1_tcal_8_to_20():
    strat = _run_resampler(bt.TimeFrame.Ticks, 1,
                           resample_timeframe=bt.TimeFrame.Days, resample_compression=1,
                           tick_interval=datetime.timedelta(seconds=600),
                           live=False,
                           backtest_number_of_bars=600,
                           tickedgestart=False,
                           use_tcal=True,
                           open_hour=8,
                           close_hour=20,
                           close_minute=0,
                           )
    bars = strat.bars
    assert len(bars) == 2

    assert_bar(bars[0], datetime.datetime(2015, 1, 1, 20, 0, 0), open=200, close=319)
    assert_bar(bars[1], datetime.datetime(2015, 1, 2, 20, 0, 0), open=320, close=463)


@freeze_time("Jan 1th, 2015", tick=True)
def test_h1_to_h1_tcal_9_to_18():
    strat = _run_resampler(bt.TimeFrame.Minutes, 60,
                           resample_timeframe=bt.TimeFrame.Minutes, resample_compression=60,
                           tick_interval=datetime.timedelta(seconds=600),
                           live=False,
                           backtest_number_of_bars=30,
                           tickedgestart=False,
                           use_tcal=True,
                           open_hour=9,
                           open_minute=0,
                           close_hour=18,
                           close_minute=0,
                           )
    bars = strat.bars

    assert len(bars) == 30

    assert_bar(bars[17], datetime.datetime(2015, 1, 1, 18, 0, 0), open=217, close=217)
    assert_bar(bars[27], datetime.datetime(2015, 1, 2,  4, 0, 0), open=227, close=227)

    assert(strat.data._filters[0][0]._nexteos == datetime.datetime(2015, 1, 2, 18))


@freeze_time("Jan 1th, 2015", tick=True)
def test_h1_to_h1_tcal_9_to_17_35():
    strat = _run_resampler(bt.TimeFrame.Minutes, 60,
                           resample_timeframe=bt.TimeFrame.Minutes, resample_compression=60,
                           tick_interval=datetime.timedelta(seconds=600),
                           live=False,
                           backtest_number_of_bars=30,
                           tickedgestart=False,
                           use_tcal=True,
                           open_hour=9,
                           open_minute=0,
                           close_hour=17,
                           close_minute=35,
                           )
    bars = strat.bars

    assert len(bars) == 30

    assert_bar(bars[17], datetime.datetime(2015, 1, 1, 18, 0, 0), open=217, close=217)
    assert_bar(bars[27], datetime.datetime(2015, 1, 2,  4, 0, 0), open=227, close=227)

    assert(strat.data._filters[0][0]._nexteos == datetime.datetime(2015, 1, 1, 17, 35))
