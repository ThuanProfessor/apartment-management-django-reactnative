from rest_framework import viewsets, generics
from apartment.models import Apartment, User, RelativeCard, Bill, ParkingCard, Locker, Feedback, Survey, SurveyResult
from apartment import serializers, paginators



class ApartmentViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Apartment.objects.filter(active=True)
    serializer_class = serializers.ApartmentSerializer

 
class UserViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = User.objects.filter(active=True)
    serializer_class = serializers.UserSerializer
    pagination_class = paginators.ItemPagination
    
    def get_queryset(self):
        query = self.queryset
        
        q = self.request.query_params.get('q')
        if q:
            query = query.filter(username__icontains=q)
            
        apartment_number = self.request.query_params.get('apartment_number')
        if apartment_number:
            query = query.filter(apartment_number=apartment_number)
        return query