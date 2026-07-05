import os
import re
import time
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")


# ================= جلب السعر الحقيقي =================
def get_real_price():

    try:

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True
            )

            page = browser.new_page()

            page.goto(
                "https://iraqprices.com",
                wait_until="networkidle",
                timeout=60000
            )

            # انتظار تحميل الأرقام
            page.wait_for_timeout(
                5000
            )

            text = page.locator(
                "body"
            ).inner_text()

            browser.close()

            print("\n========== النص ==========")
            print(text[:3000])

            # سعر 100$ موازي الكفاح
            match = re.search(
                r'100\$\s*موازي\s*\(الكفاح\)\s*([\d,]+)',
                text
            )

            if not match:

                print(
                    "لم يتم العثور على السعر"
                )

                return None,None,None

            price100 = int(
                match.group(1)
                .replace(",","")
            )

            price = price100 // 100

            print(
                f"100$ = {price100}"
            )

            print(
                f"1$ = {price}"
            )

            return price,price,"IraqPrices"

    except Exception as e:

        print(e)

    return None,None,None


# ================= إرسال =================
def send_message(message):

    try:

        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHANNEL_ID,
                "text": message,
                "parse_mode": "Markdown"
            }
        )

        print(response.status_code)

        return response.status_code==200

    except Exception as e:

        print(e)

        return False


# ================= تشغيل =================
if __name__=="__main__":

    sell,buy,source=get_real_price()

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

        if sell!=last_price:

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
