import asyncio
import urllib.parse
import aiohttp
import re
from typing import List, NewType

class GeolocationBlock(Exception): pass
class PromptBlock(Exception): pass
class UnsafeImageContentDetected(Exception): pass
class ServersAreOverloaded(Exception): pass
class TooManyRequests(Exception):
    """
    You either need to wait until the last generation completes, or you've just been rate limited (the limitations are lifted after a while, don't worry)
    """

ImageLinks = NewType("ImageLinks", List[str])

def _filter_image_links(image_links) -> ImageLinks:
    filtered_links = []
    for link in image_links:
        if link == "/rp/TX9QuO3WzcCJz1uaaSwQAz39Kb0.jpg":
            raise ServersAreOverloaded()
        if link == "/rp/in-2zU3AJUdkgFe7ZKv19yPBHVs.png":
            raise UnsafeImageContentDetected()
        if not link.endswith(".svg"):
            filtered_links.append(link)
    return ImageLinks(filtered_links)

class Client:
    def __init__(self, user_token: str):
        self._http_client = aiohttp.ClientSession(
            cookies={"_U": user_token},
            headers={"Accept-Language": "en-US,en;q=0.5"},
        )

    async def create(self, prompt: str) -> ImageLinks:
        encoded_prompt = urllib.parse.quote(prompt)
        result = await self._http_client.post(
            f"https://www.bing.com/images/create?q={encoded_prompt}&rt=3",
            allow_redirects=False,
        )
        result_text = await result.text()
        # All of these check are possible because of language headers!
        if "Please wait until your other ongoing creations are complete before trying to create again." in result_text:
            raise TooManyRequests()
        if "Image creation is coming soon to your region" in result_text:
            raise GeolocationBlock()
        if "This prompt has been blocked. Our system automatically flagged this prompt" in result_text:
            raise PromptBlock()
        redirect_location = result.headers["location"]
        request_id = re.search(r"&id=(.+?)(&|$)", redirect_location).group(1)
        polling_url = f"https://www.bing.com/images/create/async/results/{request_id}?q={encoded_prompt}"
        while True:
            response = await self._http_client.get(polling_url)
            response_text = await response.text()
            if response_text:
                image_links = re.findall(r'src="(.+?)"', response_text)
                return _filter_image_links(image_links)
            await asyncio.sleep(1)
