from django.core.management.base import BaseCommand
from django.utils import timezone
from apartment.models import User, Bill
from datetime import timedelta


class Command(BaseCommand):
    help = 'Tự động tạo các hóa đơn hàng tháng cho cư dân (quản lý, dịch vụ, gửi xe nếu có)'

    def add_arguments(self, parser):
        parser.add_argument('--management-fee', type=int, default=500000)
        parser.add_argument('--service-fee', type=int, default=200000)
        parser.add_argument('--parking-fee', type=int, default=300000)

    def handle(self, *args, **options):
        today = timezone.now()
        due_date = today + timedelta(days=30)
        residents = User.objects.filter(role='RESIDENT', apartment__isnull=False)
        created_bills = []

        for resident in residents:
            month_str = today.strftime("%m/%Y")

            # Phí quản lý
            desc_mgmt = f'Phí quản lý tháng {month_str}'
            if not Bill.objects.filter(user=resident, bill_type='management_fee', description=desc_mgmt).exists():
                created_bills.append(Bill(
                    user=resident,
                    bill_type='management_fee',
                    amount=options['management_fee'],
                    description=desc_mgmt,
                    payment_method='momo_tranfer',
                    due_date=due_date
                ))

            # Phí dịch vụ
            desc_service = f'Phí dịch vụ khác tháng {month_str}'
            if not Bill.objects.filter(user=resident, bill_type='service_fee', description=desc_service).exists():
                created_bills.append(Bill(
                    user=resident,
                    bill_type='service_fee',
                    amount=options['service_fee'],
                    description=desc_service,
                    payment_method='momo_tranfer',
                    due_date=due_date
                ))

            # Phí gửi xe - chỉ nếu có thẻ ParkingCard
            if resident.parking_card.exists():
                desc_parking = f'Phí gửi xe tháng {month_str}'
                if not Bill.objects.filter(user=resident, bill_type='parking_fee', description=desc_parking).exists():
                    created_bills.append(Bill(
                        user=resident,
                        bill_type='parking_fee',
                        amount=options['parking_fee'],
                        description=desc_parking,
                        payment_method='momo_tranfer',
                        due_date=due_date
                    ))

        Bill.objects.bulk_create(created_bills)
        self.stdout.write(self.style.SUCCESS(f'✅ Đã tạo {len(created_bills)} hóa đơn hàng tháng.'))
