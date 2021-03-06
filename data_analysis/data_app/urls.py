from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.account_list, name='account_list'),
    url(r'^account/create/$', views.account_create, name='account_create'),
    url(r'^account/(?P<pk>\d+)/detail/$', views.account_detail, name='account_detail'),
    url(r'^account/(?P<pk>\d+)/edit/$', views.account_edit, name='account_edit'),
    url(r'^account/(?P<pk>\d+)/delete/$', views.account_delete, name='account_delete'),
    url(r'^year/(?P<pk>\d+)/detail/$', views.year_detail, name='year_detail'),
    url(r'^month/(?P<pk>\d+)/detail/$', views.month_detail, name='month_detail'),
    url(r'^account/(?P<pk>\d+)/transaction/input/$', views.transaction_input_account, name='transaction_input_account'),
    url(r'^year/(?P<pk>\d+)/transaction/input/$', views.transaction_input_year, name='transaction_input_year'),
    url(r'^month/(?P<pk>\d+)/transaction/input/$', views.transaction_input_month, name='transaction_input_month'),
    url(r'^transaction/(?P<pk>\d+)/edit/$', views.transaction_edit, name='transaction_edit'),
    url(r'^transaction/(?P<pk>\d+)/delete/$', views.transaction_delete, name='transaction_delete'),
]
