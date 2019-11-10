import datetime
import logging
import time

import backtrader as bt


_logger = logging.getLogger(__name__)


class LiveFake(bt.DataBase):
    params = (
        ('starting_value', 200),
        ('tick_interval', datetime.timedelta(seconds=25)),
        ('run_duration', datetime.timedelta(seconds=30)),  # only used when not fastforward
        ('live', True),
        ('backtest_number_of_bars', 10),
        ('use_orig_timeframe', True)
    )

    def __init__(self):
        super(LiveFake, self).__init__()

        self._starttime = None
        self._last_delivered = None

        self._cur_value = None
        self._current_comp = 0
        self._num_bars_delivered = 0
        self._timeframe_in_effect = None
        self._compression_in_effect = None
        self._tmoffset = datetime.timedelta(seconds=-0.5)  # configure offset cause we are senting slightly delayed ticked data (of course!)

    def start(self):
        super(LiveFake, self).start()

        self._starttime = datetime.datetime.utcnow()
        self._cur_value = self.p.starting_value
        self._timeframe_in_effect = self.p.timeframe if self.p.use_orig_timeframe else self._timeframe
        self._compression_in_effect = self.p.compression if self.p.use_orig_timeframe else self._compression

    @staticmethod
    def islive():
        return True

    def _update_line(self, dt, value):
        _logger.info(f"Updating line - Bar Time: {dt} - Value: {value}")

        #if dt.hour == 18:
        #    dt = dt.replace(hour=17, minute=35)
        self.lines.datetime[0] = bt.date2num(dt)
        self.lines.volume[0] = 0.0
        self.lines.openinterest[0] = 0.0

        # Put the prices into the bar
        self.lines.open[0] = value
        self.lines.high[0] = value
        self.lines.low[0] = value
        self.lines.close[0] = value
        self.lines.volume[0] = 0.0
        self.lines.openinterest[0] = 0.0

    def _load(self):
        if self.p.live:
            return self._load_live()
        else:
            return self._load_backtest()

    def _load_backtest(self):
        if self._last_delivered is None:
            self._set_starttime(datetime.datetime.utcnow())
            return None

        if self._num_bars_delivered == self.p.backtest_number_of_bars:
            return False

        if self._timeframe_in_effect == bt.TimeFrame.Ticks:
            delta = self.p.tick_interval * self._compression_in_effect
        elif self._timeframe_in_effect == bt.TimeFrame.Minutes:
            delta = datetime.timedelta(minutes=self._compression_in_effect)
        elif self._timeframe_in_effect == bt.TimeFrame.Days:
            delta = datetime.timedelta(days=self._compression_in_effect)
        else:
            raise RuntimeError(f"Unsupported timeframe: {self.p.timeframe}")

        self._last_delivered += delta
        self._update_line(self._last_delivered, self._cur_value)
        self._cur_value += 1
        self._num_bars_delivered += 1
        return True

    def _set_starttime(self, now):
        t = now
        if self._timeframe_in_effect in [bt.TimeFrame.Minutes, bt.TimeFrame.Ticks]:
            t = t.replace(second=0, microsecond=0)
        elif self._timeframe_in_effect == bt.TimeFrame.Days:
            t = t.replace(minute=0, second=0, microsecond=0)
        self._last_delivered = self._starttime = t

    def _load_live(self):
        now = datetime.datetime.utcnow()

        if self._last_delivered is None:
            # first run, fill last_delivered
            self._set_starttime(now)
            return None

        if now - self._starttime > self.p.run_duration:
            return False

        if self._timeframe_in_effect == bt.TimeFrame.Ticks:
            if now - self._last_delivered < self.p.tick_interval:
                return None
            self._last_delivered += self.p.tick_interval
        else:
            if self._timeframe_in_effect == bt.TimeFrame.Minutes:
                if now.minute == self._last_delivered.minute:
                    return None
                self._last_delivered += datetime.timedelta(minutes=1)
            elif self._timeframe_in_effect == bt.TimeFrame.Days:
                if now.day == self._last_delivered.day:
                    return None
                self._last_delivered += datetime.timedelta(days=1)

        self._current_comp += 1

        if self._current_comp == self._compression_in_effect:  # do not use self._compression as it is modified by resampler already
            self._current_comp = 0

            self._update_line(self._last_delivered, self._cur_value)
            self._cur_value += 1
            return True
        else:
            return None

