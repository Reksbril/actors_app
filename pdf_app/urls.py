from django.urls import path

from . import views

app_name = "pdf_app"
urlpatterns = [
    path("", views.index, name="index"),
    path("delete/<str:scenario_id_to_delete>/", views.index, name="delete_scenario"),
    path("<str:scenario_id>/", views.file_details, name="detail"),
    path(
        "<str:scenario_id>/<str:dialogue_element_id>/",
        views.get_dialogue_element_audio,
        name="get_audio",
    ),
]
