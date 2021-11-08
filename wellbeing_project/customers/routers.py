from rest_framework.routers import DefaultRouter
from customers import views

# Create a router and register our viewsets with it.
tenant_router = DefaultRouter()
tenant_router.register(r'tenant', views.CreateTenantView)
