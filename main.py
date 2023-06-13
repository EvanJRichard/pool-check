import asyncio
import json
import importlib
import pathlib
import sys


async def main():
    coin = sys.argv[1]
    work_location = sys.argv[2]
    config_path = pathlib.Path('config').joinpath(f'{coin}.json')
    config_path = work_location + config_path
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    try:
        module = importlib.import_module(f'coins.{coin}')
    except ModuleNotFoundError:
        print(f'{coin} not supported')
        exit(-1)

    result_path = work_location + pathlib.Path('res')
    pathlib.Path(result_path).mkdir(exist_ok=True)
    connect = getattr(module, 'connect')

    async with asyncio.TaskGroup() as tg:
        for pool in config['pools']:
            tg.create_task(connect(pool))


if __name__ == '__main__':
    asyncio.run(main())
