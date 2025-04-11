from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
import cloudinary.uploader
from apartment.models import Apartment, User, RelativeCard, Bill, ParkingCard, Locker, Feedback, Survey, SurveyResult, PaymentAccount, Notification, ChatMessage
from apartment import serializers, paginators
from apartment.permissions import IsAdminOnly, IsAdminOrSelf, IsResidentOnly
from django.core.exceptions import PermissionDenied

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            serializer = serializers.UserSerializer(user)

            return Response({'user': serializer.data}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Thông tin không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        logout(request)
        return Response({'message':'Đăng xuất thành công'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def showme(self, request):
        serializer = serializers.UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class ApartmentViewSet(viewsets.ModelViewSet):
    queryset = Apartment.objects.filter(active=True)
    serializer_class = serializers.ApartmentSerializer
    permission_classes = [IsAdminOrSelf]
    pagination_class = paginators.ItemPagination
    
    def get_queryset(self):
        query = self.queryset
        
        if self.request.user.role == 'RESIDENT':
            query = query.filter(id=self.request.user.apartment.id)
        q = self.request.query_params.get('q')
        if q:
            query = query.filter(number__icontains=q)
            
        floor = self.request.query_params.get('floor')
        if floor:
            query = query.filter(floor=floor)
            
        status = self.request.query_params.get('status')
        if status:
            query = query.filter(status=status)
        return query.order_by('number')
    
    
    def perform_create(self, serializer):
        if self.request.user.role != 'ADMIN':
            raise PermissionDenied('Chỉ có admin mới có quyền tạo căn hộ mới')
        
        serializer.save()
        
    def perform_update(self, serializer):
        if self.request.user.role != 'ADMIN':
            raise PermissionDenied("Chỉ admin mới có thể cập nhật căn hộ.")
        serializer.save()
        
    @action(detail=True, methods=['get'], permission_classes=[IsAdminOnly])
    def residents(self, request, pk=None):
        apartment = self.get_object()
        residents = User.objects.filter(apartment=apartment, active=True)
        serializer = serializers.UserSerializer(residents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
   

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(active=True)
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAdminOrSelf]
    pagination_class = paginators.ItemPagination
    parser_classes = [MultiPartParser, FormParser]
    
    
    def get_queryset(self):
        query = self.queryset
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
        return query.order_by('-created_date')

    def perform_create(self, serializer):
        if self.request.user.role != 'ADMIN':
            raise permissions.PermissionDenied("Chỉ admin mới có thể tạo người dùng.")
        serializer.save()

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

    @action(detail=True, methods=['get'])
    def bills(self, request, pk=None):
        user = self.get_object()
        bills = Bill.objects.filter(user=user, active=True)
        status_param = request.query_params.get('status')
        if status_param:
            bills = bills.filter(status=status_param)
        page = self.paginate_queryset(bills)
        if page is not None:
            serializer = serializers.BillSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.BillSerializer(bills, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
# class BillViewSet(viewsets.ViewSet, generics.ListAPIView):
#     queryset = Bill.objects.filter(active=True)
#     serializer_class = serializers.BillSerializer
#     pagination_class = paginators.ItemPagination
    
#     def get_queryset(self):
#         user_id = self.kwargs.get('user_id')
#         queryset = self.queryset.filter(user_id=user_id)
#         q = self.request.query_params.get('q')
#         if q:
#             queryset = queryset.filter(description__icontains=q)
#         return queryset


# class ParkingCardViewSet(viewsets.ViewSet):
#     queryset = ParkingCard.objects.filter(active=True)
#     serializer_class = serializers.PackingCardSerializers
#     pagination_class = paginators.ItemPagination
    
#     def get_queryset(self):
#         queryset = self.queryset
        
#         user_id = self.kwargs.get('user_pk') or self.request.query_params.get('user_id')
        
#         # Nếu là cư dân, chỉ xem thẻ của mình
#         if self.request.user.role == 'RESIDENT' and not user_id:
#             queryset = queryset.filter(user=self.request.user)
#         elif user_id:
#             queryset = queryset.filter(user_id=user_id)
        
#         return queryset
    
    

# # RelativeCard ViewSet
# class RelativeCardViewSet(viewsets.ModelViewSet):
#     queryset = RelativeCard.objects.filter(active=True)
#     serializer_class = serializers.RelativeCardSerializer
#     pagination_class = paginators.ItemPagination
#     permission_classes = [permissions.IsAuthenticated]
    
#     def get_queryset(self):
#         queryset = self.queryset
        
#         # Lấy user_id từ URL nested hoặc query parameter
#         user_id = self.kwargs.get('user_pk') or self.request.query_params.get('user_id')
        
#         # Nếu là cư dân, chỉ xem thẻ của mình
#         if self.request.user.role == 'RESIDENT' and not user_id:
#             queryset = queryset.filter(resident=self.request.user)
#         elif user_id:
#             queryset = queryset.filter(resident_id=user_id)
        
#         # Lọc theo mối quan hệ
#         relationship = self.request.query_params.get('relationship')
#         if relationship:
#             queryset = queryset.filter(relationship=relationship)
        
#         return queryset
    
    
# # Locker ViewSet
# class LockerViewSet(viewsets.ModelViewSet):
#     queryset = Locker.objects.filter(active=True)
#     serializer_class = serializers.LockerSerializer
#     pagination_class = paginators.ItemPagination
#     permission_classes = [permissions.IsAuthenticated]
    
#     def get_queryset(self):
#         queryset = self.queryset
        
#         # Lấy user_id từ URL nested hoặc query parameter
#         user_id = self.kwargs.get('user_pk') or self.request.query_params.get('user_id')
        
#         # Nếu là cư dân, chỉ xem tủ đồ của mình
#         if self.request.user.role == 'RESIDENT' and not user_id:
#             queryset = queryset.filter(user=self.request.user)
#         elif user_id:
#             queryset = queryset.filter(user_id=user_id)
        
#         # Lọc theo trạng thái
#         status = self.request.query_params.get('status')
#         if status:
#             queryset = queryset.filter(status=status)
        
#         return queryset
    
    
        
       

# # Feedback ViewSet
# class FeedbackViewSet(viewsets.ModelViewSet):
#     queryset = Feedback.objects.filter(active=True)
#     serializer_class = serializers.FeedbackSerializer
#     pagination_class = paginators.ItemPagination
#     permission_classes = [permissions.IsAuthenticated]
    
#     def get_queryset(self):
#         user_id = self.kwargs.get('user_id')
#         queryset = self.queryset.filter(user_id=user_id)
#         q = self.request.query_params.get('q')
#         if q:
#             queryset = queryset.filter(content__icontains=q)
#         return queryset
    
    
# # Survey ViewSet
# class SurveyViewSet(viewsets.ModelViewSet):
#     queryset = Survey.objects.filter(active=True)
#     serializer_class = serializers.SurveySerializer
#     pagination_class = paginators.ItemPagination
#     permission_classes = [permissions.IsAuthenticated]
    
#     def get_queryset(self):
#         query = self.queryset
        
#         # Lọc theo loại khảo sát
#         choice = self.request.query_params.get('choice')
#         if choice:
#             query = query.filter(choice=choice)
        
#         # Lọc theo ngày
#         now = timezone.now()
#         active = self.request.query_params.get('active')
#         if active == 'true':
#             query = query.filter(start_date__lte=now, end_date__gte=now)
#         elif active == 'false':
#             query = query.filter(Q(end_date__lt=now) | Q(start_date__gt=now))
        
#         return query
    
    
# # SurveyResult ViewSet
# class SurveyResultViewSet(viewsets.ModelViewSet):
#     queryset = SurveyResult.objects.filter(active=True)
#     serializer_class = serializers.SurveyResultSerializer
#     pagination_class = paginators.ItemPagination
#     permission_classes = [permissions.IsAuthenticated]
    
#     def get_queryset(self):
#         queryset = self.queryset
        
#         # Lấy user_id từ URL nested hoặc query parameter
#         user_id = self.kwargs.get('user_pk') or self.request.query_params.get('user_id')
        
#         # Nếu là cư dân, chỉ xem kết quả của mình
#         if self.request.user.role == 'RESIDENT' and not user_id:
#             queryset = queryset.filter(user=self.request.user)
#         elif user_id:
#             queryset = queryset.filter(user_id=user_id)
        
#         # Lọc theo khảo sát
#         survey_id = self.request.query_params.get('survey_id')
#         if survey_id:
#             queryset = queryset.filter(survey_id=survey_id)
        
#         return queryset
    
    

# # Notification ViewSet
# class NotificationViewSet(viewsets.ModelViewSet):
#     queryset = Notification.objects.filter(active=True)
#     serializer_class = serializers.NotificationSerializer
#     pagination_class = paginators.ItemPagination
#     permission_classes = [permissions.IsAuthenticated]
    
#     def get_queryset(self):
#         queryset = self.queryset.filter(user=self.request.user)
        
#         # Lọc theo loại thông báo
#         type = self.request.query_params.get('type')
#         if type:
#             queryset = queryset.filter(type=type)
        
#         # Lọc theo trạng thái đọc
#         is_read = self.request.query_params.get('is_read')
#         if is_read == 'true':
#             queryset = queryset.filter(is_read=True)
#         elif is_read == 'false':
#             queryset = queryset.filter(is_read=False)
        
#         return queryset
    
    

# # ChatMessage ViewSet
# class ChatMessageViewSet(viewsets.ModelViewSet):
#     queryset = ChatMessage.objects.filter(active=True)
#     serializer_class = serializers.ChatMessageSerializer
#     pagination_class = paginators.ItemPagination
#     permission_classes = [permissions.IsAuthenticated]
    
#     def get_queryset(self):
#         queryset = self.queryset.filter(
#             Q(sender=self.request.user) | Q(receiver=self.request.user)
#         )
        
#         # Lọc theo người gửi/người nhận
#         user_id = self.request.query_params.get('user_id')
#         if user_id:
#             queryset = queryset.filter(
#                 Q(sender_id=user_id, receiver=self.request.user) |
#                 Q(receiver_id=user_id, sender=self.request.user)
#             )
        
#         # Lọc theo trạng thái đọc
#         is_read = self.request.query_params.get('is_read')
#         if is_read == 'true':
#             queryset = queryset.filter(is_read=True)
#         elif is_read == 'false':
#             queryset = queryset.filter(is_read=False)
        
#         return queryset.order_by('created_date')
    
  