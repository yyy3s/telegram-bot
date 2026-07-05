import requests
import cloudscraper
from bs4 import BeautifulSoup

try:

    scraper = cloudscraper.create_scraper()

    response = scraper.get(
        "https://dollar-iraq.com/",
        timeout=20
    )

    print("\n========== Status ==========")
    print(response.status_code)

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    text = soup.get_text(
        separator="\n"
    )

    text = text.translate(
        str.maketrans(
            "٠١٢٣٤٥٦٧٨٩",
            "0123456789"
        )
    )

    print("\n========== النص المستخرج ==========\n")
    print(text[:10000])

except Exception as e:

    print("\n========== خطأ ==========")
    print(e)
