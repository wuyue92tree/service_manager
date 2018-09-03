# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from service_manager.apps.Resource.models import Host
from service_manager.libs.accounts.models import AccountUser

# Create your models here.
from service_manager.middleware import threadlocals


class Config(models.Model):

    host = models.ForeignKey(Host, related_name="ansible_host",
                             verbose_name=u"主机地址")
    port = models.IntegerField(default=22, verbose_name=u"端口")
    username = models.CharField(max_length=255, blank=True, null=True,
                                verbose_name=u"登录用户")
    password = models.CharField(max_length=255, blank=True, null=True,
                                verbose_name=u"登录密码")
    owner = models.ForeignKey(AccountUser, verbose_name=u"创建者",
                              related_name='ansible_config')
    create_time = models.DateTimeField(auto_now=True, verbose_name=u"加入时间")

    def __unicode__(self):
        return u"%s:%d" % (self.host, self.port)

    def save(self, *args, **kwargs):
        if not self.owner_id:
            self.owner = threadlocals.get_current_user()
        super(Config, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('host', 'port', 'owner')
        verbose_name = "主机配置"
        verbose_name_plural = verbose_name

