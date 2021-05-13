"""projectmanagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URL conf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from ProjectManagementApp import urls as project_management_urls
from AuthenticationApp import urls as auth_urls
from SlackApp import urls as slack_urls
from FilesApp import urls as file_urls
from TodoApp import urls as todo_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include(auth_urls)),
    path("api/", include(project_management_urls)),
    path("api/", include(file_urls)),
    path("api/", include(slack_urls)),
    path("api/", include(todo_urls))
]
