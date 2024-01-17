from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.core.signing import Signer, BadSignature
from .utils import mx_wallet, mx_contract, get_address, mx_send


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError('Users require an username field')
        user = self.model(username=username, **extra_fields)
        user.save(using=self._db)
        user.set_password(password)
        pem_key = mx_wallet(user.id)
        user.set_pem_key(pem_key)
        user.address = get_address(user.pem_key)
        print(user.address)
        user.save(using=self._db)
        mx_send(user.address)

        mx_contract(user.pem_key, "add_account", [username])
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)

class CustomUser(AbstractUser):
    username = models.TextField(unique=True)

    objects = UserManager()
    pem_key = models.TextField()
    address = models.TextField()

    def set_pem_key(self, pem_key):
        self.pem_key = pem_key

    def get_pem_key(self):
        signer = Signer()
        try:
            return signer.unsign(self.pem_key)
        except BadSignature:
            return None