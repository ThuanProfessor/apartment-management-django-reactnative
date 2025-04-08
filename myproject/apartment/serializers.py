
from dataclasses import fields
from re import S, U
from rest_framework.serializers import ModelSerializer
from apartment.models import ChatMessage, Notification, PaymentAccount, User, Apartment, RelativeCard, Bill, ParkingCard, Locker, Feedback, Survey, SurveyResult

from rest_framework import serializers

class ApartmentSerializer(ModelSerializer):
    class Meta:
        model = Apartment
        fields =  ['id', 'number', 'floor', 'active']


class ItemSerializer(ModelSerializer):
    def to_representation(self, instance):        
        data = super().to_representation(instance)
        if instance.image and instance.image.startswith('image/upload/'):
            data['image'] = instance.image.url
        return data

class UserSerializer(ItemSerializer):
    apartment_number = serializers.CharField(source='apartment.number', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'phone', 'avatar', 'apartment', 'apartment_number', 'active', 'is_first_login']
    
    extra_kwargs = {
        'password': {'write_only': True}
    }
    
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
    
    
class BillSerializer(ItemSerializer):
    apartment_number = serializers.CharField(source='apartment.number', read_only=True)
    user_name = serializers.CharField(source = 'user.username', read_only=True)
    class Meta:
        model = Bill
        fields = ['id', 'user', 'user_name', 'apartment_number', 'bill_type', 'amount', 'description', 
                 'payment_method', 'payment_proof', 'payment_transaction_id', 'status', 'due_date', 'created_date']
        

class PackingCardSerializers(ModelSerializer):
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
    user_name = serializers.CharField(source = 'user.username', read_only=True)
    
    class Meta:
        model = Locker
        fields = ['id', 'user', 'user_name', 'apartment_number', 'item_description', 'tracking_code', 
                 'status', 'received_at', 'created_date']


class FeedbackSerializer(ItemSerializer):
    apartment_number = serializers.CharField(source='user.apartment.number', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'user_name', 'apartment_number', 'content', 'image', 'status', 'response', 'created_date']
        
        
class SurveySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Survey
        fields = ['id', 'title', 'choice', 'description', 'created_by', 'created_by_name', 
                 'start_date', 'end_date', 'active', 'created_date']


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


class UserDetailSerializer(UserSerializer):
    class Meta:
        model = UserSerializer.Meta.model
        fields = UserSerializer.Meta.fields + ['apartment', 'role', 'active', 'is_first_login']