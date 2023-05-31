from collections import defaultdict
import pathlib
import subprocess
import aiofiles

history = defaultdict(dict)  # height -> pool -> timestamp
best = {}  # height -> timestamp


async def save_work(coin, pool, height, timestamp, block_time):
    if height not in history:
        best[height] = timestamp
    if pool in history[height]:
        return
    history[height][pool] = timestamp
    diff_ms = timestamp - best[height]
    block_time_ms = block_time * 1000
    block_time_pct = 100 * diff_ms / block_time_ms
    influx_cmd = f"influx write -b ironfish-mining-mainnet \"{height},pool={pool} timestamp={timestamp}i,diff_from_best={diff_ms}i\""
    subprocess.run(influx_cmd, shell=True)
    res_path = pathlib.Path('res').joinpath(f'{coin}.csv')
    async with aiofiles.open(res_path, mode='a') as f:
        await f.write(f'{height},{pool},{timestamp},{diff_ms},{block_time_pct:.2f}%\n')

def encode(data):
    return (json.dumps(data) + '\n').encode('utf-8')


def decode(data):
    try:
        return json.loads(data.decode('utf-8').replace('\n', ''))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
