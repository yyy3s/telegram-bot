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

        url = request.url.lower()

        keywords = [
            "api",
            "price",
            "market",
            "exchange",
            "gold",
            "currency",
            "rate",
            "kifah",
            "json"
        ]

        if any(x in url for x in keywords):

            print("\n", request.url)

    page.on(
        "request",
        log_request
    )

    page.goto(
        "https://iraqprices.com",
        wait_until="domcontentloaded",
        timeout=30000
    )

    page.wait_for_timeout(
        15000
    )

    browser.close()
