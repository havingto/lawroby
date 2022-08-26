from django.urls import path

from . import views

app_name = 'employment'

urlpatterns = [
    path('', views.intro, name='intro'),
    path('interview/', views.interview, name='interview'),
    path('create_output/', views.create_output, name='create_output'),
    path('other_issue/', views.other_issue, name='other_issue'),
    path('feedback/', views.feedback, name='feedback')
]
