from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^api/v1/register/$', views.RegisterView.as_view(), name='register'),
    url(r'^api/v1/auth/$', views.AuthView.as_view(), name='auth'),
    url(r'api/v1/user/$',views.UserView.as_view(),name='user'),
    url(r'^api/v1/lesson/$',views.LessonView.as_view(),name='lesson'),
    url(r'^api/v1/post/$',views.PostView.as_view(),name='post'),
    url(r'^api/v1/message/$',views.MessageView.as_view(),name='message')

]

