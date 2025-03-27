from django.contrib import admin
from apartment.models import User, Apartment, RelativeCard, Fee, Payment

admin.site.register(User)
admin.site.register(Apartment)
admin.site.register(RelativeCard)
admin.site.register(Fee)
admin.site.register(Payment)