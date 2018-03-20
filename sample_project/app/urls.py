"""SaleDAC URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from django.conf.urls import include

from rest_framework.routers import DefaultRouter

import sample_project.app.views as SaleViews

router = DefaultRouter()
router.register(r'sale', SaleViews.SaleViewSet)
router.register(r'sale_item', SaleViews.SaleItemViewSet)
router.register(r'tender_type', SaleViews.TenderTypeViewSet)
router.register(r'tender', SaleViews.TenderViewSet)
router.register(r'sales_channel', SaleViews.SalesChannelViewSet)
router.register(r'store', SaleViews.StoreViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
