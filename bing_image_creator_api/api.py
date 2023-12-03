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

async def create(user_token: str, prompt: str) -> ImageLinks:
    async with aiohttp.ClientSession(
            cookies={"_U": user_token},
            headers={"Accept-Language": "en-US,en;q=0.5"},
    ) as http_client:
        encoded_prompt = urllib.parse.quote(prompt)
        async with http_client.post(
                f"https://www.bing.com/images/create?q={encoded_prompt}&rt=3",
                allow_redirects=False,
        ) as response:
            response_text = await response.text()
            # All of these check are possible because of language headers!
            if "Please wait until your other ongoing creations are complete before trying to create again." in response_text:
                raise TooManyRequests()
            if "Image creation is coming soon to your region" in response_text:
                raise GeolocationBlock()
            if "This prompt has been blocked. Our system automatically flagged this prompt" in response_text:
                raise PromptBlock()
            redirect_location = response.headers["location"]
            request_id = re.search(r"&id=(.+?)(&|$)", redirect_location).group(1)
            polling_url = f"https://www.bing.com/images/create/async/results/{request_id}?q={encoded_prompt}"
            while True:
                async with http_client.get(polling_url) as response:
                    response_text = await response.text()
                    if response_text:
                        image_links = re.findall(r'src="(.+?)"', response_text)
                        processed_links = []
                        for link in image_links:
                            link = link.split("?", 1)[0] # Removing the image size parameters
                            if link == "/rp/TX9QuO3WzcCJz1uaaSwQAz39Kb0.jpg":
                                raise ServersAreOverloaded()
                            if link == "/rp/in-2zU3AJUdkgFe7ZKv19yPBHVs.png":
                                raise UnsafeImageContentDetected()
                            if not link.endswith(".svg"):
                                processed_links.append(link)
                        return ImageLinks(processed_links)
                    await asyncio.sleep(1)
