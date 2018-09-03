# encoding=utf-8
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import UserChangeForm, UsernameField

from .models import AccountUser
from service_manager.apps.Supervisor.models import Config as SupervisorConfig
from service_manager.apps.Ansible.models import Config as AnsibleConfig


class AccountUserChangeForm(UserChangeForm):
    class Meta:
        model = AccountUser
        fields = '__all__'
        field_classes = {'username': UsernameField}


class LoginForm(forms.Form):
    """
    不直接继承model类，以避免username做唯一性检查
    """
    username = forms.CharField(required=True,
                               error_messages={'required': "用户名不能为空"},
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(required=True, min_length=8, max_length=12,
                               error_messages={'required': "密码不能为空",
                                               'min_length': "密码最小长度为八位",
                                               'max_length': '密码最大长度为十二位'},
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class RegisterForm(forms.ModelForm):
    password = forms.CharField(required=True, min_length=8, max_length=12,
                               error_messages={'required': "密码不能为空",
                                               'min_length': "密码最小长度为八位",
                                               'max_length': '密码最大长度为十二位'},
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    rpassword = forms.CharField(required=True,
                                error_messages={'required': "重复密码不能为空"},
                                widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                  'placeholder': 'Repeat Password'}))

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs = {'class': 'form-control', 'placeholder': 'Username'}
        self.fields['email'].required = True
        self.fields['email'].widget.attrs = {'class': 'form-control', 'placeholder': 'Email'}
        self.fields['nickname'].required = True
        self.fields['nickname'].widget.attrs = {'class': 'form-control', 'placeholder': 'Nickname'}

    class Meta:
        model = AccountUser
        fields = ('username', 'nickname', 'email')

        error_messages = {
            'username': {'required': "用户不能为空", 'invalid': "不是一个有效的用户名格式"},
            'nickname': {'required': "昵称不能为空"},
            'email': {'required': "邮箱地址不能为空", 'invalid': "不是一个有效的邮箱地址格式"},
        }


class ProfileForm(forms.ModelForm):
    """
    更新用户信息
    """
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['username'].disabled = True
        self.fields['last_login'].disabled = True
        self.fields['date_joined'].disabled = True
        self.fields['username'].widget.attrs = {'class': 'col-xs-10 col-sm-5'}
        self.fields['nickname'].widget.attrs = {'class': 'col-xs-10 col-sm-5'}
        self.fields['email'].widget.attrs = {'class': 'col-xs-10 col-sm-5'}
        self.fields['phone'].widget.attrs = {'class': 'col-xs-10 col-sm-5'}

    class Meta:
        model = AccountUser
        fields = ('username', 'nickname', 'email', 'phone', 'last_login', 'date_joined')


class ChangePasswordForm(PasswordChangeForm):
    """
    修改用户密码
    """
    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs = {'class': 'col-xs-10 col-sm-5'}
        self.fields['new_password1'].widget.attrs = {'class': 'col-xs-10 col-sm-5'}
        self.fields['new_password2'].widget.attrs = {'class': 'col-xs-10 col-sm-5'}

##############
# Supervisor #
##############


class SupervisorConfigForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SupervisorConfigForm, self).__init__(*args, **kwargs)
        self.fields['host'].widget.attrs = {'class': 'col-xs-10 col-sm-5'}
        self.fields['port'].widget.attrs = {'class': 'col-xs-10 col-sm-5'}
        self.fields['username'].widget.attrs = {
            'class': 'col-xs-10 col-sm-5', 'autocomplete': "off"}
        self.fields['password'].widget = forms.PasswordInput()
        self.fields['password'].widget.attrs = {
            'class': 'col-xs-10 col-sm-5', 'autocomplete': "off"}

    class Meta:
        model = SupervisorConfig
        exclude = ('id', 'create_time', 'owner')


###########
# Ansible #
###########


class AnsibleConfigForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AnsibleConfigForm, self).__init__(*args, **kwargs)
        self.fields['host'].widget.attrs = {'class': 'col-xs-10 col-sm-5'}
        self.fields['port'].widget.attrs = {'class': 'col-xs-10 col-sm-5'}
        self.fields['username'].widget.attrs = {
            'class': 'col-xs-10 col-sm-5', 'autocomplete': "off"}
        self.fields['password'].widget = forms.PasswordInput()
        self.fields['password'].widget.attrs = {
            'class': 'col-xs-10 col-sm-5', 'autocomplete': "off"}

    class Meta:
        model = AnsibleConfig
        exclude = ('id', 'create_time', 'owner')
