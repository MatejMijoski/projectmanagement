from django.urls import path
from TodoApp import views

urlpatterns = [
    path("<str:project_id>/task/", views.TaskListCreateView.as_view()),
    path("project/task/<str:id>", views.TaskRetrieveView.as_view()),
]