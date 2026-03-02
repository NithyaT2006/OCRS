"""
URL configuration for onlinecomplaint project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from .views import index 
from .views import register
from .views import adminlogin
from .views import admindashboard
from .views import forgotpassword
from .views import userlogin
from django.conf import settings
from django.conf.urls.static import static
from .views import complaintportal
from .views import verifyotp
from .views import resetpassword
from .views import edit_profile
from .views import userlogout
from .views import submit_complaint
from .views import delete_complaint
from .views import edit_complaint
from .views import complaint_status
from .views import admin_edit_complaint
from .views import admin_edit_user
from .views import admin_edit_profile
from .views import admin_delete_user
from .views import admin_delete_complaint
from .views import adminlogout


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',index , name='index'),
    path('register/',register,name='register'),
    path('adminlogin/',adminlogin,name='adminlogin'),
    path('admindashboard/',admindashboard,name='admindashboard'),    
    path('adminpanel/complaint/edit/<int:id>/',admin_edit_complaint, name='admin_edit_complaint'),
    path('adminpanel/complaint/delete/<int:id>/',admin_delete_complaint, name='admin_delete_complaint'),
    path('adminpanel/user/edit/<int:id>/',admin_edit_user, name='admin_edit_user'),
    path('adminpanel/user/delete/<int:id>/',admin_delete_user, name='admin_delete_user'),
    path('adminpanel/edit-profile/',admin_edit_profile, name='admin_edit_profile'),  
    path('complaintportal/' ,complaintportal, name='complaintportal'),
    path('adminlogout/',adminlogout, name='adminlogout'), 
    path('userlogin/', userlogin, name='userlogin'),  
    path('forgotpassword/',forgotpassword, name='forgotpassword'),
    path('verifyotp/',verifyotp, name='verifyotp'),
    path('resetpassword/',resetpassword, name='resetpassword'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('logout/', userlogout, name='userlogout'),
    path('submit_complaint/', submit_complaint, name='submit_complaint'),
    path('complaint/edit/<int:id>/', edit_complaint, name='edit_complaint'),
    path('complaint/delete/<int:id>/', delete_complaint, name='delete_complaint'),
    path('complaint/status/<int:id>/', complaint_status, name='complaint_status')




]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
