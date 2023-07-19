# This code defines a custom user authentication system using Django's built-in authentication
# framework. It consists of two main models: User and Profile. The User model extends
# Django's AbstractBaseUser and PermissionsMixin, providing a flexible user model with
# email-based authentication.
# The Profile model serves as an extension to the User model, containing additional user information
# such as address, image, user type, and clear password.
#
# The UserManager class defines custom methods for creating regular users and superusers,
# handling the creation and saving of user instances.
#
# Signal receivers (create_user_profile and save_user_profile) are used to automatically create and update
# a profile instance associated with each user. Additionally, the code includes an overridden
# save method in the Profile model to perform any necessary additional operations when saving the profile,
# such as image resizing.
#
# Overall, this code provides a foundation for a custom user authentication system in Django,
# allowing for the creation and management of users with extended profile information.

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from django.contrib.auth.models import Group, Permission


class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, **extra_fields)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True)
    name = models.CharField(max_length=254, null=True, blank=True)
    username = models.CharField(max_length=254, null=True, blank=True)  # TODO: #9 in models.py
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    groups = models.ManyToManyField(Group, verbose_name='groups', blank=True, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='user',
    )

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self):
        return "/users/%i/" % self.pk


class Profile(models.Model):
    USER_TYPES = (
        ('Admin', 'Admin'),
        ('director', 'director'),
        ('candidate', 'candidate'),
    )
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE, default=None)
    address = models.CharField(max_length=254, null=True, blank=True)
    image = models.ImageField(default='./profile_pics/default.png', upload_to='profile_pics')
    user_type = models.CharField(max_length=20,blank=True, null=True,choices=USER_TYPES)

    def __str__(self):
        return f'{self.user.email} Profile'
        # return self.pk

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # img = Image.open(self.image.path)
        #
        # if img.height > 300 or img.width >300:
        #     output_size = (300,300)
        #     img.thumbnail(output_size)
        #     img = Image.open(self.image.path)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



