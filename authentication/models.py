from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
import pyotp
from django.utils import timezone
from django.conf import settings

class User(AbstractUser):
    ADMIN = 1
    OPERATOR = 2
    CLIENT = 3
    USER = 4

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (OPERATOR, 'Operator'),
        (CLIENT, 'Client'),
        (USER, 'User'),
    )

    MALE = 1
    FEMALE = 2

    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )

    CONTENT_MANAGER = 1
    STANDARD_USER = 2

    USER_TYPE_CHOICES = (
        (CONTENT_MANAGER, 'Content Manager'),   
        (STANDARD_USER, 'Standard User'),
    )

    name = models.CharField(max_length=100, blank=True, null=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=ADMIN)
    groups = models.ManyToManyField('auth.Group', related_name='my_groups', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='my_user_permissions', blank=True)
    totp_secret = models.CharField(max_length=32, blank=True, null=True)
    timezone = models.CharField(max_length=50, default='America/New_York',null=True)
    company_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    office_phone = models.CharField(max_length=50, blank=True, null=True)
    gender = models.PositiveSmallIntegerField(choices=GENDER_CHOICES, default=MALE, null=True) 
    birthday = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    created_by = models.ForeignKey('self',on_delete=models.DO_NOTHING, null=True,related_name='created_users',)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, null=True, default=CONTENT_MANAGER)


class Company(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    subscription_ends = models.DateTimeField(null=True, default=None)
    subscription_renewal = models.BooleanField(default=False)
    related_users = models.ManyToManyField(
        'User',
        blank=True,
        related_name='related_users',
    )
    plan = models.PositiveSmallIntegerField(choices=settings.PLAN_CHOICES, default=None, null=True)


    @property
    def is_subscription_active(self):
        return timezone.now() < self.subscription_ends if self.subscription_ends else False


@receiver(post_save, sender=User)
def create_superuser(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        instance.totp_secret = pyotp.random_base32()
        instance.save()