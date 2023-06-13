from collections import defaultdict, deque
import pathlib
import subprocess
import aiofiles

history = defaultdict(dict)  # height -> pool -> timestamp
best = {}  # height -> timestamp
moving_avg = defaultdict(lambda: deque(maxlen=10))  # pool -> deque of last 10 measurements

async def save_work(coin, pool, height, timestamp, block_time):
    if height not in history:
        best[height] = timestamp
    if pool in history[height]:
        return
    history[height][pool] = timestamp
    diff_ms = timestamp - best[height]
    moving_avg[pool].append(diff_ms)  # add to the deque of measurements
    avg_diff_ms = sum(moving_avg[pool]) / len(moving_avg[pool])  # calculate the moving average
    block_time_ms = block_time * 1000
    block_time_pct = 100 * avg_diff_ms / block_time_ms  # calculate percentage with moving average
    influx_cmd = f"influx write -b ironfish-mining-mainnet \"{height},pool={pool} timestamp={timestamp}i,diff_from_best={diff_ms}i,avg_diff_from_best={avg_diff_ms}i\""
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