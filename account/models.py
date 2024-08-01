import uuid
from django.db import models

class Account(models.Model):
    account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique= True)
    account_name = models.CharField(max_length=75, db_index=True, blank=False, null=False, unique= True)
    email = models.EmailField(max_length=50, blank=False, null=False, unique= True)
    secret_key = models.CharField(max_length=50, blank=False, null=False, unique=True)
    website = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Account'
        ordering = ['-pk']

    def __str__(self):
        return str(self.account_id)


class Destination(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    url = models.URLField(blank=False, null=False)
    http_method = models.CharField(max_length=10, blank=False, null=False)
    headers = models.JSONField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Destination for {self.account.account_name}"

