from django.db import models
from django.contrib.auth.models import AbstractUser


class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser, BaseModel):
    
    ROLE_CHOICES = (
        ('ADMIN', 'Quản trị viên'),
        ('RESIDENT', 'Cư dân')
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', null=False)
    phone = models.CharField(max_length=15)

    

class Apartment(BaseModel):
    number = models.CharField(max_length=10)
    floor = models.IntegerField()
    area = models.FloatField()
    resident = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    

class RelativeCard(BaseModel):
    name = models.CharField(max_length=50)
    relationship = models.CharField(max_length=50)
    card_number = models.CharField(max_length=20)
    resident = models.ForeignKey(User, on_delete=models.CASCADE)
    
    
class Fee(BaseModel):
    FEE_CHOICES = (
        ('MANAGEMENT', 'Phí Quản Lý'),
        ('PARKING', 'Phí Gửi Xe'),
        ('SERVICE', 'Phí Dịch Vụ')
    )
    
    type = models.CharField(max_length=20, choices=FEE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    

class Payment(BaseModel):
    PAYMENT_STATUS =(
        ('PAID', 'Đã thanh toán'),
        ('UNPAID', 'Chưa thanh toán'),
        ('OVERDUE', 'Quá hạn'),
        ('CANCEL', 'Hủy bỏ')

    )
    
    PAYMENT_METHOD = (
        'TRANSFER', 'Chuyển khoản',
        'MOMO', 'Momo Pay',
        'VNPAY', 'VN Pay'
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS)
    image_conf = models.ImageField(upload_to='pay/%Y/%m/', null=True)
    
    resident = models.ForeignKey(User, on_delete=models.CASCADE)
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE)
    
    
class Locker(BaseModel):
    number = models.CharField(max_length=10)
    resident = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    
class Package(BaseModel):
    PACKAGE_STATUS = (
        ('RECEIVED', 'Đã nhận'),
        ('NOT_RECEIVED', 'Chưa nhận')
    )
    name = models.CharField(max_length=50)
    weight = models.FloatField()
    status = models.CharField(max_length=20, choices=PACKAGE_STATUS)
    locker = models.ForeignKey(Locker, on_delete=models.CASCADE)
    

class Feedback(BaseModel):
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resident = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title
    
    
class Survey(BaseModel):
    title = models.CharField(max_length= 100)
    content = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    def __str__(self):
        return self.title
    
    
class Question(BaseModel):
    content = models.TextField()
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    
    
class Answer(BaseModel):
    content = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    resident = models.ForeignKey(User, on_delete=models.CASCADE)
    


