from unittest import IsolatedAsyncioTestCase

from ...std2.concurrent.aexecutor import AExecutor
from ...std2.contextlib import aclosing


class AExe(IsolatedAsyncioTestCase):
    async def test_1(self) -> None:
        aexe = AExecutor(daemon=True)
        two = aexe.submit(lambda: 1 + 1)
        await aexe.aclose()
        self.assertEqual(two, 2)

    async def test_2(self) -> None:
        aexe = AExecutor(daemon=False)
        two = await aexe.asubmit(lambda: 1 + 1)
        await aexe.aclose()
        self.assertEqual(two, 2)

    async def test_3(self) -> None:
        aexe = AExecutor(daemon=True)
        two = await aexe.asubmit(lambda: 1 + 1)
        self.assertEqual(two, 2)

    async def test_4(self) -> None:
        aexe = AExecutor(daemon=False)
        two = await aexe.asubmit(lambda: 1 + 1)
        self.assertEqual(two, 2)

    async def test_5(self) -> None:
        async with aclosing(AExecutor(daemon=False)) as aexe:
            two = await aexe.asubmit(lambda: 1 + 1)
            self.assertEqual(two, 2)
