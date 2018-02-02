from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from prod_stat import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'shop/<int:shop_id>', views.market),
    path('', views.main),
    path('login/', views.vlogin),
    path('logout/', views.vlogout, name='Logout'),
]
