"""
URL configuration for setup project.

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
from django.urls import path
from home import views

"""

Nessa parte aqui eu to importando dos meus próprios arquivos de views 
(oq estou desenvolvendo para ser uma das páginas) para conseguir carregar em uma das urls

"""

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home_view, name="home"),
    path("project/<int:project_id>/", views.project_view, name="project"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
