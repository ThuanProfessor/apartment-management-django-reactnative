
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()  # Đảm bảo biến môi trường được nạp

def send_sms(to, message):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")

    if not all([account_sid, auth_token, from_number]):
        print("❌ Thiếu cấu hình Twilio. Vui lòng kiểm tra biến môi trường.")
        return None

    client = Client(account_sid, auth_token)

    try:
        sms = client.messages.create(
            body=message,
            from_=from_number,
            to=to
        )
        print(f"✅ Gửi SMS thành công: SID = {sms.sid}")
        return sms.sid
    except Exception as e:
        print("❌ Gửi SMS thất bại:", str(e))
        return None
