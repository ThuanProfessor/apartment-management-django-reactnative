from django.contrib import admin
from apartment.models import User, Apartment, RelativeCard, Bill, ParkingCard, Locker, Feedback, Survey, SurveyResult


class UserAdmin(admin.ModelAdmin):
    pass



admin.site.register(User)
admin.site.register(Apartment)
admin.site.register(RelativeCard)
admin.site.register(Bill)
admin.site.register(ParkingCard)
admin.site.register(Locker)
admin.site.register(Feedback)
admin.site.register(Survey)
admin.site.register(SurveyResult)