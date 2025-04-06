from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField


class BaseModel(models.Model): 
    active = models.BooleanField(default=True, verbose_name="Trạng thái hoạt động")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.id} - {self.created_date}"
    

class User(AbstractUser, BaseModel):
    
    ROLE_CHOICES = (
        ('ADMIN', 'Quản trị viên'),
        ('RESIDENT', 'Cư dân')
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='RESIDENT')
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    apartment = models.OneToOneField('Apartment', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username
    

class Apartment(BaseModel):
    number = models.CharField(max_length=10, unique=True, null=True)
    floor = models.IntegerField()
    description = models.TextField()
    # user = models.ManyToManyField('User', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.number


class RelativeCard(BaseModel):
    name = models.CharField(max_length=50)
    relationship = models.CharField(max_length=50)
    card_number = models.CharField(max_length=20)
    resident = models.ForeignKey(User, on_delete=models.CASCADE)
    
    
class Bill(BaseModel):
    PAYMENT_METHOD_CHOICE = (
        ('momo_tranfer', 'Chuyển khoản Momo'),
        ('online', 'Thanh toán trực tuyến'),
    )
    STATUS_CHOICE = (
        ('pending', 'Chờ thanh toán'),
        ('paid', 'Đã thanh toán'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, null=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICE)
    payment_proof = models.ImageField(upload_to='pay/%Y/%m/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='pending')
    
    def __str__(self):
        return f"Hoá đơn {self.id} - {self.user.username}"

        
class ParkingCard(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parking_card')
    relative_name = models.CharField(max_length=100)
    card_code = models.CharField(max_length=15, unique=True)
    
    def __str__(self):
        return f"Thẻ {self.card_code} - {self.relative_name}"
    
    
class Locker(BaseModel):
    STATUS_CHOICE = (
        ('pending', 'Chờ nhận'),
        ('received', 'Đã nhận'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lockers')
    item_description = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=10, choices = STATUS_CHOICE, default='pending')
    received_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Đồ: {self.item_description or 'Không có mô tả'} - {self.user.username}"
    
    
class Feedback(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks', null=True, blank=True)
    content = RichTextField()
    image = models.ImageField(upload_to='feedback/%Y/%m/', null=True, blank=True)
    
    def __str__(self):
        return f"Phản hồi từ {self.user.username if self.user else 'Anonymous'}"
    

class Survey(BaseModel):
    SURVEY_CHOICE = (
        ('Hygiene_issues', 'Vệ sinh'),
        ('Facilities ', 'Cơ sở vật chất'),
        ('Service','Dịch vụ'),
    )
    title = models.CharField(max_length=100)
    choice = models.CharField(max_length=50, choices=SURVEY_CHOICE, default='Service')
    description = RichTextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='surveys')
    
    def __str__(self):
        return self.title
    

class SurveyResult(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='survey_results')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='results')
    answer = RichTextField()
    def __str__(self):
        return f"Kết quả từ {self.user.username} - {self.survey.title}"
    
 