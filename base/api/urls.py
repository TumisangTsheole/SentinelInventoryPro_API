from django.urls import path
from . import views


urlpatterns = [
	path("category_list/", views.Category_List, name="category_list"),
	path("category_detail/<int:pk>", views.Category_Detail, name="category_detail")
]
