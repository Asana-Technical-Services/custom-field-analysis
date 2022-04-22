import requests
import json
import asyncio


async def asana_client(method, url, token, **kwargs):

    base_url = "https://app.asana.com/api/1.0"

    backoff_seconds = 0.200
    retryError = 429
    attempt = 0

    full_url = base_url + url

    if "data" in kwargs:
        data = json.dumps(kwargs["data"])
    else:
        data = {}

    if "params" in kwargs:
        params = kwargs["params"]
    else:
        params = {}

    headers = {"Authorization": "Bearer " + token}
    result = False
    while ((retryError == 429) or (retryError == 500)) and (attempt < 10):
        # pause execution before trying again

        if attempt == 6:
            print("hitting rate limits. slowing down calls...")

        if attempt == 8:
            print("thanks for your patience. still slow.")

        try:
            response = requests.request(
                method, url=full_url, headers=headers, data=data, params=params
            )
            retryError = response.status_code
            response.raise_for_status()
            response_content = response.json()
            result = (
                response_content["data"]
                if "data" in response_content
                else response_content
            )

        except requests.exceptions.RequestException as e:
            print(e)
            if (response.status_code != 429) and (response.status_code != 500):
                print(response.json())
                print("HTTP Error: ", response.status_code)
                return False

        # Exponential backoff = const * attempt^2
        await asyncio.sleep(backoff_seconds * attempt * attempt)
        attempt += 1

    if attempt >= 6:
        print("too many requests hit rate limits - timed out")

    return result
