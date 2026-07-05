import os
import re
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

            # انتظار ظهور سعر الكفاح
            page.wait_for_function("""
                () => {
                    return document.body.innerText.includes(
                        'سعر 100$ موازي (الكفاح)'
                    )
                }
            """, timeout=15000)

            # انتظار إضافي حتى يتحدث الرقم الحقيقي
            page.wait_for_timeout(3000)

            text = page.locator(
                "body"
            ).inner_text()

            browser.close()

            print("\n========== النص ==========")
            print(text[:3000])

            match = re.search(
                r'سعر\s*100\$\s*موازي\s*\(الكفاح\)\s*([\d,]+)',
                text
            )

            if not match:

                print("لم يتم العثور على السعر")
                return None, None, None

            price100 = int(
                match.group(1)
                .replace(",", "")
            )

            price = price100 // 100

            print("\n========== السعر ==========")
            print(f"100$ = {price100}")
            print(f"1$ = {price}")

            return price, price, "IraqPrices"

    except Exception as e:

        print(f"خطأ: {e}")

    return None, None, None


# ================= إرسال الرسالة =================
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

        print("\n========== نتيجة الإرسال ==========")
        print(response.status_code)
        print(response.text)

        return response.status_code == 200

    except Exception as e:

        print(f"خطأ الإرسال: {e}")

        return False


# ================= التشغيل =================
if __name__ == "__main__":

    sell, buy, source = get_real_price()

    if sell:

        last_price = None

        if os.path.exists("last_price.txt"):

            with open(
                "last_price.txt",
                "r"
            ) as f:

                try:

                    last_price = int(
                        f.read().strip()
                    )

                except:
                    pass

        print("\n========== مقارنة ==========")
        print(f"السعر الحالي: {sell}")
        print(f"السعر المحفوظ: {last_price}")

        if sell == last_price:

            print("السعر لم يتغير")

        else:

            message = (
                f"💵 *تحديث سعر الدولار الآن*\n\n"
                f"📍¦ *بورصة الكفاح*\n"
                f"🔻¦ {sell:,} دينار ➜ {sell*100:,}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"https://t.me/DollarNowIQ"
            )

            success = send_message(
                message
            )

            if success:

                with open(
                    "last_price.txt",
                    "w"
                ) as f:

                    f.write(
                        str(sell)
                    )

                print("تم حفظ السعر الجديد")

    else:

        print("لم يتم العثور على السعر")
