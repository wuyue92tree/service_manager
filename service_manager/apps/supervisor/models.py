# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
from django.db import models


# Create your models here.


class Config(models.Model):
    host = models.CharField(max_length=255, verbose_name=u"主机地址")
    port = models.IntegerField(default=9001, verbose_name=u"端口")
    username = models.CharField(max_length=255, blank=True, null=True,
                                verbose_name=u"用户名")
    password = models.CharField(max_length=255, blank=True, null=True,
                                verbose_name=u"密码")
    create_time = models.DateTimeField(auto_now=True, verbose_name=u"加入时间")
    slug = models.CharField(max_length=40, verbose_name="slug")

    def __unicode__(self):
        return u"%s:%d" % (self.host, self.port)

    def save(self, *args, **kwargs):
        self.slug = hashlib.sha1(self.host + str(self.port)).hexdigest()
        super(Config, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('host', 'port')
        verbose_name = "Supervisor配置"
        verbose_name_plural = verbose_name
