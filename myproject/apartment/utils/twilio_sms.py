import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()  # Cần dòng này để load .env nếu không dùng trong settings.py

def send_sms(to, message):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")

    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            body=message,
            from_=from_number,
            to=to
        )
        return message.sid
    except Exception as e:
        print("❌ Gửi SMS thất bại:", str(e))
        return None
