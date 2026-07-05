from playwright.sync_api import sync_playwright

try:

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-dev-shm-usage",
                "--no-sandbox"
            ]
        )

        page = browser.new_page()

        page.goto(
            "https://dollar-iraq.com",
            wait_until="domcontentloaded",
            timeout=30000
        )

        # انتظر حتى يتحدث الموقع
        page.wait_for_timeout(10000)

        text = page.locator(
            "body"
        ).inner_text()

        browser.close()

        print("\n========== النص ==========\n")

        print(text[:10000])

except Exception as e:

    print("\n========== خطأ ==========")
    print(e)
