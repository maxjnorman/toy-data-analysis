from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^$', views.table_list, name='table_list'),
    url(r'^table/(?P<pk>\d+)/$', views.table_detail, name='table_detail'),
    url(r'^table/create/$', views.create_table, name='create_table'),
    url(r'^table/(?P<pk>\d+)/edit/$', views.edit_table, name='edit_table'),
    url(r'^table/(?P<pk>\d+)/entry/$', views.input_table_entry, name='input_table_entry'),

    url(r'^$', views.account_list, name='account_list'),
    url(r'^account/(?P<pk>\d+)/$', views.account_detail, name='account_detail'),
    url(r'^account/create/$', views.account_create, name='account_create'),
    url(r'^account/(?P<pk>\d+)/edit/$', views.account_edit, name='account_edit'),
    url(r'^account/(?P<pk>\d+)/entry/$', views.transaction_input, name='transaction_input'),
]
