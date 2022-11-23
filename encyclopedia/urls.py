from django.urls import path

from . import views

urlpatterns = [
    path("wiki/", views.index, name="index"),
    path("wiki/search_results", views.search, name="search"),
    path("wiki/random_page", views.random_page, name="random_page"),
    path("wiki/new_page", views.new_page, name="new_page"),
    path("wiki/edit_page/<str:entry>", views.edit_page, name="edit_page"),
    path("wiki/not_found", views.not_found, name="not_found"),
    path("wiki/<str:title>", views.page, name="page")
]
