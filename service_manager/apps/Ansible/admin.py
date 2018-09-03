# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *


# Register your models here.


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'username', 'owner', 'create_time')
    list_filter = ('owner',)
    search_fields = ('host',)
