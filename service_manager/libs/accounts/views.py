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
from service_manager.middleware import threadlocals

from .forms import *
from .models import AccountUser


# Create your views here.


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'service_manager/index.html'


class LoginView(TemplateView):
    template_name = 'service_manager/auth/login.html'

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
    template_name = 'service_manager/auth/register.html'

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
    template_name = 'service_manager/auth/forgot.html'


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/accounts/login/')


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'service_manager/auth/profile.html'
    model = AccountUser
    form_class = ProfileForm
    slug_field = 'username'


class ChangePasswordView(LoginRequiredMixin, TemplateView):
    template_name = 'service_manager/auth/change_password.html'

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
from service_manager.apps.Supervisor.models import Config as SupervisorConfig
from service_manager.apps.Supervisor.core import SupervisorCore


class SupervisorIndexView(LoginRequiredMixin, ListView):
    template_name = 'service_manager/supervisor/index.html'
    model = SupervisorConfig
    paginate_by = 20
    ordering = 'create_time'

    def get(self, request, *args, **kwargs):
        self.queryset = SupervisorConfig.objects.filter(
            owner_id=request.user.pk)
        return super(SupervisorIndexView, self).get(request, *args,
                                                    **kwargs)


class SupervisorServiceStatus(LoginRequiredMixin, DetailView):
    model = SupervisorConfig

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        supervisor_core = SupervisorCore(host=object.host, port=object.port)
        status = supervisor_core.get_process_list()
        return HttpResponse(status)


class SupervisorServiceStatusCheck(LoginRequiredMixin, DetailView):
    model = SupervisorConfig

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


class SupervisorServiceRestartAll(LoginRequiredMixin, DetailView):
    model = SupervisorConfig

    def get(self, request, *args, **kwargs):
        response_data = dict()
        object = self.get_object()
        supervisor_core = SupervisorCore(host=object.host, port=object.port)
        status = supervisor_core.restart_all()
        if status:
            response_data['status'] = 200
            response_data['message'] = 'SUCCESS'
            return HttpResponse(json.dumps(response_data))

        response_data['status'] = 500
        response_data['message'] = 'FAIL'
        return HttpResponse(json.dumps(response_data))


class SupervisorServiceStopAll(LoginRequiredMixin, DetailView):
    model = SupervisorConfig

    def get(self, request, *args, **kwargs):
        response_data = dict()
        object = self.get_object()
        supervisor_core = SupervisorCore(host=object.host, port=object.port)
        status = supervisor_core.stop_all()
        if status:
            response_data['status'] = 200
            response_data['message'] = 'SUCCESS'
            return HttpResponse(json.dumps(response_data))

        response_data['status'] = 500
        response_data['message'] = 'FAIL'
        return HttpResponse(json.dumps(response_data))


class SupervisorServiceClearLog(LoginRequiredMixin, DetailView):
    model = SupervisorConfig

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
    template_name = 'service_manager/supervisor/tail.html'
    model = SupervisorConfig

    def get(self, request, *args, **kwargs):
        app = request.GET.get("app", None)
        object = self.get_object()
        supervisor_core = SupervisorCore(host=object.host, port=object.port)
        log = supervisor_core.tail(app)
        return render(request, self.get_template_names(), locals())


class SupervisorServiceTailF(LoginRequiredMixin, DetailView):
    template_name = 'service_manager/supervisor/tail_f.html'
    model = SupervisorConfig

    def get(self, request, *args, **kwargs):
        app = request.GET.get("app", None)
        object = self.get_object()
        supervisor_core = SupervisorCore(host=object.host, port=object.port)
        log = supervisor_core.tail_f(app)
        for item in log:
            yield render(request, self.get_template_names(), locals())


class SupervisorHostIndexView(LoginRequiredMixin, ListView):
    template_name = 'service_manager/supervisor/host/index.html'
    model = SupervisorConfig
    paginate_by = 20
    ordering = 'create_time'

    def get(self, request, *args, **kwargs):
        self.queryset = SupervisorConfig.objects.filter(
            owner_id=request.user.pk)
        return super(SupervisorHostIndexView, self).get(request, *args,
                                                        **kwargs)

    def post(self, request, *args, **kwargs):
        """
        实现批量删除功能
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.queryset = SupervisorConfig.objects.filter(
            owner_id=request.user.pk)
        selected_actions = request.POST.getlist('_selected_action')
        if not selected_actions:
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            context['warning'] = "条目必须选中以对其进行操作。没有任何条目被更改。"
            return self.render_to_response(context)
        delete = request.POST['post']
        if delete:
            action = SupervisorConfig.objects.filter(
                owner_id=request.user.pk).filter(
                id__in=selected_actions).delete()
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            context['info'] = "所选条目删除成功。"
            return self.render_to_response(context)
        object_list = SupervisorConfig.objects.filter(
            owner_id=request.user.pk).filter(
            id__in=selected_actions)
        return render(request,
                      'service_manager/supervisor/host/multi_delete.html',
                      locals())


class SupervisorHostAddView(LoginRequiredMixin, CreateView):
    template_name = 'service_manager/supervisor/host/add.html'
    form_class = SupervisorConfigForm
    success_url = reverse_lazy('accounts:supervisor-host-index')


class SupervisorHostDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'service_manager/supervisor/host/delete.html'
    model = SupervisorConfig
    success_url = reverse_lazy('accounts:supervisor-host-index')


class SupervisorHostChangeView(LoginRequiredMixin, UpdateView):
    template_name = 'service_manager/supervisor/host/change.html'
    model = SupervisorConfig
    form_class = SupervisorConfigForm
    success_url = reverse_lazy('accounts:supervisor-host-index')


###########
# ansible #
###########

from service_manager.apps.Ansible.models import Config as AnsibleConfig
from service_manager.apps.Ansible.ansible_api import AnsibleAPI


def pre_resources(resources):
    res_list = []
    for resource in resources:
        res = dict()
        res['hostname'] = resource.host
        res['username'] = resource.username
        res['password'] = resource.password
        res['port'] = resource.port
        res_list.append(res)
    return res_list


def deal_ansible_res(res, host):
    response_data = dict()
    if res.get("success").get(host):
        response_data['code'] = 200
        response_data['data'] = res.get("success").get(host)
    elif res.get("failed").get(host):
        response_data['code'] = 500
        response_data['msg'] = res.get("failed").get(host)
    elif res.get("unreachable").get(host):
        response_data['code'] = 400
        response_data['msg'] = res.get("unreachable").get(host)
    return response_data


class AnsibleHostIndexView(LoginRequiredMixin, ListView):
    template_name = 'service_manager/ansible/host/index.html'
    model = AnsibleConfig
    paginate_by = 20
    ordering = 'create_time'

    def get(self, request, *args, **kwargs):
        self.queryset = AnsibleConfig.objects.filter(
            owner_id=request.user.pk)
        return super(AnsibleHostIndexView, self).get(request, *args,
                                                     **kwargs)

    def post(self, request, *args, **kwargs):
        """
        实现批量删除功能
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.queryset = AnsibleConfig.objects.filter(
            owner_id=request.user.pk)
        selected_actions = request.POST.getlist('_selected_action')
        if not selected_actions:
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            context['warning'] = "条目必须选中以对其进行操作。没有任何条目被更改。"
            return self.render_to_response(context)
        delete = request.POST['post']
        if delete:
            action = AnsibleConfig.objects.filter(
                owner_id=request.user.pk).filter(
                id__in=selected_actions).delete()
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            context['info'] = "所选条目删除成功。"
            return self.render_to_response(context)
        object_list = AnsibleConfig.objects.filter(
            owner_id=request.user.pk).filter(
            id__in=selected_actions)
        return render(request,
                      'service_manager/ansible/host/multi_delete.html',
                      locals())


class AnsibleHostSystemInfo(LoginRequiredMixin, DetailView):
    model = AnsibleConfig
    slug_field = 'pk'

    def get(self, request, *args, **kwargs):
        resources = self.get_queryset().filter(owner_id=request.user.pk)
        ansible_api = AnsibleAPI(pre_resources(resources))
        ansible_api.run(['%s' % self.get_object().host], 'setup', '')
        res = deal_ansible_res(ansible_api.get_result(),
                               self.get_object().host)
        return HttpResponse(json.dumps(res))


class AnsibleRunModule(LoginRequiredMixin, ListView):
    model = AnsibleConfig

    def get(self, request, *args, **kwargs):
        response_data = dict()
        module = request.GET.get('module', '')
        module_args = request.GET.get('module_args', '')
        host_list = request.GET.get('host_list', '')

        if not module or not host_list:
            response_data['code'] = 500
            response_data['msg'] = "Insufficient parameters."
            return HttpResponse(json.dumps(response_data))

        host_list = host_list.split(',')
        print(host_list)

        resources = self.get_queryset().filter(owner_id=request.user.pk)
        ansible_api = AnsibleAPI(pre_resources(resources))
        ansible_api.run(host_list, module, module_args)
        res = ansible_api.get_result()
        response_data['code'] = 200
        response_data['msg'] = "success"
        response_data['data'] = res
        return HttpResponse(json.dumps(response_data))


class AnsibleHostAddView(LoginRequiredMixin, CreateView):
    template_name = 'service_manager/ansible/host/add.html'
    form_class = AnsibleConfigForm
    success_url = reverse_lazy('accounts:ansible-host-index')


class AnsibleHostDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'service_manager/ansible/host/delete.html'
    model = AnsibleConfig
    success_url = reverse_lazy('accounts:ansible-host-index')


class AnsibleHostChangeView(LoginRequiredMixin, UpdateView):
    template_name = 'service_manager/ansible/host/change.html'
    model = AnsibleConfig
    form_class = AnsibleConfigForm
    success_url = reverse_lazy('accounts:ansible-host-index')
