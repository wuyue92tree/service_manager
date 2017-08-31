# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


class AccountUser(AbstractUser):
    GENDER_CHOICE = {
        ('M', _('male')),
        ('F', _('female')),
        ('U', _('unkown')),
    }
    nickname = models.CharField(max_length=20, blank=True, verbose_name=_('nickname'))
    phone = models.BigIntegerField(blank=True, null=True, verbose_name=_('phone'))
    head_avatar = models.ImageField(
        upload_to='./avatars',
        default="./avatars/default.png",
        blank=True,
        verbose_name=_('head_avatar'))
    head_oauth_avatar = models.URLField(blank=True, verbose_name=_('head_oauth_avatar'))
    description = models.TextField(blank=True, verbose_name=_('description'))
    gender = models.CharField(max_length=10, blank=True, choices=GENDER_CHOICE, verbose_name=_('gender'))
    birthday = models.DateField(default=timezone.now, verbose_name=_('birthday'))
    activate_key = models.SlugField(max_length=40, blank=True, verbose_name=_('activate_key'))

    def get_absolute_url(self):
        return '/accounts/profile/%s/' % self.username
