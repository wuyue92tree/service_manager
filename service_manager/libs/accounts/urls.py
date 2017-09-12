"""antio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),

    # auth
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^forgot/$', ForgotView.as_view(), name='forgot'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^profile/(?P<slug>.*)/$', ProfileView.as_view(), name='profile'),
    url(r'^change_password/$', ChangePasswordView.as_view(), name='change_password'),

    # supervisor
    url(r'supervisor/$', SupervisorIndexView.as_view(),
        name='supervisor'),
    url(r'supervisor/host/index/$', SupervisorHostIndexView.as_view(),
        name='supervisor-host-index'),
    url(r'supervisor/host/add/$', SupervisorHostAddView.as_view(),
        name='supervisor-host-add'),
    url(r'supervisor/host/(?P<pk>.*)/delete/$',
        SupervisorHostDeleteView.as_view(),
        name='supervisor-host-delete'),
    url(r'supervisor/host/(?P<pk>.*)/change/$',
        SupervisorHostChangeView.as_view(),
        name='supervisor-host-change'),
    url(r'supervisor/service/(?P<pk>.*)/status_check/$',
        SupervisorServiceStatusCheck.as_view(),
        name='supervisor-service-status-check'),
    url(r'supervisor/service/(?P<pk>.*)/status/$',
        SupervisorServiceStatus.as_view(),
        name='supervisor-service-status'),
    url(r'supervisor/service/(?P<pk>.*)/start/$',
        SupervisorServiceStart.as_view(),
        name='supervisor-service-start'),
    url(r'supervisor/service/(?P<pk>.*)/stop/$',
        SupervisorServiceStop.as_view(),
        name='supervisor-service-stop'),
    url(r'supervisor/service/(?P<pk>.*)/restart/$',
        SupervisorServiceRestart.as_view(),
        name='supervisor-service-restart'),
    url(r'supervisor/service/(?P<pk>.*)/restart_all/$',
        SupervisorServiceRestartAll.as_view(),
        name='supervisor-service-restart-all'),
    url(r'supervisor/service/(?P<pk>.*)/stop_all/$',
        SupervisorServiceStopAll.as_view(),
        name='supervisor-service-stop-all'),
    url(r'supervisor/service/(?P<pk>.*)/clearlog/$',
        SupervisorServiceClearLog.as_view(),
        name='supervisor-service-clearlog'),
    url(r'supervisor/service/(?P<pk>.*)/tail/$',
        SupervisorServiceTail.as_view(),
        name='supervisor-service-tail'),
    url(r'supervisor/service/(?P<pk>.*)/tail_f/$',
        SupervisorServiceTailF.as_view(),
        name='supervisor-service-tail-f'),
]
