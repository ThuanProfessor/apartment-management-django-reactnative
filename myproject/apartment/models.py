from urllib import response
from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField

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
    avatar = CloudinaryField('avatar', null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    apartment = models.OneToOneField('Apartment', on_delete=models.SET_NULL, null=True, blank=True)
    is_first_login = models.BooleanField(default=True, verbose_name="Lần đầu đăng nhập")
    is_locked = models.BooleanField(default=False, verbose_name="Tài khoản bị khóa")
    lock_reason = models.CharField(max_length=255, null=True, blank=True)
    

    def __str__(self):
        return self.username
    

class Apartment(BaseModel):
    STATUS_CHOICES = (
        ('vailable', 'Còn trống'),
        ('not_available', 'Đã cho thuê'),
    )
    number = models.CharField(max_length=10, unique=True, null=True)
    floor = models.IntegerField()
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    # user = models.ManyToManyField('User', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.number


class RelativeCard(BaseModel):
    name = models.CharField(max_length=50)
    relationship = models.CharField(max_length=50)
    card_number = models.CharField(max_length=20)
    resident = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} - {self.relationship} ({self.card_number})"
    
    
class Bill(BaseModel):
    PAYMENT_METHOD_CHOICE = (
        ('momo_tranfer', 'Chuyển khoản Momo'),
        ('online', 'Thanh toán trực tuyến'),
    )
    STATUS_CHOICE = (
        ('pending', 'Chờ thanh toán'),
        ('paid', 'Đã thanh toán'),
        ('overdue', 'Quá hạn'),
    )
    BILL_TYPE_CHOICES = (
        ('management_fee', 'Phí quản lý'),
        ('parking_fee', 'Phí gửi xe'),
        ('service_fee', 'Phí dịch vụ'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills')
    bill_type = models.CharField(max_length=20, choices=BILL_TYPE_CHOICES, default='management_fee')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, null=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICE)
    payment_proof = CloudinaryField('payment_proof', null=True, blank=True)
    payment_transaction_id = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='pending')
    due_date = models.DateTimeField(null=True, blank=True)
    
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
    tracking_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    status = models.CharField(max_length=10, choices = STATUS_CHOICE, default='pending')
    received_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Đồ: {self.item_description or 'Không có mô tả'} - {self.user.username}"
    
    
class Feedback(BaseModel):
    STATUS_CHOICE = (
        ('pending', 'Chờ phản hồi'),
        ('in_progress', 'Đang xử lý'),
        ('resolved', 'Đã giải quyết'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks', null=True, blank=True)
    content = RichTextField()
    image = CloudinaryField('image', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='pending')
    response = models.TextField(null=True, blank=True)
    
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
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
        
    def __str__(self):
        return self.title
    

class SurveyResult(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='survey_results')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='results')
    answer = RichTextField()
    
    def __str__(self):
        return f"Kết quả từ {self.user.username} - {self.survey.title}"
    

class Notification(BaseModel):
    TYPE_CHOICES = (
        ('locker', 'Tủ đồ'),
        ('bill', 'Hóa đơn'),
        ('feedback', 'Phản hồi'),
        ('survey', 'Khảo sát'),
        ('system', 'Hệ thống'),
     )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    content = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Thông báo {self.title} - {self.user.username}"
    
    
#tài khoản này nhận thanh toán chuyển khoản
class PaymentAccount(BaseModel):
    ACCOUNT_TYPE_CHOICES = (
        ('Momo', 'Momo'),
        ('Bank', 'Ngân hàng'),
    )
    
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='Bank')
    account_number = models.CharField(max_length=20, unique=True)
    account_name = models.CharField(max_length=50)
    descripttion = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.account_type} - {self.account_number} - {self.account_name}"
        

class ChatMessage(BaseModel):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    firebase_massage_id = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"Tin nhắn từ {self.sender.username} đến {self.receiver.username}"
    
    
class Payment(BaseModel):
     PAYMENT_METHOD_CHOICES = [
         ('MOMO', 'Momo'),
         ('BANK', 'Bank Transfer'),

     ]
     
     STATUS_CHOICES = [
         ('PENDING', 'Pending'),
         ('SUCCESS', 'Success'),
         ('FAILED', 'Failed'),
         ('CANCELLED', 'Cancelled'),
     ]
 
     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
     bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='payments')
     amount = models.DecimalField(max_digits=10, decimal_places=2)
     payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
     transaction_id = models.CharField(max_length=100, null=True, blank=True)
     payment_url = models.URLField(null=True, blank=True)
     payment_info = models.JSONField(null=True, blank=True)
     payment_date = models.DateTimeField(null=True, blank=True)
 
     class Meta:
         ordering = ['-created_date']
 
     def __str__(self):
         return f"Payment {self.id} - {self.amount} - {self.status}"
     

class CardRequest(BaseModel):
    TYPE_CHOICES = (
        ('relative', 'Thẻ thân nhân'),
        ('parking', 'Thẻ giữ xe'),
    )
    STATUS_CHOICES = (
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='card_requests')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Yêu cầu {self.type} từ {self.user.username}"