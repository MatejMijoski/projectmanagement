from django.urls import path

from LeadApp import views

urlpatterns = [
    path('lead/', views.LeadListCreateView.as_view()),
    path('lead/<str:id>', views.LeadRetrieveView.as_view()),

    path('<str:lead_id>/timeline/', views.TimelineItemListCreateView.as_view()),
    path('lead/timeline/<str:id>', views.TimelineItemRetrieveView.as_view()),
]