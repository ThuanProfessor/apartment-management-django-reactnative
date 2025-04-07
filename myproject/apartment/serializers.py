from rest_framework.serializers import ModelSerializer
from apartment.models import ChatMessage, Notification, User, Apartment, RelativeCard, Bill, ParkingCard, Locker, Feedback, Survey, SurveyResult



class ApartmentSerializer(ModelSerializer):
    class Meta:
        model = Apartment
        fields =  ['id', 'number', 'floor', 'active']


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username','role', 'phone', 'avatar', 'apartment', 'active']
     

class RelativeCardSerializer(ModelSerializer):
    class Meta:
        model = RelativeCard
        fields = []   