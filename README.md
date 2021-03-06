# Python 3 library for [libbitcoin-server](https://github.com/libbitcoin/libbitcoin-server)

## Installation

```sh
$ pip3 install python-libbitcoin
```

## Examples

```sh
$ git clone https://github.com/RojavaCrypto/python-libbitcoin.git
$ cd python-libbitcoin/examples/
$ python3 fetch_last_height.py
```

Tornado integration also exists. See ```examples/web_app.py```

## Basic Usage

```sh
$ python3
>>> import libbitcoin
>>> context = libbitcoin.Context()
```

This library uses Python3 asyncio and pyzmq. It interfaces with a libbitcoin
server.

See the examples/ directory for more examples.

Here's an example of querying the last blockheight.

```py
import sys
import zmq.asyncio
import asyncio

loop = zmq.asyncio.ZMQEventLoop()
asyncio.set_event_loop(loop)

import libbitcoin
context = libbitcoin.Context()

async def main():
    # The settings parameter is optional.
    # Use help(client_settings) to see more options.
    client_settings = libbitcoin.ClientSettings()
    client_settings.query_expire_time = None

    client = context.Client("tcp://gateway.unsystem.net:9091",
                            settings=client_settings)

    ec, height = await client.last_height()
    if ec:
        print("Couldn't fetch last_height:", ec, file=sys.stderr)
        context.stop_all()
        return
    print("Last height:", height)

    context.stop_all()

if __name__ == '__main__':
    tasks = [
        main(),
    ]
    tasks.extend(context.tasks())
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
```

## API Reference

To keep the examples short, we're not handling ErrorCodes here.
See ```help(libbitcoin.ErrorCode)``` for a full list of possible values.
When a query times out, it will return ```ErrorCode.channel_timeout```.

### Block header

Fetches the block header by height or integer index.

```py
import binascii
# ...
idx = bytes.fromhex(
    "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f")
ec, header = await client.block_header(idx)
print("Header:", binascii.hexlify(header))
```

```
$ python3 fetch_block_header.py
Header: b'0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c'
```

### History for an address (outputs and spend inputs)

Fetches history for an address. Returns an error code,
and a list of rows consisting of outputs and corresponding
spend inputs.

Outputs are a tuple of:

```
OutPoint(hash, index)
block height
value
```

Spends are either None (if unspent) or:

```
InPoint(hash, index)
block height
```

These values form a tuple for each row in the history.

```py
address = "13ejSKUxLT9yByyr1bsLNseLbx9H9tNj2d"
ec, history = await client.history(address)
for output, spend in history:
    print("OUTPUT point=%s, height=%s, value=%s" %
          (output[0], output[1], output[2]))
    if spend is not None:
        print("-> SPEND point=%s, height=%s" %
              (spend[0], spend[1]))
    print()
# Calculate the balance of a Bitcoin address from its history.
balance = sum(output[2] for output, spend in history if spend is None)
print("Address balance:", balance)
```

```
$ python3 fetch_history.py
OUTPUT point=OutPoint(hash=54dc90aa618ea1c300aac021399c66f5f5152848a57984a757075036e3046147, index=1), height=200000, value=127000000
-> SPEND point=InPoint(hash=1431117a24f80fdc7771cef77722473f8fe528d12f8202659e1c0081adac0441, index=2), height=200009

OUTPUT point=OutPoint(hash=2502852f77bd63d0ef71a5a854a91d35b7bec3450baeee268cca1511b51e3416, index=1), height=199919, value=69000000
-> SPEND point=InPoint(hash=fd6ce207e5b540e8a74b2dd0571235cbc4a64e711aa8b1749f53190d24f3fa88, index=1), height=199928

OUTPUT point=OutPoint(hash=34238a653e66651f5484edd06c8eef68b4245d98227c6b7eb00b0221225f9c1d, index=1), height=198327, value=411000000
-> SPEND point=InPoint(hash=d96be857d22065994c2f5f1497405f3022044a98db5da5e30e80c56061765a52, index=5), height=198334

OUTPUT point=OutPoint(hash=0d7efb76a574d71685b89d45d3badf99ad965668a1105b22b6ee9dd3c7473d2a, index=0), height=184531, value=500000
-> SPEND point=InPoint(hash=0d8e104d1a839025846105e7e22cf503c5c1e92648504411b766a0a466df65b5, index=5), height=184555

Address balance: 0
```

If the spend is None, then the output is unspent.

### Height of the last block

Fetches the height of the last block in our blockchain.

```py
ec, height = await client.last_height()
print("Last height:", height)
```

```
$ python3 fetch_last_height.py
Last height: 425156
```

### Transaction

Fetches a transaction by hash from the blockchain.

```py
idx = "77cb1e9d44f1b8e8341e6e6848bf34ea6cb7a88bdaad0126ac1254093480f13f"
idx = bytes.fromhex(idx)
ec, tx_data = await client.transaction(idx)
# Should be 257 bytes.
print("tx size is %s bytes" % len(tx_data))
```

```
$ python3 fetch_transaction.py
tx size is 257 bytes
```

### Transaction (from the transaction pool)

Fetches a transaction the transaction pool (also known as the memory pool).

```py
idx = "77cb1e9d44f1b8e8341e6e6848bf34ea6cb7a88bdaad0126ac1254093480f13f"
idx = bytes.fromhex(idx)
ec, tx_data = await client.transaction_from_pool(idx)
# Should be 257 bytes.
print("tx size is %s bytes" % len(tx_data))
```

```
$ python3 fetch_transaction.py
tx size is 257 bytes
```

### Spend for an output point.

Fetches a corresponding spend of an output.

```py
outpoint = libbitcoin.OutPoint()
outpoint.hash = bytes.fromhex(
	"0530375a5bf4ea9a82494fcb5ef4a61076c2af807982076fa810851f4bc31c09")
outpoint.index = 0

ec, spend = await client.spend(outpoint)

check_spend = libbitcoin.InPoint()
check_spend.hash = bytes.fromhex(
	"e03a9a4b5c557f6ee3400a29ff1475d1df73e9cddb48c2391abdc391d8c1504a")
check_spend.index = 0
if spend != check_spend:
	print("Incorrect spend value supplied by server.")
	context.stop_all()
	return

print(spend)
```

```
$ python3 fetch_spend.py 
InPoint(hash=e03a9a4b5c557f6ee3400a29ff1475d1df73e9cddb48c2391abdc391d8c1504a, index=0)
```

### Transaction index for a transaction hash

Fetch the block height that contains a transaction and its index
within that block.

```py
idx = "77cb1e9d44f1b8e8341e6e6848bf34ea6cb7a88bdaad0126ac1254093480f13f"
idx = bytes.fromhex(idx)
ec, height, index = await client.transaction_index(idx)
# 210000 4
print(height, index)
```

```
$ python3 fetch_transaction.py
210000 4
```

### Block transaction hashes

Fetches list of transaction hashes in a block by block hash.

```py
idx = "000000000000048b95347e83192f69cf0366076336c639f9b7228e9ba171342e"
idx = bytes.fromhex(idx)

ec, hashes = await client.block_transaction_hashes(idx)
for hash in hashes:
	print(binascii.hexlify(hash))
```

```
$ python3 fetch_block_transaction_hashes.py 
b'76a30f7eefb41cd01733b23218faea8a1a1a2f6bbf1a2c11e4bc77f62c8e7ce9'
b'12fb554e126757eb61bd7eee6561529ff341dbba1034f0b22ef46a050033c61c'
b'6f37c134ce41f688f0b4f2b18286228f28c2c537750c24ce253681893dcfd18e'
b'415b5c238ca9c0e386d12f4c4c411e0e2d71e1777070b80e34f6c8bb7dd28312'
b'77cb1e9d44f1b8e8341e6e6848bf34ea6cb7a88bdaad0126ac1254093480f13f'
...
```

### Block height

Fetches the height of a block given its hash.

```py
idx = "000000000000048b95347e83192f69cf0366076336c639f9b7228e9ba171342e"
idx = bytes.fromhex(idx)

ec, height = await client.block_height(idx)
# Should be 210000
print("Block's height is", height)
```

```
$ python3 fetch_block_height.py
Block's height is 210000
```

### Stealth

Fetch possible stealth results. These results can then be iterated
to discover new payments belonging to a particular stealth address.
This is for recipient privacy.

The prefix is a special value that can be adjusted to provide
greater precision at the expense of deniability.

from_height is not guaranteed to only return results from that
height, and may also include results from earlier blocks.
It is provided as an optimisation. All results at and after
from_height are guaranteed to be returned however.

```py
prefix = libbitcoin.Binary.from_string("")
ec, rows = await client.stealth(prefix, 419135)
print("Fetched %s rows." % len(rows))
```

```
$ python3 fetch_stealth.py
Fetched 23036 rows.
```

### Total server connections

Fetches the total number of server connections.

```py
ec, total_connections = await client.total_connections()
print("Total server connections:", total_connections)
```

```
$ python3 fetch_total_connections.py
Total server connections: 11
```

### Broadcast transaction data

Broadcasts a transaction to the network.

```py
raw_tx_data = b"..."
ec = await client.broadcast(raw_tx_data)
```

### Subscribe to an address

Subscribe to address updates. Client is notified of all new transactions containing
a specific address or address prefix.

```py
# To subscribe to a specific address, then use:
#   address = "15s5nojkHKxJz3GvpKD1S6DR9nKUxSzNko"
#   prefix = libbitcoin.Binary.from_address(address)
prefix = libbitcoin.Binary.from_string("11")
ec, subscription = await client.subscribe_address(prefix)
if ec:
	print("Couldn't subscribe:", ec, file=sys.stderr)
	context.stop_all()
	return

#print("Watching address: %s..." % address)
print("prefix=%s" % prefix)

# Stop after 1 minute.
loop.call_later(60, lambda: loop.create_task(subscription.stop()))

with subscription:
	while subscription.is_running():
		update = await subscription.updates()
		print("Received update:")
		if update.confirmed:
			print("Block #%s %s" % (update.height,
									hash_str(update.block_hash)))
		tx_hash = libbitcoin.bitcoin_utils.bitcoin_hash(update.tx_data)
		print("Transaction:", hash_str(tx_hash))
```


