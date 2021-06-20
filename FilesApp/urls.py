from django.urls import path

from FilesApp import views

urlpatterns = [
    path("file/", views.FileProjectListView.as_view()),
    path("file/<str:id>", views.FileRetrieveView.as_view()),
    path("file_download/<str:id>", views.FileDownloadView.as_view()),
    path("<str:project_id>/files/", views.FileListCreateView.as_view()),
]
