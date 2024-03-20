from django.urls import path
from . import views
from .views import schema_view

urlpatterns = [
    path('', views.HealthView.as_view(), name="Health-Check"),
    path('account', views.AccountView.as_view(), name="account-manager"),
    path('destination', views.DestinationView.as_view(), name="destination-manager"),
    path('data-handler', views.DataHandlerView.as_view(), name="data-handler"), # approach 1 : rest api data handler
    path('swagger/', schema_view.with_ui('swagger'), name='schema-swagger-ui'),
]
