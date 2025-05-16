from string import Template
from django.contrib import admin
from apartment.models import CardRequest, User, Apartment, RelativeCard, Bill, ParkingCard, Locker, Feedback, Survey, SurveyResult
from django.utils.safestring import mark_safe
from django.db.models import Count
from django.template.response import TemplateResponse

from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.urls import path

class FeedbackForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)
    
    class Meta:
        model = Feedback
        fields = '__all__'


class ApartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'floor', 'created_date', 'updated_date', 'active']
    search_fields = ['number', 'floor']
    list_filter = ['number', 'floor']
    
    class Media:
        css = {
            'all': ('/static/css/style.css',)
        }


from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role', 'phone', 'apartment', 'is_first_login', 'active')

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = UserChangeForm.Meta.fields

class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ['id', 'username', 'role', 'phone', 'apartment', 'is_first_login', 'active']
    search_fields = ['username', 'role', 'phone', 'apartment']
    list_filter = ['role', 'apartment', 'active']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone', 'apartment', 'is_first_login', 'active')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone', 'apartment', 'is_first_login', 'active')}),
    )


class BillAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'payment_method', 'status']
    search_fields = ['user', 'amount', 'payment_method', 'status']
    list_filter = ['user', 'status']
    readonly_fields = ['image_view']
   
    
    def image_view(self, bill):
        if bill.payment_proof:
            return mark_safe(f"<img src='/static/{bill.payment_proof.name}' width='100' />")
        return "Không có ảnh"
    
    class Media:
        css = {
            'all': ('/static/css/style.css',)  # Thêm file CSS tùy chỉnh
        }
    
    
class ParkingCardAdmin(admin.ModelAdmin):
    list_display = ['user', 'relative_name', 'card_code', 'active']
    search_fields = ['user', 'relative_name', 'card_code']
    list_filter = ['user', 'active']
    
    class Media:
        css = {
            'all': ('/static/css/style.css',)
        }
    
    
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'status']
    search_fields = ['user']
    readonly_fields = ['image_view_feedback']
    form = FeedbackForm
    
    def image_view_feedback(self, feedback):
        if feedback.image:
            return mark_safe(f"<img src='/static/{feedback.image.name}' width='100' />")
        return "Không có ảnh"



class LockerAdmin(admin.ModelAdmin):
    list_display = ['user', 'item_description', 'tracking_code', 'status', 'received_at']
    search_fields = ['user', 'item_description', 'tracking_code', 'status']
    list_filter = ['user', 'status']
    readonly_fields = ['image_view_locker']
    
    def image_view_locker(self, locker):
        if locker.tracking_code:
            return mark_safe(f"<img src='/static/{locker.tracking_code.name}' width='100' />")
        return "Không có ảnh"


class SurveyAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'created_date', 'updated_date', 'created_by']
    search_fields = ['title', 'created_by']
    list_filter = ['created_by']
    
    def image_view_survey(self, survey):
        if survey.image:
            return mark_safe(f"<img src='/static/{survey.image.name}' width='100' />")
        return "Không có ảnh"
    

class CardRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'name', 'relationship', 'status', 'created_date']
    search_fields = ['user__username', 'name', 'type']
    list_filter = ['type', 'status']


#tạo instance của riêng
class MyAdminSite(admin.AdminSite):
    site_header = 'Apartment Management'
    index_title = 'Welcome to Apartment Management Admin'
    # login_template = 'admin/custom_login.html'
    # logout_template = 'admin/custom_logout.html'
    
    def get_urls(self):
        return [path('apartment-stats/', self.apartment_stats)] + super().get_urls()
    
    def apartment_stats(self, request):
    # Đếm số lượng căn hộ cho mỗi user
        stats = User.objects.annotate(apm_count=Count('apartment__id')).values('id', 'username', 'apm_count')
        total_apartments = Apartment.objects.count()  # Tổng số căn hộ
        
        return TemplateResponse(request, 'admin/apartment-stats.html', {
            'stats': stats,
            'total_apartments': total_apartments  # Thêm tổng số
        })
        
        
    # Thêm context tùy chỉnh
    def each_context(self, request):
        context = super().each_context(request)
        context['custom_message'] = 'Custom Admin Site for Apartment Management'
        return context
    
    
admin_site = MyAdminSite(name='ApartmentManagement')
    
    

admin_site.register(User, UserAdmin)
admin_site.register(Apartment, ApartmentAdmin)
admin_site.register(RelativeCard)
admin_site.register(Bill, BillAdmin)
admin_site.register(ParkingCard)
admin_site.register(Locker, LockerAdmin)
admin_site.register(Feedback, FeedbackAdmin)
admin_site.register(Survey, SurveyAdmin)
admin_site.register(SurveyResult)
admin_site.register(CardRequest, CardRequestAdmin)

