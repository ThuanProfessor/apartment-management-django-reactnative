import time
from rest_framework import serializers
from .models import Apartment, User, Bill, Feedback, Survey, SurveyResult, Notification, ChatMessage, PaymentAccount, Payment, CardRequest
from dataclasses import fields
from re import S, U
import cloudinary
from rest_framework.serializers import ModelSerializer
from apartment.models import ChatMessage, Notification, PaymentAccount, User, Apartment, RelativeCard, Bill, ParkingCard, Locker, Feedback, Survey, SurveyResult
from django import forms
from rest_framework import serializers
from django.utils import timezone

class ApartmentSerializer(ModelSerializer):
    class Meta:
        model = Apartment
        fields =  '__all__'


class ItemSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):        
        data = super().to_representation(instance)
        
        if hasattr(instance, 'image') and instance.image:
            try:
                data['image'] = instance.image.url
            except AttributeError:
                data['image'] = str(instance.image)
        
        if hasattr(instance, 'payment_proof') and instance.payment_proof:
            try:
                data['payment_proof'] = instance.payment_proof.url
                
            except AttributeError:
                data['payment_proof'] = str(instance.payment_proof)
                
        if hasattr(instance, 'avatar') and instance.avatar:
            try:
                data['avatar'] = instance.avatar.url
            except AttributeError:
                data['avatar'] = str(instance.avatar)
        
        return data
        
        # cloudinary_fields = ['image', 'payment_proof', 'avatar']
        
        # for field in cloudinary_fields:
        #     if hasattr(instance, field) and getattr(instance, field):
        #         try:
        #             data[field] = getattr(instance, field).url
        #         except AttributeError:
        #             data[field] = str(getattr(instance, field))


class UserSerializer(ItemSerializer):
    apartment_number = serializers.CharField(source='apartment.number', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'phone', 'avatar', 'apartment', 'apartment_number', 'active', 'is_first_login']
        extra_kwargs = {'password': {'write_only': True}}
  
    def get_has_completed_setup(self, obj):
        return not obj.is_first_login and bool(obj.avatar)
    
    def to_representation(self, instance):        
        data = super().to_representation(instance)
        if instance.avatar:
            data['avatar'] = instance.avatar.url
        return data
    
    def create(self, validated_data):
        data = validated_data.copy()
        u = User(**data)
        u.set_password(u.password)
        u.save()
        
        return u
    
    def update(self, instance, validated_date):
        if 'password' in validated_date:
            instance.set_password(validated_date.pop('password'))
        
        return super().update(instance, validated_date)
    

class MockMomoPayment:
    @staticmethod
    def create_payment_url(amount, bill_id):
        # Tạo mock payment URL
        return {
            'status': 'success',
            'message': 'Mock Payment URL created',
            'pay_url': f'http://mock-momo.com/pay/{bill_id}',
            'transaction_id': f'MOCK_{bill_id}_{int(time.time())}'
        }

    @staticmethod
    def verify_payment(transaction_id):
       #Mock payment verification
        return {
            'status': 'success',
            'message': 'Payment verified',
            'transaction_id': transaction_id
        }

    
class BillSerializer(ItemSerializer):
    status_display = serializers.SerializerMethodField()

    def get_status_display(self, obj):
        return obj.get_status_display()
    apartment_number = serializers.CharField(source='apartment.number', read_only=True)
    user_name = serializers.CharField(source = 'user.username', read_only=True)
    class Meta:
        model = Bill
        fields = ['id', 'user', 'user_name', 'apartment_number', 'bill_type', 'amount', 'description',
                  'payment_method', 'payment_proof', 'payment_transaction_id', 'status', 'status_display',
                  'due_date', 'created_date']
        

class ParkingCardSerializer(ModelSerializer):
    apartment_number = serializers.CharField(source='user.apartment.number', read_only=True)
    user_name = serializers.CharField(source = 'user.username', read_only=True)
    class Meta:
        model = ParkingCard
        fields = ['id', 'user', 'user_name', 'apartment_number', 'relative_name', 'card_code', 'active']
        

class RelativeCardSerializer(serializers.ModelSerializer):
    apartment_number = serializers.CharField(source='resident.apartment.number', read_only=True)
    resident_name = serializers.CharField(source='resident.username', read_only=True)
    
    class Meta:
        model = RelativeCard
        fields = ['id', 'resident', 'resident_name', 'apartment_number', 'name', 'relationship', 'card_number', 'active']
        
        
class LockerSerializer(serializers.ModelSerializer):
    apartment_number = serializers.CharField(source='user.apartment.number', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Locker
        fields = [
            'id', 'user', 'user_name', 'apartment_number', 'item_description',
            'tracking_code', 'status', 'received_at', 'created_date', 'image'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.image and not str(instance.image).startswith("http"):
            data['image'] = f"https://res.cloudinary.com/dg5ts9slf/{instance.image}"
        return data


class FeedbackSerializer(ItemSerializer):
    apartment_number = serializers.CharField(source='user.apartment.number', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'user_name', 'apartment_number', 'content', 'image', 'status', 'response', 'created_date']
        
        
class SurveySerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Survey
        fields = ['id', 'title', 'choice', 'description', 'created_by', 'created_by_name', 
                 'start_date', 'end_date', 'active', 'created_date', 'is_active']

    def get_is_active(self, obj):
        now = timezone.now()
        return obj.start_date <= now <= obj.end_date
                

class SurveyResultSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    apartment_number = serializers.CharField(source='user.apartment.number', read_only=True)
    survey_title = serializers.CharField(source='survey.title', read_only=True)
    
    class Meta:
        model = SurveyResult
        fields = ['id', 'user', 'user_name', 'apartment_number', 'survey', 'survey_title', 'answer', 'created_date']


class NotificationSerializer(serializers.ModelSerializer):
    apartment_number = serializers.CharField(source='user.apartment.number', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'user_name', 'apartment_number', 'title', 'content', 'type', 'is_read', 'created_date']


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    receiver_name = serializers.CharField(source='receiver.username', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'sender_name', 'receiver', 'receiver_name', 'content', 'is_read', 
                 'firebase_massage_id', 'created_date']


class PaymentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAccount
        fields = ['id', 'account_type', 'account_number', 'account_name', 'descripttion', 'active']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'bill', 'amount', 'payment_method', 
                 'status', 'transaction_id', 'payment_url', 
                 'payment_info', 'payment_date', 'created_date']
        read_only_fields = ['user', 'status', 'transaction_id', 
                          'payment_url', 'payment_info', 'payment_date']
        

class CardRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardRequest
        fields = '__all__'
        read_only_fields = ['user', 'status', 'created_date']

    def validate(self, data):
        if data['type'] == 'relative' and not data.get('relationship'):
            raise serializers.ValidationError("Mối quan hệ là bắt buộc cho thẻ thân nhân.")
        return data


# class UserDetailSerializer(UserSerializer):
#     class Meta:
#         model = UserSerializer.Meta.model
#         fields = UserSerializer.Meta.fields + ['apartment', 'role', 'active', 'is_first_login']
        

class PaymentRequestSerializer(serializers.Serializer):
        bill_id = serializers.IntegerField()  # Thay vì subscription_id
        bank_code = serializers.CharField(required=False, max_length=20)
        language = serializers.CharField(default='vn', max_length=2)
class PaymentResponseSerializer(serializers.Serializer):
    vnp_TransactionNo = serializers.CharField()
    vnp_Amount = serializers.IntegerField()
    vnp_OrderInfo = serializers.CharField()
    vnp_ResponseCode = serializers.CharField()
    vnp_TransactionStatus = serializers.CharField()
class PaymentForm(forms.Form):
    order_id = forms.CharField(max_length=250)
    order_type = forms.CharField(max_length=20)
    amount = forms.IntegerField()
    order_desc = forms.CharField(max_length=100)
    bank_code = forms.CharField(max_length=20, required=False)
    language = forms.CharField(max_length=2)