from django.urls import path
from . import views
from .views import (
    redirect_to_streamlit,
    reserve,
    add_reservation,
    add_gallery,
    art_gallery_detail,
    like_painting,
    gallery_list,
    add_visit,
    visit_list,
    edit_art_gallery,
    delete_art_gallery,
    edit_planned_visit,
    delete_planned_visit,liste_avis, creer_avis, mettre_a_jour_avis, supprimer_avis,liste_catalogues,mettre_a_jour_catalogue,creer_catalogue,supprimer_catalogue,ia_view
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),  # URL racine
    path('home', views.home, name="home"),
    path('about', views.about, name="about"),
    path('contact', views.contact, name="contact"),
    path('services', views.services, name="services"),
    path('login', views.login_user_or_admin, name="login"),
    path('upload', views.upload, name="upload"),
    path('register', views.register, name='register'),
    path('gallery/<str:pk>', views.gallery, name='gallery'),
    path('gallery/detail/<int:pk>/', art_gallery_detail, name='art_gallery_detail'),
    path('like/', like_painting, name='like_painting'),
    path('get-liked-paintings/', views.get_liked_paintings, name='get_liked_paintings'),
    path('suggest-art/', views.suggest_art, name='suggest_art'),
    path('delete-artimage/<int:image_id>/', views.delete_artimage_view, name='delete_artimage'),
    path('galleryinner', views.galleryinner, name='galleryinner'),
    path('logout', views.logout_user_or_admin, name='logout'),
    path('expositions', views.expositions, name='expositions'),  # New URL for expositions
    path('reservations', views.reservations, name='reservations'),  # New URL for reservations
    path('reserve/<int:reservation_id>/', reserve, name='reserve'),
    path('add-reservation/', add_reservation, name='add_reservation'),  # Add reservation
    path('add-gallery/', add_gallery, name='add_gallery'),  # Add new art gallery
    path('gallery-list/', gallery_list, name='gallery_list'),  # List of art galleries
    path('add-visit/', add_visit, name='add_visit'),  # Plan a new visit
    path('visit-list/', visit_list, name='visit_list'),  # List of planned visits
    path('edit-gallery/<int:pk>/', edit_art_gallery, name='edit_art_gallery'),  # Edit art gallery
    path('delete-gallery/<int:pk>/', delete_art_gallery, name='delete_art_gallery'),  # Delete art gallery
    path('edit-visit/<int:pk>/', edit_planned_visit, name='edit_planned_visit'),  # Edit planned visit
    path('delete-visit/<int:pk>/', delete_planned_visit, name='delete_planned_visit'),  # Delete planned visit
    path('streamlit/', redirect_to_streamlit, name='streamlit'),  # Redirect route
     path('avis/', liste_avis, name='liste_avis'),
    path('avis/creer/', creer_avis, name='creer_avis'),
    path('avis/mettre-a-jour/<int:avis_id>/', mettre_a_jour_avis, name='mettre_a_jour_avis'),
    path('avis/supprimer/<int:avis_id>/', supprimer_avis, name='supprimer_avis'),
    path('catalogues/', views.liste_catalogues, name='liste_catalogues'), 
    path('catalogues/modifier/<int:catalogue_id>/', views.mettre_a_jour_catalogue, name='modifier_catalogue'),
    path('catalogues/creer/', views.creer_catalogue, name='creer_catalogue'),
    path('catalogues/supprimer/<int:catalogue_id>/', views.supprimer_catalogue, name='supprimer_catalogue'), 
    path('ia/', views.ia_view, name='ia'),
    path('ia2/', views.ia_view2, name='ia2'),
path('cultural-events/', views.cultural_event_list, name='cultural_event_list'),  # Lister les événements culturels
 path('events/<int:event_id>/workshops/add/', views.add_workshop, name='add_workshop'),  # Ajouter un nouvel atelier
 path('event/<int:event_id>/generate_workshop_program/', views.generate_workshop_program, name='generate_workshop_program'),
    path('event/<int:event_id>/workshop/<int:workshop_id>/program/', views.view_workshop_program, name='view_workshop_program'),
    path('event/<int:event_id>/workshops/', views.view_workshops, name='view_workshops'),  
  path('event/<int:event_id>/workshop/<int:workshop_id>/', views.view_workshop, name='view_workshop'),
    path('event/<int:event_id>/workshops/edit/<int:workshop_id>/', views.edit_workshop, name='edit_workshop'),  # Ajout de la route pour modifier
    path('event/<int:event_id>/workshops/delete/<int:workshop_id>/', views.delete_workshop, name='delete_workshop'),  # Ajout de la route pour supprimer
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
