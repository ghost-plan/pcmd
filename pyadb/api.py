import asyncio
import time


async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)


async def main():
    # 1
    # print(f"started at {time.strftime('%X')}")

    # await say_after(3, 'hello')
    # await say_after(1, 'world')

    # print(f"finished at {time.strftime('%X')}")

    # # 2
    # task1 = asyncio.create_task(
    #     say_after(3, 'hello'))

    # task2 = asyncio.create_task(
    #     say_after(1, 'world'))

    # print(f"started at {time.strftime('%X')}")

    # # Wait until both tasks are completed (should take
    # # around 2 seconds.)
    # await task1
    # await task2

    # print(f"finished at {time.strftime('%X')}")

    async def handle(index):
        if index == 2:
            await asyncio.sleep(2)
        print('index '+str(index))
        # while True:
        # print('index '+str(index))
        # asyncio.sleep(index)
    for i in range(1, 7):
        asyncio.create_task(handle(i))
    print('cjf')

    # asyncio.run(main())
asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()
