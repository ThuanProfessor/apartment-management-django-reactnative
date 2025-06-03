from string import Template
from django.contrib import admin
from apartment.models import CardRequest, User, Apartment, RelativeCard, Bill, ParkingCard, Locker, Feedback, Survey, SurveyResult
from django.utils.safestring import mark_safe
from django.template.response import TemplateResponse
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum
from django.utils.timezone import now, timedelta
from apartment.models import Apartment, User, Bill, RelativeCard, ParkingCard, Feedback
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
        fields = ('username', 'email', 'password1', 'password2', 'role', 'phone', 'apartment', 'is_first_login', 'active')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

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
        ('Custom Fields', {'fields': ('role', 'phone', 'apartment', 'is_first_login', 'active', 'avatar', 'is_locked', 'lock_reason')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'phone', 'apartment', 'is_first_login', 'active'),
        }),
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
    list_display = ['user', 'item_description', 'tracking_code', 'status', 'received_at', 'image_view_locker']
    search_fields = ['user__username', 'item_description', 'tracking_code']
    list_filter = ['status']
    readonly_fields = ['image_view_locker']

    def image_view_locker(self, obj):
        if obj.image:
            return mark_safe(f"<img src='{obj.image.url}' width='150' />")
        return "Không có ảnh"

    image_view_locker.short_description = "Ảnh tủ đồ"

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
        return [
            path('apartment-stats/', self.admin_view(self.apartment_stats)),
            path('report-dashboard/', self.admin_view(self.report_dashboard)),
        ] + super().get_urls()

    def apartment_stats(self, request):
    # Đếm số lượng căn hộ cho mỗi user
        stats = User.objects.annotate(apm_count=Count('apartment__id')).values('id', 'username', 'apm_count')
        total_apartments = Apartment.objects.count()  # Tổng số căn hộ
        
        return TemplateResponse(request, 'apartment-stats.html', {
            'stats': stats,
            'total_apartments': total_apartments  # Thêm tổng số
        })

    def report_dashboard(self, request):
        total_apartments = Apartment.objects.count()
        empty_apartments = Apartment.objects.filter(status='available').count()
        occupied_apartments = total_apartments - empty_apartments

        total_users = User.objects.filter(role='RESIDENT').count()
        locked_users = User.objects.filter(role='RESIDENT', is_locked=True).count()
        new_users = User.objects.filter(role='RESIDENT', created_date__gte=now() - timedelta(days=30)).count()

        total_bills = Bill.objects.count()
        paid_bills = Bill.objects.filter(status='paid').count()
        pending_bills = Bill.objects.filter(status='pending').count()
        overdue_bills = Bill.objects.filter(status='overdue').count()
        total_revenue = Bill.objects.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0

        total_parking_cards = ParkingCard.objects.count()
        total_relative_cards = RelativeCard.objects.count()

        feedback_stats = Feedback.objects.values('status').annotate(count=Count('id'))
        selected_month = int(request.GET.get('month', now().month))
        # Doanh thu theo tháng trong năm hiện tại
        bills_by_month = (
            Bill.objects.filter(status='paid', created_date__year=now().year)
            .annotate(month=TruncMonth('created_date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        fees_by_type = (
            Bill.objects.filter(
                status='paid',
                created_date__year=now().year,
                created_date__month=selected_month
            )
            .values('bill_type')
            .annotate(total=Sum('amount'))
        )

        fee_labels = ['Phí quản lý', 'Phí gửi xe', 'Phí dịch vụ']
        fee_types = ['management_fee', 'parking_fee', 'service_fee']
        fee_data = []

        fee_map = {f['bill_type']: float(f['total']) for f in fees_by_type}
        for key in fee_types:
            fee_data.append(fee_map.get(key, 0))

        months = [(i, now().replace(month=i).strftime('%B')) for i in range(1, 13)]
        revenue_labels = [b['month'].strftime('%B') for b in bills_by_month]
        revenue_data = [float(b['total']) for b in bills_by_month]

        return TemplateResponse(request, 'admin/report-dashboard.html', {
            'total_apartments': total_apartments,
            'empty_apartments': empty_apartments,
            'occupied_apartments': occupied_apartments,
            'total_users': total_users,
            'locked_users': locked_users,
            'new_users': new_users,
            'total_bills': total_bills,
            'paid_bills': paid_bills,
            'pending_bills': pending_bills,
            'overdue_bills': overdue_bills,
            'total_revenue': total_revenue,
            'total_parking_cards': total_parking_cards,
            'total_relative_cards': total_relative_cards,
            'feedback_stats': feedback_stats,
            'revenue_labels': revenue_labels,
            'revenue_data': revenue_data,
            'fee_labels': fee_labels,
            'fee_data': fee_data,
            'selected_month': selected_month,
            'months': months,
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

