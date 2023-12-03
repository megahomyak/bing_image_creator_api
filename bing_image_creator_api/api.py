import asyncio
import urllib.parse
import aiohttp
import re
from typing import List, NewType
import logging
import bs4

class GeolocationBlock(Exception): pass
class PromptBlock(Exception): pass
class UnsafeImageContentDetected(Exception): pass
class ServersAreOverloaded(Exception): pass
class TooManyRequests(Exception):
    """
    You either need to wait until the last generation completes, or you've just been rate limited (the limitations are lifted after a while, don't worry)
    """
class PromptNotDescriptiveEnough(Exception): pass
class TemporaryBackendError(Exception): pass
class UnexpectedServerResponse(Exception): pass

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
            logging.debug(f"response text for a query: {response_text}")
            # All of these check are possible because of language headers!
            if "Please wait until your other ongoing creations are complete before trying to create again." in response_text:
                raise TooManyRequests()
            if "Image creation is coming soon to your region" in response_text:
                raise GeolocationBlock()
            if "This prompt has been blocked. Our system automatically flagged this prompt" in response_text:
                raise PromptBlock()
            if "Please provide a more descriptive prompt" in response_text:
                raise PromptNotDescriptiveEnough()
            if "Bing isn't avaiable right now, but everything should be back to normal very soon" in response_text:
                raise TemporaryBackendError()
            redirect_location = response.headers["location"]
            request_id = re.search(r"&id=(.+?)(&|$)", redirect_location).group(1)
            polling_url = f"https://www.bing.com/images/create/async/results/{request_id}?q={encoded_prompt}"
            while True:
                async with http_client.get(polling_url) as response:
                    response_text = await response.text()
                    if "Bing isn't avaiable right now, but everything should be back to normal very soon" in response_text:
                        raise TemporaryBackendError()
                    if response_text:
                        logging.debug(f"response text for a generation result: {response_text}")
                        image_links = re.findall(r'src="(.+?)"', response_text)
                        if not image_links:
                            # We were given an error JSON
                            continue
                        error_element = bs4.BeautifulSoup(response_text, "html.parser").find(attrs={"id": "girer"})
                        if error_element is not None:
                            if "Unsafe image content detected" in str(error_element):
                                raise UnsafeImageContentDetected()
                            elif "Due to high demand, we're unable to process new requests. Please try again later" in str(error_element):
                                raise ServersAreOverloaded()
                            raise UnexpectedServerResponse()
                        processed_links = []
                        for link in image_links:
                            link = link.split("?", 1)[0] # Removing the image size parameters
                            if not link.endswith(".svg"):
                                processed_links.append(link)
                        return ImageLinks(processed_links)
                    await asyncio.sleep(1)
