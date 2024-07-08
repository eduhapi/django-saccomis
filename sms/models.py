from django.db import models

class SMSNotification(models.Model):
    phone_number = models.CharField(max_length=15)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.phone_number} - {self.timestamp}'

class SMSLog(models.Model):
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(max_length=10)  # 'success' or 'failed'
    created_at = models.DateTimeField(auto_now_add=True)

