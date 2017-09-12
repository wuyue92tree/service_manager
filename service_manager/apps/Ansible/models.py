# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from service_manager.libs.accounts.models import AccountUser

# Create your models here.
from service_manager.middleware import threadlocals


class Supplier(models.Model):
    # 主机服务商
    name = models.CharField(max_length=255, verbose_name="主机服务商")
    description = models.TextField(verbose_name="服务商描述")
    owner = models.ForeignKey(AccountUser, verbose_name=u"创建者")

    def __unicode__(self):
        return "%s" % self.name

    def save(self, *args, **kwargs):
        if not self.owner:
            self.owner = threadlocals.get_current_user()
        super(Supplier, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('name', 'owner')
        verbose_name = "主机服务商配置"
        verbose_name_plural = verbose_name


class Config(models.Model):
    # 系统平台
    PLATFORM_CHOICE = (
        ("LINUX", "LINUX"),
        ("WINDOW", "WINDOWS"),
        ("MAC", "MAC")
    )
    host = models.CharField(max_length=255, verbose_name=u"主机地址")
    port = models.IntegerField(default=22, verbose_name=u"端口")
    username = models.CharField(max_length=255, blank=True, null=True,
                                verbose_name=u"登录用户")
    password = models.CharField(max_length=255, blank=True, null=True,
                                verbose_name=u"登录密码")
    supplier = models.ForeignKey("Supplier", verbose_name=u"主机服务商")
    platform = models.CharField(max_length=255, choices=PLATFORM_CHOICE,
                                verbose_name=u"系统平台")
    owner = models.ForeignKey(AccountUser, verbose_name=u"创建者",
                              related_name='ansible_config')
    create_time = models.DateTimeField(auto_now=True, verbose_name=u"加入时间")

    def __unicode__(self):
        return u"%s:%d" % (self.host, self.port)

    def save(self, *args, **kwargs):
        if not self.owner:
            self.owner = threadlocals.get_current_user()
        super(Config, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('host', 'port', 'owner')
        verbose_name = "主机配置"
        verbose_name_plural = verbose_name



