import requests
import json

try:

    response = requests.get(
        "https://market-rate.m-tbeshe.workers.dev/",
        timeout=20
    )

    print("Status:", response.status_code)

    print("\n========== الناتج ==========\n")

    try:
        data = response.json()

        print(
            json.dumps(
                data,
                indent=4,
                ensure_ascii=False
            )
        )

    except:
        print(response.text)

except Exception as e:

    print(e)
