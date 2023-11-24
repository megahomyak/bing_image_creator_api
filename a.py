user_token = open("user_token.txt").read().strip() # token from p<...>a

import requests
import urllib.parse
import re
import time

prompt = "cute puppies"
encoded_prompt = urllib.parse.quote(prompt)
result = requests.post(f"https://www.bing.com/images/create?q={encoded_prompt}&rt=4&FORM=GENCRE", cookies={"_U": user_token}, allow_redirects=False)#, headers=HEADERS, data=f"q={encoded_prompt}&qs=ds")
redirect_location = result.headers["location"]
print(redirect_location)
request_id = re.search(r"&id=(.+?)(&|$)", redirect_location).group(1)
polling_url = f"https://www.bing.com/images/create/async/results/{request_id}?q={encoded_prompt}"

retries_amt = 1

while True:
    response = requests.get(polling_url)
    if response.text:
        response = response.json()
        print(response)
        if input():
            exit(0)
        continue
        if response["errorMessage"] == "Pending":
            raise Exception("prompt block")
        elif response["errorMessage"]:
            raise Exception(f"weird error: {response['errorMessage']}")
        image_links = re.findall(r'src="(.+?)"', response.text)
        for link in image_links:
            if link == "https://r.bing.com/rp/TX9QuO3WzcCJz1uaaSwQAz39Kb0.jpg":
                raise Exception("badfosh CANNOT GENERATE IMAGES RIGHT NOW")
            elif link == "https://r.bing.com/rp/in-2zU3AJUdkgFe7ZKv19yPBHVs.png":
                raise Exception("image block")
        break # =return image_links
    if retries_amt == 10:
        raise Exception("too many retries")
    retries_amt += 1
    time.sleep(1)

print(image_links)
