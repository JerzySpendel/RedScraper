import asyncio
import fractions
import time
import math
from .settings import config


class LoadBalancer:
    MINUTE = 60
    SECOND = 1

    def __init__(self, limit=None, type=None, sub_balancer=False):
        self.limit = limit
        self.fullness_rate = fractions.Fraction(0, self.limit)
        self.unit_type = type
        self.balancers = []
        self.t = time.time()
        if not sub_balancer:
            self._load_config()

    def _load_config(self):
        if 'load_balancer' not in config:
            return
        LB = config['load_balancer']
        if 'requests' in LB:
            if 'per_minute' in LB['requests']:
                self.add_requests_limit(int(LB['requests']['per_minute']), type=LoadBalancer.MINUTE)
            if 'per_second' in LB['requests']:
                self.add_requests_limit(int(LB['requests']['per_second']), type=LoadBalancer.SECOND)

    @property
    def dt(self):
        return time.time() - self.t

    def _update_fullness_rate(self):
        '''
        `free` - how much of fullness_rate is going to be freed
        `consumed_time` - since last time we called `_update_fullness_rate`
        some time passed and it is `dt`, but not all `dt` have been consumed to
        lower `fullness_rate` so the rest we put to self.t
        '''
        free = self.dt*self.limit/self.unit_type
        if free >= 1:
            self.fullness_rate -= fractions.Fraction(math.floor(free), self.limit)
            if self.fullness_rate < 0:
                self.fullness_rate = fractions.Fraction(0, self.limit)
            consumed_time = math.floor(free)*self.unit_type/self.limit
            self.t += consumed_time #dt is now lower

    def _increment(self):
        self.fullness_rate += fractions.Fraction(1, self.limit)

    def _rest(self):
        '''
        Calculates how much time have to pass to allow another ask()
        '''
        t = self.unit_type/self.limit - self.dt
        if not self.balancers:
            return t if t >= 0 else 0
        else:
            for balancer in self.balancers:
                bt = balancer.unit_type/balancer.limit - self.dt
            t = bt if bt > t else t
        return t if t >= 0 else 0

    def set_requests_limit(self, limit, type=None):
        type = type or LoadBalancer.MINUTE
        self.limit = limit
        self.unit_type = type

    def add_requests_limit(self, limit, type=None):
        '''
        :param limit: max requests per unit of time
        :return:
        '''
        type = type or LoadBalancer.MINUTE
        if self.limit is None or self.unit_type is None:
            self.limit = limit
            self.unit_type = type
        else:
            balancer = LoadBalancer(limit=limit, type=type, sub_balancer=True)
            self.add_balancer(balancer)

    def get_requests_limit(self):
        '''
        :return: max requests per unit of time
        '''
        return (self.limit, self.unit_type)

    @asyncio.coroutine
    def ask(self):
        '''
        Ask for permission to continue code execution
        after yielding from this coroutine
        '''
        self._update_fullness_rate()
        for balancer in self.balancers:
            balancer._update_fullness_rate()
        if self.fullness_rate < 1 and (not any(map(lambda x: x.fullness_rate >= 1, self.balancers))):
            self._increment()
            for balancer in self.balancers:
                balancer._increment()
            return
        else:
            yield from asyncio.sleep(self._rest())
            yield from self.ask()

    def add_balancer(self, balancer):
        if balancer is not None:
            self.balancers.append(balancer)
            return
