import os
import re
import time
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")


# ================= جلب السعر =================
def get_real_price():

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
                "https://iraqprices.com",
                wait_until="domcontentloaded",
                timeout=30000
            )

            prices = []

            # راقب الصفحة 10 ثواني
            for i in range(10):

                text = page.locator(
                    "body"
                ).inner_text()

                matches = re.findall(
                    r'موازي.*?(\d{6})',
                    text,
                    re.DOTALL
                )

                if matches:

                    try:

                        current = int(
                            matches[-1]
                            .replace(",", "")
                        )

                        prices.append(current)

                        print(
                            f"قراءة {i+1}: {current}"
                        )

                    except:
                        pass

                time.sleep(1)

            browser.close()

            if not prices:

                print(
                    "ما لكيت أسعار"
                )

                return None,None,None

            # خذ آخر قراءة
            price100 = prices[-1]

            price = price100 // 100

            print(
                f"100$ = {price100}"
            )

            print(
                f"1$ = {price}"
            )

            return price,price,"IraqPrices"

    except Exception as e:

        print(
            f"خطأ: {e}"
        )

    return None,None,None


# ================= إرسال =================
def send_message(message):

    try:

        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHANNEL_ID,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
        )

        return response.status_code == 200

    except Exception as e:

        print(e)
        return False


# ================= تشغيل =================
if __name__=="__main__":

    sell,buy,source = get_real_price()

    if sell:

        last_price=None

        if os.path.exists(
            "last_price.txt"
        ):

            with open(
                "last_price.txt",
                "r"
            ) as f:

                try:

                    last_price=int(
                        f.read().strip()
                    )

                except:
                    pass

        print(
            f"الحالي: {sell}"
        )

        print(
            f"المحفوظ: {last_price}"
        )

        if sell != last_price:

            message=(
                f"💵 *تحديث سعر الدولار الآن*\n\n"
                f"📍¦ *بورصة الكفاح*\n"
                f"🔻¦ {sell:,} دينار ➜ {sell*100:,}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"https://t.me/DollarNowIQ"
            )

            if send_message(
                message
            ):

                with open(
                    "last_price.txt",
                    "w"
                ) as f:

                    f.write(
                        str(sell)
                    )

                print(
                    "تم النشر"
                )

        else:

            print(
                "السعر لم يتغير"
            )
