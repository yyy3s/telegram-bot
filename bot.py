from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-dev-shm-usage",
            "--no-sandbox"
        ]
    )

    page = browser.new_page()

    def log_request(request):

        url = request.url

        if (
            "api" in url.lower()
            or "price" in url.lower()
            or "market" in url.lower()
            or "exchange" in url.lower()
            or "dollar" in url.lower()
        ):

            print(url)

    page.on(
        "request",
        log_request
    )

    page.goto(
        "https://dollar-iraq.com",
        wait_until="domcontentloaded"
    )

    page.wait_for_timeout(
        15000
    )

    browser.close()
