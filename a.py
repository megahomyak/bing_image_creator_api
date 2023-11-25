user_token = open("user_token.txt").read().strip() # personal token

import requests
import urllib.parse
import re
import time
import webbrowser

AUTH_COOKIES = {"_U": user_token}

prompt = "cute puppies"
encoded_prompt = urllib.parse.quote(prompt)
result = requests.post(f"https://www.bing.com/images/create?q={encoded_prompt}&rt=3", cookies=AUTH_COOKIES, allow_redirects=False)
try:
    redirect_location = result.headers["location"]
except KeyError:
    raise Exception("prompt block")
request_id = re.search(r"&id=(.+?)(&|$)", redirect_location).group(1)
polling_url = f"https://www.bing.com/images/create/async/results/{request_id}?q={encoded_prompt}"

retries_amt = 1

while True:
    response = requests.get(polling_url, cookies=AUTH_COOKIES)
    if response.text:
        image_links = re.findall(r'src="(.+?)"', response.text)
        print(image_links)
        for link in image_links:
            if link == "/rp/TX9QuO3WzcCJz1uaaSwQAz39Kb0.jpg":
                raise Exception("servers are overloaded")
            elif link == "/rp/in-2zU3AJUdkgFe7ZKv19yPBHVs.png":
                raise Exception("image block")
        for link in image_links:
            webbrowser.open(link)
        exit(0)
    time.sleep(1)
    if retries_amt == 10:
        raise Exception("too many retries")
    retries_amt += 1
