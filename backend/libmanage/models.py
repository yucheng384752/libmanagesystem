from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User


# Create your models here.
class Book(models.Model):
     # 定義書籍分類的選項 
   CATEGORY_CHOICES = [
        ('SCIENCE', '科學'),
        ('LANGUAGE', '語言'),
        ('HISTORY', '歷史'),
        ('FICTION', '小說'),
        ('ENGINEERING', '工程'),
        ('ART', '藝術'),
        ('COMPUTER', '電腦'), 
        ('OTHER', '其他'),
    ]
    # 新增書籍狀態的選項
   STATUS_CHOICES = [
       ('AVAILABLE', '可借閱'),
       ('DAMAGED', '已損壞'),
       ('UNDER_REPAIR', '維修中'),
       ('LOST', '遺失'),
   ]
   title = models.CharField('書名', max_length=100)
   author = models.CharField('作者', max_length=50)
   isbn  = models.CharField('ISBN', max_length=17, blank=True)
   is_borrowed = models.BooleanField(default=False)
   category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='OTHER',
        verbose_name='書籍分類'
    )
   # 新增 status 欄位
   status = models.CharField(
       max_length=20,
       choices=STATUS_CHOICES,
       default='AVAILABLE', # 預設狀態為「可借閱」
       verbose_name='書籍狀態'
   )
   def __str__(self):
       return self.title
   
    
class BorrowRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    returned = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.user.username} borrowed {self.book.title}' 
    
    @property  #檢查是否逾期
    def is_overdue(self):
        return not self.returned and self.due_date < timezone.now().date()