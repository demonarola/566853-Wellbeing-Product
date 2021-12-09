"""wellbeing_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include
from wellbeingapp.views import *
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf.urls import handler403, handler500, handler404
from customers.views import error_403, error_500
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path("login/", EmailLoginView.as_view(title="Team member sign in",notes=''), name="login"),
    path(
        "logout/",
        TeamAdminLogout.as_view(),
        {"next_page": "login"},
        name="logout",
    ),
    path('', include('django.contrib.auth.urls')),
    path("registration/<uuid:random_url>/", TeamAdminRegistrationView.as_view(), name="team-admin-registration"),
    path("wellbeing_pledge/", WellbeingPledgeView.as_view(), name="wellbeing_pledge"),
    # path("wellbeing_pledge/<int:id>/", PledgeUpdateView.as_view(), name="updatedata"),
    path("wellbeing/", include("wellbeingapp.urls"), name="wellbeing"),
    path("edit_wellbeing_pledge/<int:pk>", EditWellbeingPledgeView.as_view(), name="edit_wellbeing_pledge"),
    path("pledge_comment/", PledgeCommentView.as_view(), name="pledge_comment"),
    path("edit_comment/<int:pk>", EditPledgeCommentView.as_view(), name="edit_comment"),
    path("delete_pledge_comment/<int:id>", DeletePledgeCommentView.as_view(), name="delete_pledge_comment"),
    path("proud/", ProudView.as_view(), name="proud"),
    path("edit_proud/<int:pk>", EditProudView.as_view(), name="edit_proud"),
    path("delete_proud/<int:id>", DeleteProudView.as_view(), name="delete_proud"),
    path("user_pledge/", UserPledgeView.as_view(), name="user_pledge"),
    path("profile/",ProfileView.as_view(),name="client-profile"),


    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler403 = error_403
handler404 = error_403
handler500 = error_500

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
