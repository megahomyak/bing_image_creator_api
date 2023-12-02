# bing\_image\_creator\_api

This repository was created using the code from these repositories:
* https://github.com/nociza/Bimg
* https://github.com/acheong08/BingImageCreator

I am very thankful to the creators of these repos, they did an amazing job. I simplified the algorithm a lot and added a better (in my opinion) way to invoke the tool programmatically.

## What's not currently supported

Using boosts for generations

## Installation

`pip install bing_image_creator_api`

## Usage

### As a library

```python
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
```

### As a standalone program

The "token file" is a file containing tokens from one or more accounts, where each token is placed on a separate line. This file can have comments that start with "#"

```bash
python -m bing_image_creator_api -t '/path/to/token/file.txt' -n 10 -p "cute puppies" # Generate at least 10 images and then stop
python -m bing_image_creator_api -t '/path/to/token/file.txt' -p "cute puppies" # Generate images until killed (Ctrl+C)
```
