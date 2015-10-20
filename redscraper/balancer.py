import asyncio
import fractions
import time
import math


class LoadBalancer:
    MINUTE = 60
    SECOND = 1

    def __init__(self):
        self.limit = 60
        self.fullness_rate = fractions.Fraction(0, self.limit)
        self.unit_type = LoadBalancer.MINUTE
        self.balancers = []
        self.t = time.time()

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

    def set_requests_limit(self, limit, type=None):
        '''
        :param limit: max requests per unit of time
        :return:
        '''
        type = type or LoadBalancer.MINUTE
        self.limit = limit
        self.unit_type = type

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
            yield from asyncio.sleep(0.5) #TODO: delete hardcoded time
            yield from self.ask()

    def add_balancer(self, balancer):
        self.balancers.append(balancer)
