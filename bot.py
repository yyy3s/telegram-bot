import os
import re
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")


def get_real_price():

    try:

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )

            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0 Safari/537.36",
                viewport={
                    "width":1366,
                    "height":768
                },
                locale="ar-IQ"
            )

            page = context.new_page()

            # إخفاء علامات الأتمتة
            page.add_init_script("""
            Object.defineProperty(navigator,'webdriver',{
                get:()=>undefined
            });
            """)

            page.goto(
                "https://iraqprices.com",
                wait_until="domcontentloaded",
                timeout=30000
            )

            page.wait_for_timeout(8000)

            text = page.locator("body").inner_text()

            browser.close()

            print(text[:5000])

            if "security verification" in text.lower():
                print("Cloudflare ما زال حاجب الصفحة")
                return None,None,None

            match = re.search(
                r'100\$\s*موازي.*?(\d{6})',
                text,
                re.DOTALL
            )

            if not match:
                return None,None,None

            price100 = int(match.group(1))
            price = price100 // 100

            print("100$ =",price100)
            print("1$ =",price)

            return price,price,"IraqPrices"

    except Exception as e:
        print(e)

    return None,None,None


def send_message(message):

    response=requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id":CHANNEL_ID,
            "text":message,
            "parse_mode":"Markdown"
        }
    )

    return response.status_code==200


if __name__=="__main__":

    sell,buy,source=get_real_price()

    if sell:

        message=(
            f"💵 *تحديث سعر الدولار الآن*\n\n"
            f"📍¦ *بورصة الكفاح*\n"
            f"🔻¦ {sell:,} دينار ➜ {sell*100:,}"
        )

        send_message(message)
