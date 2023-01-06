from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('transaction/limit', views.transaction_limit, name='limit'),
    path('transaction/market', views.transaction_market, name='market'),
    path('transaction/cancel', views.transaction_cancel, name='cancel'), 
    # path('withdraw', views.withdraw_request, name='cancel'),   

]


