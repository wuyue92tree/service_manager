#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: wuyue92tree@163.com

from __future__ import unicode_literals, print_function
import json
import uuid
import os
import itchat
import hashlib
from braces.views import LoginRequiredMixin
from django.contrib.auth import authenticate
from django.contrib.auth.views import login, logout
from django.db import IntegrityError
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import *

from .forms import *
from .models import AccountUser


# Create your views here.


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/index.html'


class LoginView(TemplateView):
    template_name = 'accounts/auth/login.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/')
        else:
            return super(LoginView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.data['username'],
                                password=form.data['password'])

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/accounts/')

                else:
                    return HttpResponse("账号未激活")
            else:
                form.add_error('password', '用户名不存在/密码不正确')
                return render(request, self.get_template_names(), locals())
        else:
            return render(request, self.get_template_names(), locals())

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context['form'] = LoginForm()
        return context


class RegisterView(TemplateView):
    template_name = 'accounts/auth/register.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)

        if form.data['password'] != form.data['rpassword']:
            form.add_error('rpassword', '两次输入的密码不一致')

        if form.is_valid():
            user = AccountUser.objects.create_user(
                username=form.data['username'],
                nickname=form.data['nickname'],
                email=form.data['email'],
                password=form.data['password']
            )
            user.is_active = True
            user.save()
            return HttpResponse("注册成功")
        else:
            return render(request, self.template_name, locals())

    def get_context_data(self, **kwargs):
        context = super(RegisterView, self).get_context_data(**kwargs)
        context['form'] = RegisterForm()
        return context


class ForgotView(TemplateView):
    template_name = 'accounts/auth/forgot.html'


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/accounts/login/')


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/auth/profile.html'
    model = AccountUser
    form_class = ProfileForm
    slug_field = 'username'


class ChangePasswordView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/auth/change_password.html'

    def post(self, request, *args, **kwargs):
        form = ChangePasswordForm(self.request.user, request.POST)
        if form.is_valid():
            return "修改成功"
        else:
            return render(request, self.get_template_names(), locals())

    def get_context_data(self, **kwargs):
        context = super(ChangePasswordView, self).get_context_data(**kwargs)
        context['form'] = ChangePasswordForm(self.request.user)
        return context


##############
# supervisor #
##############

from .forms import SupervisorConfigForm
from service_manager.apps.supervisor.models import Config as SupervisorConfig
from service_manager.apps.supervisor.core import SupervisorCore


class SupervisorIndexView(LoginRequiredMixin, ListView):
    template_name = 'accounts/supervisor/index.html'
    model = SupervisorConfig
    paginate_by = 20


class SupervisorServiceStatus(LoginRequiredMixin, DetailView):
    model = SupervisorConfig
    slug_field = 'slug'

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        supervisor_core = SupervisorCore(host=object.host, port=object.port)
        status = supervisor_core.get_process_list()
        return HttpResponse(status)


class SupervisorServiceStatusCheck(LoginRequiredMixin, DetailView):
    model = SupervisorConfig
    slug_field = 'slug'

    def get(self, request, *args, **kwargs):
        response_data = dict()
        object = self.get_object()
        supervisor_core = SupervisorCore(host=object.host, port=object.port)
        status = supervisor_core.status()

        if status:
            response_data['status'] = 200
            response_data['message'] = 'SUCCESS'
            return HttpResponse(json.dumps(response_data))

        response_data['status'] = 500
        response_data['message'] = 'FAIL'
        return HttpResponse(json.dumps(response_data))


class SupervisorServiceStart(LoginRequiredMixin, DetailView):
    model = SupervisorConfig
    slug_field = 'slug'

    def get(self, request, *args, **kwargs):
        response_data = dict()
        app = request.GET.get("app", None)
        object = self.get_object()
        supervisor_core = SupervisorCore(host=object.host, port=object.port)
        status = supervisor_core.start(app)
        if status:
            response_data['status'] = 200
            response_data['message'] = 'SUCCESS'
            return HttpResponse(json.dumps(response_data))

        response_data['status'] = 500
        response_data['message'] = 'FAIL'
        return HttpResponse(json.dumps(response_data))


class SupervisorServiceStop(LoginRequiredMixin, DetailView):
    model = SupervisorConfig
    slug_field = 'slug'

    def get(self, request, *args, **kwargs):
        response_data = dict()
        app = request.GET.get("app", None)
        object = self.get_object()
        supervisor_core = SupervisorCore(host=object.host, port=object.port)
        status = supervisor_core.stop(app)
        if status:
            response_data['status'] = 200
            response_data['message'] = 'SUCCESS'
            return HttpResponse(json.dumps(response_data))

        response_data['status'] = 500
        response_data['message'] = 'FAIL'
        return HttpResponse(json.dumps(response_data))


class SupervisorServiceRestart(LoginRequiredMixin, DetailView):
    model = SupervisorConfig
    slug_field = 'slug'

    def get(self, request, *args, **kwargs):
        response_data = dict()
        app = request.GET.get("app", None)
        object = self.get_object()
        supervisor_core = SupervisorCore(host=object.host, port=object.port)
        status = supervisor_core.restart(app)
        if status:
            response_data['status'] = 200
            response_data['message'] = 'SUCCESS'
            return HttpResponse(json.dumps(response_data))

        response_data['status'] = 500
        response_data['message'] = 'FAIL'
        return HttpResponse(json.dumps(response_data))


class SupervisorServiceClearLog(LoginRequiredMixin, DetailView):
    model = SupervisorConfig
    slug_field = 'slug'

    def get(self, request, *args, **kwargs):
        response_data = dict()
        app = request.GET.get("app", None)
        object = self.get_object()
        supervisor_core = SupervisorCore(host=object.host, port=object.port)
        status = supervisor_core.clearlog(app)
        if status:
            response_data['status'] = 200
            response_data['message'] = 'SUCCESS'
            return HttpResponse(json.dumps(response_data))

        response_data['status'] = 500
        response_data['message'] = 'FAIL'
        return HttpResponse(json.dumps(response_data))


class SupervisorServiceTail(LoginRequiredMixin, DetailView):
    template_name = 'accounts/supervisor/tail.html'
    model = SupervisorConfig
    slug_field = 'slug'

    def get(self, request, *args, **kwargs):
        app = request.GET.get("app", None)
        object = self.get_object()
        supervisor_core = SupervisorCore(host=object.host, port=object.port)
        log = supervisor_core.tail(app)
        return render(request, self.get_template_names(), locals())


class SupervisorHostIndexView(LoginRequiredMixin, ListView):
    template_name = 'accounts/supervisor/host/index.html'
    model = SupervisorConfig
    paginate_by = 20

    def post(self, request, *args, **kwargs):
        """
        实现批量删除功能
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        selected_actions = request.POST.getlist('_selected_action')
        if not selected_actions:
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            context['warning'] = "条目必须选中以对其进行操作。没有任何条目被更改。"
            return self.render_to_response(context)
        delete = request.POST['post']
        if delete:
            action = SupervisorConfig.objects.filter(
                id__in=selected_actions).delete()
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            context['info'] = "所选条目删除成功。"
            return self.render_to_response(context)
        object_list = SupervisorConfig.objects.filter(
            slug__in=selected_actions)
        return render(request,
                      'accounts/supervisor/host/multi_delete.html',
                      locals())


class SupervisorHostAddView(LoginRequiredMixin, CreateView):
    template_name = 'accounts/supervisor/host/add.html'
    form_class = SupervisorConfigForm
    success_url = reverse_lazy('accounts:supervisor-host-index')


class SupervisorHostDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'accounts/supervisor/host/delete.html'
    model = SupervisorConfig
    slug_field = 'slug'
    success_url = reverse_lazy('accounts:supervisor-host-index')


class SupervisorHostChangeView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/supervisor/host/change.html'
    model = SupervisorConfig
    form_class = SupervisorConfigForm
    slug_field = 'slug'
    success_url = reverse_lazy('accounts:supervisor-host-index')


