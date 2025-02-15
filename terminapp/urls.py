"""
URL configuration for terminapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # admin.domain.com / admin_restrict
    path('admin/', admin.site.urls),

    # главная страница domain.com - использует hero app middlewere
    path('', include('hero.urls')),

    path('orders/', include('orders.urls', namespace='orders')),

    # API-эндпоинты (например, под /api/...)
    path('api/account/', include('account.urls')),
    path('api/clients/', include('clients.urls')),
    path('api/hr/', include('hr.urls')),

    path('api/products/', include('products.urls')),
    path('api/cashflow/', include('cashflow.urls')),
    path('api/analytics/', include('analytics.urls')),

]