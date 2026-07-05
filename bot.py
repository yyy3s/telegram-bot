import requests
import json

try:

    response = requests.get(
        "https://prices-api.alawe6663.workers.dev/prices",
        timeout=20
    )

    print("Status:", response.status_code)

    data = response.json()

    print(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        )
    )

except Exception as e:

    print(e)
