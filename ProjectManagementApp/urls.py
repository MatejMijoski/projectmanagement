from django.urls import path

from ProjectManagementApp import views

urlpatterns = [
    path("clients/", views.ClientListCreateView.as_view()),
    path("clients/<str:id>", views.ClientRetrieveView.as_view()),

    path("clients/<str:client_id>/timeline/", views.TimelineItemListCreateView.as_view()),
    path("clients/timeline/<str:id>", views.TimelineItemRetrieveView.as_view()),

    path("projects/", views.ProjectListCreateView.as_view()),
    path("projects/<str:id>", views.ProjectRetrieveView.as_view()),

    path("projects/<str:project_id>/posts/", views.ProjectPostsListCreateView.as_view()),
    path("projects/<str:project_id>/posts/<str:id>", views.ProjectPostsRetrieveView.as_view()),

    path("invites/<str:id>", views.ProjectInviteView.as_view()),

    path("posts/<str:post_id>/comments/", views.PostCommentListCreateView.as_view()),
    path("posts/<str:post_id>/comments/<str:id>", views.PostCommentsRetrieveView.as_view()),

    path('invoices/', views.InvoiceListCreateView.as_view()),
    path('invoices/<str:id>', views.InvoiceRetrieveView.as_view()),

    path('resume/', views.ResumeCreateView.as_view()),
]
