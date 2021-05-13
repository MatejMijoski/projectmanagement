from django.urls import path

from ProjectManagementApp import views

urlpatterns = [
    path("client/", views.ClientListCreateView.as_view()),
    path("client/<str:id>", views.ClientRetrieveView.as_view()),

    path("client/<str:client_id>/timeline/", views.TimelineItemListCreateView.as_view()),
    path("client/timeline/<str:id>", views.TimelineItemRetrieveView.as_view()),

    path("project/", views.ProjectListCreateView.as_view()),
    path("project/<str:id>", views.ProjectRetrieveView.as_view()),

    path("<str:project_id>/post/", views.ProjectPostsListCreateView.as_view()),
    path("<str:project_id>/post/<str:id>", views.ProjectPostsRetrieveView.as_view()),

    path("invite/<str:id>", views.ProjectInviteView.as_view()),

    path("<str:post_id>/comment/", views.PostCommentListCreateView.as_view()),
    path("<str:post_id>/comment/<str:id>", views.PostCommentsRetrieveView.as_view()),

    path('invoice/', views.InvoiceListCreateView.as_view()),
    path('invoice/<str:id>', views.InvoiceRetrieveView.as_view()),

    path('resume/', views.ResumeCreateView.as_view()),
]
