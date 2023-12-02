from argparse import ArgumentParser
import asyncio
import urllib.parse
import aiohttp
from . import Client, UnsafeImageContentDetected
import imghdr
import traceback

parser = ArgumentParser()
parser.add_argument("-t", "--token-file", required=True)
parser.add_argument("-p", "--prompt", required=True)
parser.add_argument("-n", "--minimum-generations-amount", type=int)

args = parser.parse_args()

with open(args.token_file, encoding="utf-8") as f:
    lines = f.read().splitlines()

tokens = filter(lambda s: s and not s.startswith("#"), lines)
clients = [(Client(token), token) for token in tokens]
generations_amount = 0

async def loop(client: Client, client_number: int, token: str):
    global generations_amount
    http_client = aiohttp.ClientSession()
    try:
        while True:
            if args.minimum_generations_amount and args.minimum_generations_amount <= generations_amount:
                break
            try:
                urls = await client.create(args.prompt)
            except UnsafeImageContentDetected:
                pass
            else:
                generations_amount += len(urls)
                for url in urls:
                    file_response = await http_client.get(url)
                    image_name = urllib.parse.urlparse(url).path.rsplit("/", 1)[1]
                    image_bytes = await file_response.read()
                    file_extension = imghdr.what(None, h=image_bytes)
                    file_name = f"{image_name}.{file_extension}"
                    with open(file_name, "wb") as f:
                        f.write(image_bytes)
    except Exception:
        print(f"Client number {client_number} (...{token[-6:]}) is giving up:")
        traceback.print_exc()

async def main():
    first_client, _ = clients[0]
    try:
        await first_client.create(args.prompt)
    except UnsafeImageContentDetected:
        pass
    await asyncio.gather(
        loop(client, client_number, token)
        for client_number, (client, token) in enumerate(clients)
    )

asyncio.run(main())
