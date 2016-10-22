import sys
import zmq.asyncio
import asyncio

loop = zmq.asyncio.ZMQEventLoop()
asyncio.set_event_loop(loop)

import libbitcoin.server
context = libbitcoin.server.Context()

tor_enabled = False

async def main():
    if tor_enabled:
        url = "tcp://55k4e2eaeucf3omt.onion:9091"
    else:
        url = "tcp://gateway.unsystem.net:9091"
        # Testnet URL
        url = "tcp://5.135.30.59:9091"

    client_settings = libbitcoin.server.ClientSettings()
    client_settings.query_expire_time = None
    if tor_enabled:
        client_settings.socks5 = "127.0.0.1:9150"

    client = context.Client(url, settings=client_settings)

    ec, height = await client.last_height()
    if ec:
        print("Couldn't fetch last_height:", ec, file=sys.stderr)
        context.stop_all()
        return
    print("Last height:", height)

    ec, total_connections = await client.total_connections()
    if ec:
        print("Couldn't fetch total_connections:", ec, file=sys.stderr)
        context.stop_all()
        return
    print("Total server connections:", total_connections)

    context.stop_all()

if __name__ == '__main__':
    tasks = [
        main(),
    ]
    tasks.extend(context.tasks())
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

