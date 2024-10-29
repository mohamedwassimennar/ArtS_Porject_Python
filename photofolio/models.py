from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class User(AbstractUser):
    is_admin = models.BooleanField('Is admin', default=False)
    liked_paintings = models.ManyToManyField('ArtImages', related_name='liked_by_users', blank=True)

    def __str__(self):
        return self.username


class Galerie(models.Model):
    nom = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.nom  # Retourne le nom de la galerie


# Exposition model
class Exposition(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()  # Date de début
    end_date = models.DateField()    # Date de fin
    attendees = models.ManyToManyField(User, through='Reservation', related_name='expositions')

    def __str__(self):
        return self.nom

class Avis(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    contenu = models.TextField()
    note = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Note de 1 à 5
    date = models.DateTimeField(auto_now_add=True, editable=False)
    galerie = models.ForeignKey(Galerie, on_delete=models.CASCADE, null=True, blank=True)
    exposition = models.ForeignKey(Exposition, on_delete=models.CASCADE, null=True, blank=True)

    # Nouveau champ pour spécifier le type d'avis
    TYPE_OPTIONS = (
        ('galerie', 'Galerie'),
        ('exposition', 'Exposition'),
        ('les_deux', 'Les deux'),
    )
    
    type_avis = models.CharField(max_length=20, choices=TYPE_OPTIONS, default='galerie')

    def __str__(self):
        return f'Avis de {self.utilisateur} sur {self.galerie or self.exposition}'

class Catalogue(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    galerie = models.ForeignKey(Galerie, on_delete=models.CASCADE, null=True, blank=True)
    exposition = models.ForeignKey(Exposition, on_delete=models.CASCADE, null=True, blank=True)   
    TYPE_OPTIONS = (
    ('galerie', 'Galerie'),
    ('exposition', 'Exposition'),
    ('les_deux', 'Les deux'),
)
    type_catalogue = models.CharField(max_length=20, choices=TYPE_OPTIONS, default='galerie')
    def __str__(self):
        return f'Avis de {self.utilisateur} sur {self.galerie or self.exposition}'




# Reservation model
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exposition = models.ForeignKey(Exposition, on_delete=models.CASCADE)
    date = models.DateField()  # Date of reservation
    entry_time = models.TimeField()  # Heure d'entrée
    STATUS_CHOICES = (
        ('valid', 'Valide'),
        ('cancelled', 'Annulé'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Reserved')

    def __str__(self):
        return f"Reservation for {self.exposition.nom} by {self.user.username}"



class Artist(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class ArtImages(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    year = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    art_image = models.ImageField(upload_to='art_images/')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='art_images')

    def __str__(self):
        return f"{self.name} by {self.artist.name}"









class ArtGallery(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Gallery Name")
    image = models.ImageField(upload_to='galleries/', blank=True, null=True)
    adresse = models.CharField(max_length=255, verbose_name="Address")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    heures_ouverture = models.TimeField(verbose_name="Opening Hours")
    heures_fermeture = models.TimeField(verbose_name="Closing Hours")
    expositions = models.ManyToManyField(Exposition, related_name='galleries', blank=True, verbose_name="Expositions")  # Nouveau champ

    def __str__(self):
        return self.nom


class PlannedVisit(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Visit Name")
    date_visite = models.DateField(verbose_name="Visit Date")
    galleries_a_visiter = models.ManyToManyField(ArtGallery, related_name='planned_visits', verbose_name="List of Galleries to Visit")
    duree_estimee = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="Estimated Duration (hours)")
    STATUT_VISITE_CHOICES = [
        ('planned', 'Planned'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ]
    statut_visite = models.CharField(max_length=10, choices=STATUT_VISITE_CHOICES, default='planned', verbose_name="Visit Status")

    def __str__(self):
        return f"{self.nom} on {self.date_visite}"
    
    # CulturalEvent model
class CulturalEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('concert', 'Concert'),
        ('exhibition', 'Exhibition'),
        ('festival', 'Festival'),
        ('theater', 'Theater'),
      
    ]

    event_name = models.CharField(max_length=255, verbose_name="Event Name")
    description = models.TextField(verbose_name="Description")
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")
    location = models.CharField(max_length=255, verbose_name="Location")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, verbose_name="Event Type")

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError('La date de début doit être antérieure à la date de fin.')

    def save(self, *args, **kwargs):
        self.clean()  # Appelle la méthode de validation avant de sauvegarder
        super().save(*args, **kwargs)

    def __str__(self):
        return self.event_name
class CulturalWorkshop(models.Model):
    name = models.CharField(max_length=200)  # Nom de l'atelier
    description = models.TextField()  # Description détaillée de l'atelier
    date = models.DateField()  # Date de l'atelier
    start_time = models.TimeField()  # Heure de début de l'atelier
   
    duration = models.DurationField()  # Durée de l'atelier
    participant_limit = models.PositiveIntegerField()  # Limite de participants
    cultural_event = models.ForeignKey(CulturalEvent, on_delete=models.CASCADE, related_name='workshops', null=True, blank=True)
    program = models.TextField(blank=True, null=True) 
    def __str__(self):
        return self.name
    def update_program(self, new_program):
        self.program = new_program  # Met à jour le programme
        self.save()  # Sauvegarde l'atelier avec le nouveau programme