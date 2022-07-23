import asyncio

async def printer(name:str, times:int)-> None:
    for i in range(times):
        print(name)
        await asyncio.sleep(1)

async def main():
    await asyncio.gather(
        printer("A",5),
        printer("B",2),
    )

asyncio.run(main())