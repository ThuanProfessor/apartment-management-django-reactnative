from django.db.models.signals import post_save
from django.dispatch import receiver
from apartment.models import Locker
from apartment.utils.sms_helper import send_sms

@receiver(post_save, sender=Locker)
def send_locker_sms(sender, instance, created, **kwargs):
    if created and instance.status == "pending":
        user = instance.user
        phone = user.phone
        if phone:
            if phone.startswith("0"):
                phone = "+84" + phone[1:]
            sms = f"[Chung cư] Bạn có hàng mới trong tủ đồ: {instance.item_description}."

            send_sms(phone, sms)
