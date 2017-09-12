# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Config

# Register your models here.


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'username', 'password',
                    'owner', 'create_time')
    list_filter = ('host',)
    search_fields = ('host', 'port', 'username')
