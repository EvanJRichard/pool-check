import asyncio
from coins import encode, decode, save_work
import time

MAX_RETRIES = 10  # maximum number of reconnection attempts

async def connect(pool, retries=0):
    host, port = pool.split(':')
    writer = None
    try:
        reader, writer = await asyncio.open_connection(host, port)
        writer.write(encode(
            {"id": 0, "method": "mining.subscribe",
             "body": {"version": 2, "agent": "Rigel/1.4.1", "name": "wrk",
                      "publicAddress": "719e1a617a96353049f82c953938d3ca6d9e89f7ea8e88308b7ec5a3aea8cee8"}}))
        while True:
            try:
                data = await reader.readline()
            except Exception as ex:
                print(f'{pool}\t{ex}')
                break

            received_at = round(time.time() * 1000)
            msg = decode(data)
            if not msg:
                break

            method = msg.get('method')

            if method != 'mining.notify':
                continue

            height = int.from_bytes(bytes.fromhex(msg['body']['header'][16:24]), 'little')
            asyncio.create_task(save_work('iron', pool, height, received_at, 60))
    except Exception as ex:
        print(f'{pool}\t{ex}')
        if retries < MAX_RETRIES:
            await asyncio.sleep(1)  # wait for a while before retrying
            await connect(pool, retries + 1)
        else:
            print(f"Failed to connect to {pool} after {MAX_RETRIES} attempts")
    finally:
        try: 
            if writer:
                writer.close()  # ensure to close the writer
                await writer.wait_closed()  # wait for the writer to close
        except ConnectionResetError as ex:
            pass # if connection is reset, it's already closed
    print(f'Reconnecting to {pool}')
    await connect(pool)