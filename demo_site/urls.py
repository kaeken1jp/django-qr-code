"""qr_code_demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls import url, include
from django.views.generic import RedirectView
from qr_code_demo import urls as qr_code_demo_urls
from qr_code import urls as qr_code_urls

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='qr_code_demo/', permanent=True)),
    url(r'^qr_code_demo/', include(qr_code_demo_urls, namespace='qr_code_demo')),
    url(r'^qr_code/', include(qr_code_urls, namespace='qr_code')),
]
