from asyncio import sleep
from unittest import IsolatedAsyncioTestCase


from ..std2.timeit import timeit


class TimeIt(IsolatedAsyncioTestCase):
    async def test_1(self) -> None:
        t = 0.2
        with timeit() as duration:
            await sleep(t)
        d = duration()
        self.assertGreater(d, t)
        self.assertAlmostEqual(d, t, places=1)
