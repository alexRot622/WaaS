from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
urlpatterns = router.urls
urlpatterns = [
    path('verify/', VerifyView.as_view(), name='verify_view'),
    path('balance/', BalanceView.as_view(), name='balance_view'),
    path("transfer/", TransferView.as_view(), name="transfer"),
    path("create/", CreateView.as_view(), name="create"),
    path("mint/", MintView.as_view(), name="mint"),
    path("history/", HistoryView.as_view(), name="history"),
    path(r'', include(router.urls)),
]