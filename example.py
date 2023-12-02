import bing_image_creator_api
import asyncio
import webbrowser
from getpass import getpass

async def main():
    client = bing_image_creator_api.Client(user_token=getpass("Enter your user token: "))
    urls = await client.create("cute puppies")
    for url in urls:
        webbrowser.open(url)

asyncio.run(main())
