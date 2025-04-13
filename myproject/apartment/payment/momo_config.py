import os
from dotenv import load_dotenv

load_dotenv()

MOMO_CONFIG = {
    'PARTNER_CODE': os.getenv('MOMO_PARTNER_CODE', 'MOMOBKUN20180529'),
    'ACCESS_KEY': os.getenv('MOMO_ACCESS_KEY', 'klm05TvNBzhg7h7j'),
    'SECRET_KEY': os.getenv('MOMO_SECRET_KEY', 'at67qH6mk8w5Y1nAyMoYKMWACiEi2bsa'),
    'API_ENDPOINT': os.getenv('MOMO_API_ENDPOINT', 'https://test-payment.momo.vn/v2/gateway/api/create'),
    'RETURN_URL': os.getenv('MOMO_RETURN_URL', 'http://localhost:8000/api/v1/payments/momo/return'),
    'NOTIFY_URL': os.getenv('MOMO_NOTIFY_URL', 'http://localhost:8000/api/v1/payments/momo/notify'),
    'REQUEST_TYPE': 'captureWallet'
} 