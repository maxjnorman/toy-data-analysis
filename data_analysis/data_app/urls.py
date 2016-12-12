from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.account_list, name='account_list'),
    url(r'^account/(?P<pk>\d+)/$', views.account_detail, name='account_detail'),
    url(r'^account/create/$', views.account_create, name='account_create'),
    url(r'^account/(?P<pk>\d+)/edit/$', views.account_edit, name='account_edit'),
    url(r'^account/(?P<pk>\d+)/transaction/entry/$', views.transaction_input, name='transaction_input'),
    url(r'^account/(?P<pk>\d+)/transaction/edit/$', views.transaction_edit, name='transaction_edit'),
    url(r'^account/(?P<pk>\d+)/transaction/delete/$', views.transaction_delete, name='transaction_delete'),
]
