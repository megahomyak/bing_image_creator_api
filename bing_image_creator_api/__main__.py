from argparse import ArgumentParser
import asyncio
import logging
import urllib.parse
import aiohttp

from bing_image_creator_api.api import TemporaryBackendError, TooManyRequests

from . import UnsafeImageContentDetected, create
import traceback

parser = ArgumentParser()
parser.add_argument("-t", "--token-file", required=True)
parser.add_argument("-p", "--prompt", required=True)
parser.add_argument("-n", "--minimum-generations-amount", type=int)
parser.add_argument("-l", "--log-level", default="WARNING")

args = parser.parse_args()

logging.basicConfig(level=args.log_level.upper())

with open(args.token_file, encoding="utf-8") as f:
    lines = f.read().splitlines()

tokens = list(filter(lambda s: s and not s.startswith("#"), lines))
generations_amount = 0

async def create_and_save(token: str):
    global generations_amount
    async with aiohttp.ClientSession() as http_client:
        try:
            urls = await create(token, args.prompt)
        except UnsafeImageContentDetected:
            pass
        else:
            generations_amount += len(urls)
            for url in urls:
                while True:
                    async with http_client.get(url) as response:
                        if response.headers["Content-Type"].startswith("image"):
                            # This is an error page
                            continue
                        image_bytes = await response.read()
                        image_name = urllib.parse.urlparse(url).path.rsplit("/", 1)[1]
                        file_name = f"{image_name}.jpeg"
                        with open(file_name, "wb") as f:
                            f.write(image_bytes)
                        break

async def loop(token: str, token_number: int):
    try:
        while True:
            if args.minimum_generations_amount and args.minimum_generations_amount <= generations_amount:
                break
            try:
                await create_and_save(token)
            except TemporaryBackendError:
                pass
    except Exception:
        print(f"Account number {token_number} (...{token[-6:]}) is giving up:")
        traceback.print_exc()

async def main():
    token_index = 0
    while True:
        token = tokens[token_index]
        try:
            await create_and_save(token)
        except TemporaryBackendError:
            pass
        except TooManyRequests:
            token_index += 1
        else:
            break
    await asyncio.gather(*(
        loop(token, token_number)
        for token_number, token in enumerate(tokens)
    ))

asyncio.run(main())
