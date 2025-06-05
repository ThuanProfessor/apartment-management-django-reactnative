from urllib import request
from rest_framework import viewsets, status, permissions, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.utils import timezone
import cloudinary.uploader
from apartment.models import Apartment, CardRequest, User, RelativeCard, Bill, ParkingCard, Locker, Feedback, Survey, SurveyResult, PaymentAccount, Notification, ChatMessage, Payment, SurveyFeedback
from apartment import serializers, paginators
from apartment.permissions import IsAdminOrSelf, IsAdminOnly, IsPasswordChanged, IsResidentOnly
import logging
from rest_framework.exceptions import PermissionDenied
from datetime import datetime
from django.conf import settings
from .models import SurveyQuestion, SurveyChoice, SurveyResult
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from django.shortcuts import get_object_or_404
from .models import Bill, Payment
from django.shortcuts import render
from .utils.vnpay_helper import VNPay, get_client_ip
from rest_framework.permissions import AllowAny, SAFE_METHODS, IsAuthenticated, IsAdminUser
from .permissions import IsResidentOnly, IsAdminOnly
from .serializers import PaymentRequestSerializer
from .serializers import (
    SurveySerializer, SurveyQuestionSerializer, SurveyChoiceSerializer, SurveyResultSerializer, SurveyFeedbackSerializer
)
from decimal import Decimal
from apartment.utils.sms_helper import send_sms
logger = logging.getLogger(__name__)
from decimal import Decimal

from datetime import timedelta

from .serializers import PaymentSerializer
from rest_framework.parsers import JSONParser
class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            if user.is_locked:  # Sửa từ active sang is_locked
                return Response({
                    'error': 'Tài khoản đã bị khóa',
                    'reason': user.lock_reason
                }, status=status.HTTP_400_BAD_REQUEST)
            login(request, user)
            serializer = serializers.UserSerializer(user)
            return Response({'user': serializer.data}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Tên đăng nhập hoặc mật khẩu không đúng'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    
class ApartmentViewSet(viewsets.ModelViewSet):
    queryset = Apartment.objects.all()
    serializer_class = serializers.ApartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['number', 'floor', 'description']
    ordering_fields = ['number', 'floor', 'created_date']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Apartment.objects.none()
            
        if user.role == 'ADMIN':
            return Apartment.objects.all()
        elif user.role == 'RESIDENT':
            if not hasattr(user, 'apartment') or user.apartment is None:
                return Apartment.objects.none()
            return Apartment.objects.filter(id=user.apartment.id)
        return Apartment.objects.none()

    # @action(detail=True, methods=['get'])
    # def residents(self, request, pk=None):
    #     apartment = self.get_object()
    #     residents = User.objects.filter(apartment=apartment, role='RESIDENT')
    #     serializer = serializers.UserSerializer(residents, many=True)
    #     return Response(serializer.data)

    # @action(detail=True, methods=['get'])
    # def bills(self, request, pk=None):
    #     apartment = self.get_object()
    #     bills = Bill.objects.filter(apartment=apartment)
    #     serializer = serializers.BillSerializer(bills, many=True)
    #     return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='residents/(?P<resident_id>[^/.]+)/remove')
    def remove_resident(self, request, pk=None, resident_id=None):
        apartment = self.get_object()
        try:
            resident = apartment.residents.get(id=resident_id)
            apartment.residents.remove(resident)
            return Response({'message': 'Removed successfully'})
        except:
            return Response({'error': 'Resident not found'}, status=404)

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        apartment = self.get_object()
        summary = {
            'total_residents': User.objects.filter(apartment=apartment, role='RESIDENT').count(),
            'total_bills': Bill.objects.filter(apartment=apartment).count(),
            'pending_bills': Bill.objects.filter(apartment=apartment, status='PENDING').count(),
            'paid_bills': Bill.objects.filter(apartment=apartment, status='PAID').count(),
            'overdue_bills': Bill.objects.filter(apartment=apartment, status='OVERDUE').count(),
        }
        return Response(summary)
    
    def perform_create(self, serializer):
        if self.request.user.role != 'ADMIN':
            raise permissions.PermissionDenied('Chỉ có admin mới có quyền tạo căn hộ mới')
        
        serializer.save()
        
       
        
    def perform_update(self, serializer):
        if self.request.user.role != 'ADMIN':
            raise permissions.PermissionDenied("Chỉ admin mới có thể cập nhật căn hộ.")
        serializer.save()
        
    @action(detail=True, methods=['get'], permission_classes=[IsAdminOnly])
    def residents(self, request, pk=None):
        apartment = self.get_object()
        residents = User.objects.filter(apartment=apartment, active=True)
        serializer = serializers.UserSerializer(residents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
   

class UserViewSet(viewsets.ModelViewSet):
    # queryset = User.objects.filter(active=True)
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAdminOrSelf, IsPasswordChanged]
    pagination_class = paginators.ItemPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    


    def get_queryset(self):
        
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset
        
        query = self.queryset
        
        #xem coi người dùng đã đăng nhập chưa
        if not self.request.user.is_authenticated:
            return query.none()
        
        
        if self.request.user.role == 'RESIDENT':
            query = query.filter(id=self.request.user.id)
        q = self.request.query_params.get('q')
        if q:
            query = query.filter(Q(username__icontains=q) | Q(phone__icontains=q))
        role = self.request.query_params.get('role')
        if role:
            query = query.filter(role=role)
        apartment_number = self.request.query_params.get('apartment_number')
        if apartment_number:
            query = query.filter(apartment__number=apartment_number)
        
        apartment_id = self.kwargs.get('apartment_id')
        if apartment_id:
            query = query.filter(apartment_id=apartment_id)
        return query.order_by('-created_date')

    def perform_create(self, serializer):
        if self.request.user.role != 'ADMIN':
            raise permissions.PermissionDenied("Chỉ admin mới có thể tạo người dùng.")
        user = serializer.save()
        
        if user.role == 'RESIDENT':
            user.is_first_login = True

    def perform_update(self, serializer):
        if self.request.user.role != 'ADMIN' and self.get_object().id != self.request.user.id:
            raise permissions.PermissionDenied("Bạn chỉ có thể cập nhật thông tin của chính mình.")
        avatar_file = self.request.FILES.get('avatar')
        if avatar_file:
            upload_result = cloudinary.uploader.upload(avatar_file, folder='avatars/')
            serializer.save(avatar=upload_result['public_id'])
        else:
            serializer.save()

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminOnly])
    def assign_apartment(self, request, pk=None):
        user = self.get_object()
        apartment_id = request.data.get('apartment_id')
        if not apartment_id:
            return Response({'error': 'Vui lòng cung cấp apartment_id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            apartment = Apartment.objects.get(id=apartment_id)
            user.apartment = apartment
            user.save()
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Apartment.DoesNotExist:
            return Response({'error': 'Căn hộ không tồn tại'}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['get'], url_path='current-user', detail=False)
    def get_current_user(self, request):
        return Response(serializers.UserSerializer(request.user).data)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def lock_account(self, request, pk=None):
        user = self.get_object()
        user.is_locked = True
        user.save()
        return Response({'status': 'locked'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_pass(self, request):
        user = request.user

        old_pass = request.data.get('old_password')
        new_pass = request.data.get('new_password')

        if not user.check_password(old_pass):
            return Response({'error': 'Mật khẩu cũ không đúng'}, status=status.HTTP_400_BAD_REQUEST)

        if not new_pass or len(new_pass) < 8:
            return Response(
                {'error': 'Mật khẩu mới phải dài ít nhất 8 ký tự'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.password = make_password(new_pass)
        user.is_first_login = False
        user.save()

        return Response(
            {'message': 'Đổi mật khẩu thành công'},
            status=status.HTTP_200_OK
        )

    
    def perform_update(self, serializer):
        # Kiểm tra first login và avatar cho resident
        if self.request.user.role == 'RESIDENT' and self.request.user.is_first_login:
            if not self.request.FILES.get('avatar'):
                raise permissions.PermissionDenied(
                    "Cư dân phải upload avatar để hoàn tất thiết lập tài khoản."
                )
            
        # Xử lý upload avatar
        avatar_file = self.request.FILES.get('avatar')
        if avatar_file:
            upload_result = cloudinary.uploader.upload(avatar_file, folder='avatars/')
            serializer.save(avatar=upload_result['public_id'])
        else:
            serializer.save()
            
    #phải điền đủ form mới cho nhận nhà nhé bro
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def complete_setup(self, request):
        user = request.user
        if user.role != 'RESIDENT':
            raise permissions.PermissionDenied("Chỉ cư dân mới có thể thực hiện hành động này.")
        if user.is_first_login:
            raise permissions.PermissionDenied("Vui lòng đổi mật khẩu và upload avatar trước.")
        if not user.avatar:
            raise permissions.PermissionDenied("Vui lòng upload avatar.")
        user.is_first_login = False
        user.save()
        return Response({'message': 'Thiết lập tài khoản hoàn tất.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOnly], parser_classes=[JSONParser])
    def create_monthly_bills(self, request):
        # Lấy dữ liệu từ request (nếu có), không có thì dùng mặc định
        management_fee = request.data.get('management_fee', 500000)
        service_fee = request.data.get('service_fee', 200000)
        parking_fee = request.data.get('parking_fee', 300000)

        today = timezone.now()
        due_date = today + timedelta(days=30)
        residents = User.objects.filter(role='RESIDENT', apartment__isnull=False)
        created_bills = []

        for resident in residents:
            month_str = today.strftime("%m/%Y")

            desc_mgmt = f'Phí quản lý tháng {month_str}'
            if not Bill.objects.filter(user=resident, bill_type='management_fee', description=desc_mgmt).exists():
                created_bills.append(Bill(
                    user=resident,
                    bill_type='management_fee',
                    amount=management_fee,
                    description=desc_mgmt,
                    payment_method='momo_transfer',
                    due_date=due_date
                ))

            desc_service = f'Phí dịch vụ khác tháng {month_str}'
            if not Bill.objects.filter(user=resident, bill_type='service_fee', description=desc_service).exists():
                created_bills.append(Bill(
                    user=resident,
                    bill_type='service_fee',
                    amount=service_fee,
                    description=desc_service,
                    payment_method='momo_transfer',
                    due_date=due_date
                ))

            if resident.parking_card.exists():
                desc_parking = f'Phí gửi xe tháng {month_str}'
                if not Bill.objects.filter(user=resident, bill_type='parking_fee', description=desc_parking).exists():
                    created_bills.append(Bill(
                        user=resident,
                        bill_type='parking_fee',
                        amount=parking_fee,
                        description=desc_parking,
                        payment_method='momo_transfer',
                        due_date=due_date
                    ))

        Bill.objects.bulk_create(created_bills)
        return Response({
            'message': f'✅ Đã tạo {len(created_bills)} hóa đơn.',
            'management_fee': management_fee,
            'service_fee': service_fee,
            'parking_fee': parking_fee
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'], permission_classes=[IsAdminOnly])
    def toggle_lock(self, request, pk=None):
        try:
            user = self.get_object()
            reason = request.data.get('reason', '')
            
            if not reason and not user.is_locked:
                return Response({
                    'error': 'Vui lòng cung cấp lý do khóa tài khoản'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.is_locked = not user.is_locked
            user.lock_reason = reason if user.is_locked else None
            user.save()
            
            # Tạo thông báo
            Notification.objects.create(
                user=user,
                title='Trạng thái tài khoản thay đổi',
                content=f"Tài khoản của bạn đã được {'khóa' if user.is_locked else 'mở khóa'}" + 
                        (f" với lý do: {reason}" if user.is_locked else ""),
                type='system'
            )
            
            return Response({
                'status': 'success',
                'message': f"Tài khoản đã được {'khóa' if user.is_locked else 'mở khóa'}",
                'is_locked': user.is_locked,
                'reason': user.lock_reason
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
# Bill ViewSet
class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.filter(active=True)
    serializer_class = serializers.BillSerializer
    # permission_classes = [IsAdminOrSelf, IsPasswordChanged]
    permission_classes = [permissions.AllowAny]
    # pagination_class = paginators.ItemPagination
    # parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        query = self.queryset
        user_id = self.kwargs.get('user_id') or self.request.user.id
        query = query.filter(user_id=user_id)
        q = self.request.query_params.get('q')
        if q:
            query = query.filter(description__icontains=q)
        status_param = self.request.query_params.get('status')
        if status_param:
            query = query.filter(status=status_param)
        bill_type = self.request.query_params.get('bill_type')
        if bill_type:
            query = query.filter(bill_type=bill_type)
        return query.order_by('-due_date')

        return self.queryset.filter(user=user).order_by('-due_date')
    def perform_create(self, serializer):
        if self.request.user.role != 'ADMIN':
            raise permissions.PermissionDenied("Chỉ admin mới có thể tạo hóa đơn.")
        serializer.save()

    @action(detail=True, methods=['patch'])
    def upload_proof(self, request, pk=None):
        bill = self.get_object()

        if bill.status != 'pending':
            raise permissions.PermissionDenied("Hóa đơn không ở trạng thái chờ thanh toán.")

        if bill.user != request.user and request.user.role != 'ADMIN':
            raise permissions.PermissionDenied("Bạn không có quyền cập nhật hóa đơn này.")

        payment_proof = request.FILES.get('payment_proof')
        if payment_proof:
            upload_result = cloudinary.uploader.upload(payment_proof, folder='bills/')
            bill.payment_proof = upload_result['public_id']

        bill.payment_transaction_id = request.data.get('payment_transaction_id')

        # ✅ Cập nhật payment_method nếu client gửi
        new_method = request.data.get('payment_method')
        if new_method in ['momo_tranfer', 'bank_transfer']:
            bill.payment_method = new_method

        bill.status = 'submitted'
        bill.save()

        Payment.objects.create(
            user=bill.user,
            bill=bill,
            amount=bill.amount,
            payment_method='MOMO' if bill.payment_method == 'momo_transfer' else 'BANK',
            status='PENDING',
            transaction_id=bill.payment_transaction_id
        )

        serializer = self.get_serializer(bill)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminOnly])
    def confirm(self, request, pk=None):
        bill = self.get_object()
        bill.status = 'paid'
        bill.save()
        Notification.objects.create(
            user=bill.user,
            title='Thanh toán xác nhận',
            content=f'Hóa đơn {bill.id} đã được xác nhận.',
            type='bill'
        )
        serializer = self.get_serializer(bill)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOnly])
    def generate_monthly(self, request):
        residents = User.objects.filter(role='RESIDENT', apartment__isnull=False)
        amount = request.data.get('amount', 500000)
        description = request.data.get('description', 'Phí quản lý tháng này')
        bills = [
            Bill(
                user=resident,
                bill_type='management_fee',
                amount=amount,
                description=description,
                payment_method='momo_tranfer',
                due_date=timezone.now() + timezone.timedelta(days=30),
            ) for resident in residents
        ]
        Bill.objects.bulk_create(bills)
        return Response({'message': f'Đã tạo {len(bills)} hóa đơn'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsResidentOnly, IsPasswordChanged])
    def mock_momo_payment(self, request, pk=None):
        try:
            bill = self.get_object()
            if bill.status != 'pending':
                return Response({
                    'error': 'Hóa đơn đã được thanh toán hoặc không hợp lệ'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if bill.user != request.user:
                return Response({
                    'error': 'Không có quyền thanh toán hóa đơn này'
                }, status=status.HTTP_403_FORBIDDEN)

            # Tạo transaction ID
            transaction_id = f"MOCK-MOMO-{bill.id}-{int(timezone.now().timestamp())}"
            amount = bill.amount

            # Tạo payment_url giả lập
            payment_url = f"{settings.MOCK_MOMO_REDIRECT_URL}?transactionId={transaction_id}&billId={bill.id}"

            # Lưu giao dịch
            payment = Payment.objects.create(
                user=request.user,
                bill=bill,
                amount=amount,
                payment_method='MOMO',
                status='PENDING',
                transaction_id=transaction_id,
                payment_url=payment_url,
                payment_info={
                    'mock': True,
                    'source': 'Mock MoMo API',
                    'created_at': timezone.now().isoformat()
                }
            )

            logger.info(f"Created mock MoMo payment: {transaction_id} for bill {bill.id}")

            serializer = serializers.PaymentSerializer(payment)
            return Response({
                'payment_url': payment_url,
                'transaction_id': transaction_id,
                'bill_id': bill.id,
                'payment': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error creating mock MoMo payment: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='mock-momo/webhook', 
            permission_classes=[permissions.AllowAny])
    def mock_momo_webhook(self, request):
        try:
            logger.info(f"Received mock MoMo webhook: {request.data}")
            
            data = request.data
            transaction_id = data.get('transactionId')
            bill_id = data.get('billId')
            result_code = data.get('resultCode', 0) # 0: thành công, khác: thất bại

            # Tìm giao dịch
            payment = Payment.objects.filter(
                transaction_id=transaction_id, 
                bill__id=bill_id
            ).first()
            
            if not payment:
                logger.error(f"Payment not found: {transaction_id}")
                return Response({
                    'error': 'Giao dịch không tồn tại'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Cập nhật trạng thái
            if result_code == 0:
                payment.status = 'SUCCESS'
                payment.payment_date = timezone.now()
                payment.bill.status = 'paid'
                payment.bill.payment_transaction_id = transaction_id
                payment.bill.payment_method = 'online'
                payment.bill.save()
                payment.save()

                # Gửi thông báo
                Notification.objects.create(
                    user=payment.user,
                    title='Thanh toán thành công',
                    content=f'Hóa đơn {payment.bill.id} đã được thanh toán qua MoMo.',
                    type='bill'
                )
                
                logger.info(f"Payment successful: {transaction_id}")
            else:
                payment.status = 'FAILED'
                payment.save()
                logger.error(f"Payment failed: {transaction_id}")

            serializer = serializers.PaymentSerializer(payment)
            return Response({
                'message': 'Webhook processed',
                'transaction_id': transaction_id,
                'payment': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error processing mock MoMo webhook: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='mock-momo/success', permission_classes=[IsResidentOnly, IsPasswordChanged])
    def mock_momo_success(self, request):
        transaction_id = request.query_params.get('transactionId')
        bill_id = request.query_params.get('billId')

        # Tìm giao dịch
        payment = Payment.objects.filter(
            transaction_id=transaction_id, 
            bill__id=bill_id, 
            user=request.user
        ).first()
        if not payment:
            return Response({'error': 'Giao dịch không tồn tại hoặc không thuộc về bạn'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.PaymentSerializer(payment)
        if payment.status == 'SUCCESS':
            return Response({
                'message': 'Thanh toán giả lập thành công!',
                'payment': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'error': 'Thanh toán chưa hoàn tất hoặc thất bại',
            'payment': serializer.data
        }, status=status.HTTP_400_BAD_REQUEST)


class ParkingCardViewSet(viewsets.ModelViewSet):
    queryset = ParkingCard.objects.filter(active=True)
    serializer_class = serializers.ParkingCardSerializer
    permission_classes = [IsAdminOrSelf]
    pagination_class = paginators.ItemPagination

    def get_queryset(self):
        query = self.queryset
        user_id = self.kwargs.get('user_id') or self.request.user.id
        query = query.filter(user_id=user_id)
        card_code = self.request.query_params.get('card_code')
        if card_code:
            query = query.filter(card_code__icontains=card_code)
        return query.order_by('-created_date')

    def perform_create(self, serializer):
        if self.request.user.role != 'ADMIN':
            raise permissions.PermissionDenied("Chỉ admin mới có thể cấp thẻ xe.")
        serializer.save()
    
    @action(detail=False, methods=['post'], permission_classes=[IsResidentOnly], parser_classes=[MultiPartParser, FormParser])
    def request_card(self, request):
        serializer = serializers.CardRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, status='pending')
        admin = User.objects.filter(role='ADMIN').first()
        if admin:
            Notification.objects.create(
                user=admin,
                title='Yêu cầu thẻ mới',
                content=f'Cư dân {request.user.username} đã gửi yêu cầu {serializer.validated_data["type"]}.',
                type='system'
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
class CardRequestViewSet(viewsets.ModelViewSet):
    queryset = CardRequest.objects.all()
    serializer_class = serializers.CardRequestSerializer
    pagination_class = paginators.ItemPagination
    filterset_fields = ['type', 'status']

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [permissions.IsAuthenticated()]  # Cho phép xem GET, HEAD, OPTIONS
        return [IsAdminOnly()]  # Tất cả hành động khác (POST, PATCH, DELETE) chỉ admin được

    def get_queryset(self):
        query = self.queryset
        user = self.request.user

        # Nếu không phải admin → chỉ được xem thẻ của chính mình
        if not getattr(user, 'is_staff', False) and getattr(user, 'role', '') != 'ADMIN':
            query = query.filter(user=user)

        status_param = self.request.query_params.get('status')
        if status_param:
            query = query.filter(status=status_param)
        type_param = self.request.query_params.get('type')
        if type_param:
            query = query.filter(type=type_param)

        return query.order_by('-created_date')

    def perform_create(self, serializer):
        raise permissions.PermissionDenied("Không thể tạo yêu cầu thẻ trực tiếp qua API này.")

    def perform_update(self, serializer):
        raise PermissionDenied("Không thể chỉnh sửa yêu cầu thẻ.")

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminOnly])
    def approve(self, request, pk=None):
        card_request = self.get_object()
        if card_request.status != 'pending':
            return Response({'error': 'Yêu cầu đã được xử lý'}, status=status.HTTP_400_BAD_REQUEST)

        if card_request.type == 'relative':
            RelativeCard.objects.create(
                resident=card_request.user,
                name=card_request.name,
                relationship=card_request.relationship,
                card_number=f"REL-{card_request.id}-{timezone.now().strftime('%Y%m%d')}",
                active=True  # 👈 THÊM DÒNG NÀY
            )
        elif card_request.type == 'parking':
            ParkingCard.objects.create(
                user=card_request.user,
                relative_name=card_request.name,
                card_code=f"PARK-{card_request.id}-{timezone.now().strftime('%Y%m%d')}"
            )

        card_request.status = 'approved'
        card_request.save()

        Notification.objects.create(
            user=card_request.user,
            title='Yêu cầu thẻ được duyệt',
            content=f'Yêu cầu {card_request.type} của bạn đã được duyệt.',
            type='system'
        )

        serializer = self.get_serializer(card_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminOnly])
    def reject(self, request, pk=None):
        card_request = self.get_object()
        if card_request.status != 'pending':
            return Response({'error': 'Yêu cầu đã được xử lý'}, status=status.HTTP_400_BAD_REQUEST)

        card_request.status = 'rejected'
        card_request.save()

        Notification.objects.create(
            user=card_request.user,
            title='Yêu cầu thẻ bị từ chối',
            content=f'Yêu cầu {card_request.type} của bạn đã bị từ chối.',
            type='system'
        )

        serializer = self.get_serializer(card_request)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# RelativeCard ViewSet
class RelativeCardViewSet(viewsets.ModelViewSet):
    queryset = RelativeCard.objects.all() 
    serializer_class = serializers.RelativeCardSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = paginators.ItemPagination

    def get_queryset(self):
        user = self.request.user
        # Nếu là admin thì xem tất cả, cư dân chỉ xem thẻ của mình
        if user.role == 'ADMIN':
            return RelativeCard.objects.filter(active=True).order_by('-created_date')
        return RelativeCard.objects.filter(resident=user, active=True).order_by('-created_date')

    def perform_create(self, serializer):
        # Chỉ admin mới được phép tạo thủ công
        if self.request.user.role != 'ADMIN':
            raise permissions.PermissionDenied("Chỉ admin mới có thể cấp thẻ thân nhân.")
        serializer.save()

    @action(detail=False, methods=['post'], permission_classes=[IsResidentOnly])
    def request_card(self, request):
        serializer = serializers.CardRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Tạo yêu cầu
        serializer.save(user=request.user, status='pending')

        # Tạo thông báo gửi cho admin đầu tiên
        admin_user = User.objects.filter(role='ADMIN').first()
        if admin_user:
            Notification.objects.create(
                user=admin_user,
                title='Yêu cầu cấp thẻ',
                content=f'Cư dân {request.user.username} yêu cầu cấp thẻ người thân.',
                type='system'
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)
# Locker ViewSet
class LockerViewSet(viewsets.ModelViewSet):
    queryset = Locker.objects.filter(active=True)
    serializer_class = serializers.LockerSerializer
    # permission_classes = [AllowAny]
    permission_classes = [IsAdminOrSelf, IsPasswordChanged]
    # pagination_class = paginators.ItemPagination

    def get_queryset(self):
        query = self.queryset
        user_id = self.kwargs.get('user_id') or self.request.user.id
        query = query.filter(user_id=user_id)
        status_param = self.request.query_params.get('status')
        if status_param:
            query = query.filter(status=status_param)
        return query.order_by('-created_date')

    def perform_create(self, serializer):
        if self.request.user.role != 'ADMIN':
            raise permissions.PermissionDenied("Chỉ admin mới có thể tạo tủ đồ.")

        locker = serializer.save()

        Notification.objects.create(
            user=locker.user,
            title='Hàng mới trong tủ đồ',
            content=f'Bạn có hàng mới trong tủ đồ: {locker.item_description}.',
            type='system'
        )


    def mark_as_received(self, request, pk=None):
        locker = self.get_object()
        locker.status = 'received'
        locker.received_at = timezone.now()
        locker.save()
        return Response(status=status.HTTP_200_OK)

# Feedback ViewSet
class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.filter(active=True)
    serializer_class = serializers.FeedbackSerializer
    permission_classes = [IsAdminOrSelf, IsPasswordChanged]
    pagination_class = paginators.ItemPagination
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset
               
        query = self.queryset
        if self.request.user.role == 'RESIDENT':
            query = query.filter(user=self.request.user)
        user_id = self.kwargs.get('user_id')
        if user_id and self.request.user.role == 'ADMIN':
            query = query.filter(user_id=user_id)
        status_param = self.request.query_params.get('status')
        if status_param:
            query = query.filter(status=status_param)
        return query.order_by('-created_date')

    def perform_create(self, serializer):
        if self.request.user.role != 'RESIDENT':
            raise permissions.PermissionDenied("Chỉ cư dân mới có thể gửi phản hồi.")
        image = self.request.FILES.get('image')
        if image:
            upload_result = cloudinary.uploader.upload(image, folder='feedbacks/')
            serializer.save(user=self.request.user, image=upload_result['public_id'])
        else:
            serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminOnly])
    def respond(self, request, pk=None):
        feedback = self.get_object()
        feedback.response = request.data.get('response')
        feedback.status = 'resolved'
        feedback.save()
        Notification.objects.create(
            user=feedback.user,
            title='Phản hồi được trả lời',
            content=f'Phản hồi {feedback.id} đã được giải quyết.',
            type='feedback'
        )
        serializer = self.get_serializer(feedback)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def resolve(self, request, pk=None):
        feedback = self.get_object()
        feedback.status = 'resolved'
        feedback.save()
        return Response({'status': 'resolved'}, status=status.HTTP_200_OK)


# Survey ViewSet
class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [IsAuthenticated()]
        return [IsAdminOnly()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def questions(self, request, pk=None):
        survey = self.get_object()
        questions = SurveyQuestion.objects.filter(survey=survey)
        serializer = SurveyQuestionSerializer(questions, many=True)
        return Response(serializer.data)

class SurveyQuestionViewSet(viewsets.ModelViewSet):
    queryset = SurveyQuestion.objects.all()
    serializer_class = SurveyQuestionSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        print("Dữ liệu gửi tới survey-questions:", request.data)
        return super().create(request, *args, **kwargs)


class SurveyChoiceViewSet(viewsets.ModelViewSet):
    queryset = SurveyChoice.objects.all()
    serializer_class = SurveyChoiceSerializer
    permission_classes = [AllowAny]


# Cư dân: trả lời khảo sát
class SurveyResultViewSet(viewsets.ModelViewSet):
    queryset = SurveyResult.objects.all()
    serializer_class = SurveyResultSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
class SurveyFeedbackViewSet(viewsets.ModelViewSet):
    queryset = SurveyFeedback.objects.all()
    serializer_class = SurveyFeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Notification ViewSet
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.filter(active=True)
    serializer_class = serializers.NotificationSerializer
    permission_classes = [IsAdminOrSelf]
    pagination_class = paginators.ItemPagination

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset
        
        if not self.request.user.is_authenticated:
            return self.queryset.none()
            
        query = self.queryset.filter(user=self.request.user)
        type_param = self.request.query_params.get('type')
        if type_param:
            query = query.filter(type=type_param)
        is_read = self.request.query_params.get('is_read')
        if is_read == 'true':
            query = query.filter(is_read=True)
        elif is_read == 'false':
            query = query.filter(is_read=False)
        return query.order_by('-created_date')

    def perform_create(self, serializer):
        raise permissions.PermissionDenied("Không thể tạo thông báo trực tiếp qua API.")

    def perform_update(self, serializer):
        raise permissions.PermissionDenied("Không thể chỉnh sửa thông báo.")

    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'])
    def mark_all_as_read(self, request):
        notifications = self.get_queryset().filter(is_read=False)
        notifications.update(is_read=True)
        return Response({'message': f'Đã đánh dấu {notifications.count()} thông báo là đã đọc'}, status=status.HTTP_200_OK)

# ChatMessage ViewSet
class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.filter(active=True)
    serializer_class = serializers.ChatMessageSerializer
    permission_classes = [IsAdminOrSelf]
    pagination_class = paginators.ItemPagination

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset
        
        if not self.request.user.is_authenticated:
            return self.queryset.none()
        
        query = self.queryset.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        )
        user_id = self.request.query_params.get('user_id')
        if user_id:
            query = query.filter(
                Q(sender_id=user_id, receiver=self.request.user) |
                Q(receiver_id=user_id, sender=self.request.user)
            )
        is_read = self.request.query_params.get('is_read')
        if is_read == 'true':
            query = query.filter(is_read=True)
        elif is_read == 'false':
            query = query.filter(is_read=False)
        return query.order_by('created_date')

    def perform_create(self, serializer):
        receiver_id = self.request.data.get('receiver')
        if not User.objects.filter(id=receiver_id, active=True).exists():
            raise permissions.PermissionDenied("Người nhận không tồn tại.")
        serializer.save(sender=self.request.user)

    def perform_update(self, serializer):
        raise permissions.PermissionDenied("Không thể chỉnh sửa tin nhắn.")

    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, pk=None):
        message = self.get_object()
        if message.receiver != request.user:
            raise permissions.PermissionDenied("Bạn không phải người nhận tin nhắn này.")
        message.is_read = True
        message.save()
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)


# PaymentAccount ViewSet
class PaymentAccountViewSet(viewsets.ModelViewSet):
    queryset = PaymentAccount.objects.filter(active=True)
    serializer_class = serializers.PaymentAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = paginators.ItemPagination

    def get_queryset(self):
        # Kiểm tra nếu là swagger_fake_view
        if getattr(self, 'swagger_fake_view', False):
            return PaymentAccount.objects.none()

        query = self.queryset
        if self.request.user.is_authenticated:
            return query.filter(user=self.request.user)
        return query.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'])
    def active_accounts(self, request):
        accounts = self.get_queryset().filter(active=True)
        serializer = self.get_serializer(accounts, many=True)
        return Response(serializer.data)


class UploadAvatarViewSet(viewsets.ViewSet):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def upload(self, request):
        try:
            if 'file' not in request.FILES:
                return Response({'error': 'No file uploaded'}, status=400)
                
            file = request.FILES['file']
            # Validate file type
            if not file.content_type.startswith('image/'):
                return Response({'error': 'File must be an image'}, status=400)
                
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file,
                folder='avatars/',
                transformation=[
                    {'width': 200, 'height': 200, 'crop': 'fill'}
                ]
            )
            
            # Update user avatar
            request.user.avatar = result['secure_url']
            request.user.save()
            
            return Response({
                'avatar_url': result['secure_url'],
                'message': 'Avatar uploaded successfully'
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=400)
    queryset = PaymentAccount.objects.filter(active=True)
    serializer_class = serializers.PaymentAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = paginators.ItemPagination

    def get_queryset(self):
        query = self.queryset
        account_type = self.request.query_params.get('account_type')
        if account_type:
            query = query.filter(account_type=account_type)
        return query.order_by('-created_date')

    def perform_create(self, serializer):
        if self.request.user.role != 'ADMIN':
            raise permissions.PermissionDenied("Chỉ admin mới có thể tạo tài khoản thanh toán.")
        serializer.save()

    def perform_update(self, serializer):
        if self.request.user.role != 'ADMIN':
            raise permissions.PermissionDenied("Chỉ admin mới có thể cập nhật tài khoản thanh toán.")
        serializer.save()

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def active_accounts(self, request):
        accounts = self.queryset.filter(active=True)
        serializer = self.get_serializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class PaymentView(APIView):
    def post(self, request):
        serializer = PaymentRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            bill = Bill.objects.get(id=serializer.validated_data['bill_id'])
            if bill.status == 'paid':
                return Response({'error': 'Hóa đơn đã được thanh toán'}, status=status.HTTP_400_BAD_REQUEST)
            elif bill.status == 'overdue':
                return Response({'error': 'Hóa đơn đã quá hạn, không thể thanh toán'},
                                status=status.HTTP_400_BAD_REQUEST)

            payment = Payment.objects.create(
                user=request.user,
                bill=bill,
                amount=bill.amount,
                payment_method='BANK',
                status='PENDING'
            )
            print(settings.VNPAY_CONFIG['vnp_ReturnUrl'])

            vnp = VNPay()
            vnp.requestData = {
                'vnp_Version': '2.1.0',
                'vnp_Command': 'pay',
                'vnp_TmnCode': settings.VNPAY_CONFIG['vnp_TmnCode'],
                'vnp_Amount': int(bill.amount * 100),
                'vnp_CurrCode': 'VND',
                'vnp_TxnRef': str(payment.id),
                'vnp_OrderInfo': f"Thanh toán hóa đơn {bill.id}",
                'vnp_OrderType': 'billpayment',
                'vnp_Locale': serializer.validated_data.get('language', 'vn'),
                'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
                'vnp_IpAddr': get_client_ip(request),
                'vnp_ReturnUrl': settings.VNPAY_CONFIG['vnp_ReturnUrl']
            }

            if serializer.validated_data.get('bank_code'):
                vnp.requestData['vnp_BankCode'] = serializer.validated_data['bank_code']

            payment_url = vnp.get_payment_url()
            print("DEBUG RETURN URL:", vnp.requestData['vnp_ReturnUrl'])
            payment.payment_url = payment_url
            payment.save()

            return Response({
                'payment_url': payment_url,
                'payment_id': payment.id
            })

        except Bill.DoesNotExist:
            return Response({'error': 'Không tìm thấy hóa đơn'}, status=status.HTTP_404_NOT_FOUND)

class PaymentReturnView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        input_data = request.GET
        vnp = VNPay()
        vnp.responseData = input_data.dict()

        if not vnp.validate_response():
            return Response({
                "result": "error",
                "message": "Sai checksum",
                "data": vnp.responseData
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment_id = vnp.responseData.get('vnp_TxnRef')
            transaction_no = vnp.responseData.get('vnp_TransactionNo')
            response_code = vnp.responseData.get('vnp_ResponseCode')
            amount = Decimal(vnp.responseData.get('vnp_Amount')) / 100

            payment = get_object_or_404(Payment, id=payment_id)
            if payment.amount != amount:
                return Response({"error": "Số tiền không khớp"}, status=status.HTTP_400_BAD_REQUEST)

            if response_code == '00':
                payment.status = 'SUCCESS'
                payment.payment_date = timezone.now()
                payment.transaction_id = transaction_no
                payment.bill.status = 'paid'
                payment.bill.payment_transaction_id = transaction_no
                payment.bill.payment_method = 'online'
                payment.bill.save()
            else:
                payment.status = 'FAILED'

            payment.save()

            return Response({"message": "Xử lý thanh toán thành công", "status": payment.status})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class PaymentIPNView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        input_data = request.GET
        vnp = VNPay()
        vnp.responseData = input_data.dict()

        if not vnp.validate_response():
            return Response({'RspCode': '97', 'Message': 'Invalid Signature'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment_id = vnp.responseData.get('vnp_TxnRef')
            transaction_no = vnp.responseData.get('vnp_TransactionNo')
            response_code = vnp.responseData.get('vnp_ResponseCode')
            amount = int(vnp.responseData.get('vnp_Amount')) / 100

            payment = get_object_or_404(Payment, id=payment_id)
            if str(payment.amount) != str(amount):
                return Response({'RspCode': '04', 'Message': 'Invalid Amount'}, status=status.HTTP_400_BAD_REQUEST)

            if payment.status != 'PENDING':
                return Response({'RspCode': '02', 'Message': 'Order Already Confirmed'}, status=status.HTTP_200_OK)

            if response_code == '00':
                payment.status = 'SUCCESS'
                payment.payment_date = timezone.now()
                payment.transaction_id = transaction_no
                payment.bill.status = 'paid'
                payment.bill.payment_transaction_id = transaction_no
                payment.bill.payment_method = 'online'
                payment.bill.save()
            else:
                payment.status = 'FAILED'

            payment.save()

            return Response({'RspCode': '00', 'Message': 'Confirm Success'}, status=status.HTTP_200_OK)

        except Exception:
            return Response({'RspCode': '99', 'Message': 'Unknown Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


