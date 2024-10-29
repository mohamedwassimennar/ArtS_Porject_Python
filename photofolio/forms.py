from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ArtImages, Artist, Reservation, Exposition, ArtGallery, PlannedVisit, Avis, Catalogue, CulturalEvent, CulturalWorkshop
from django.utils import timezone

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'name': 'type', 'class': 'form-username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-password1'})
        }

photo_choices = (('nature', 'nature'), ('adventure', 'adventure'),
                 ('people', 'people'), ('travel', 'travel'))

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ImageForm(forms.ModelForm):
    photo = MultipleFileField(label='Select files', required=False)

    class Meta:
        model = ArtImages
        fields = ['photo']

class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ['contenu', 'note', 'type_avis', 'galerie', 'exposition']
        widgets = {
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter review content here...',
                'required': True,
            }),
            'note': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rating between 1 and 5',
                'min': 1,
                'max': 5,
                'required': True,
            }),
            'type_avis': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            }),
        }

class CatalogueForm(forms.ModelForm):
    class Meta:
        model = Catalogue
        fields = ['titre', 'description', 'type_catalogue']

    def clean(self):
        cleaned_data = super().clean()
        titre = cleaned_data.get('titre')
        description = cleaned_data.get('description')
        type_catalogue = cleaned_data.get('type_catalogue')

        if not titre:
            self.add_error('titre', 'Ce champ est obligatoire.')
        if not description:
            self.add_error('description', 'Ce champ est obligatoire.')
        if not type_catalogue:
            self.add_error('type_catalogue', 'Sélectionnez un type de catalogue.')

class FormReservation(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['exposition', 'date', 'entry_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'entry_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class ArtGalleryForm(forms.ModelForm):
    class Meta:
        model = ArtGallery
        fields = ['nom', 'image', 'adresse', 'description', 'heures_ouverture', 'heures_fermeture', 'expositions']
        widgets = {
            'heures_ouverture': forms.TimeInput(attrs={'type': 'time'}),
            'heures_fermeture': forms.TimeInput(attrs={'type': 'time'}),
            'expositions': forms.CheckboxSelectMultiple()
        }

class PlannedVisitForm(forms.ModelForm):
    class Meta:
        model = PlannedVisit
        fields = ['nom', 'date_visite', 'galleries_a_visiter', 'duree_estimee', 'statut_visite']
        widgets = {
            'date_visite': forms.DateInput(attrs={'type': 'date'}),
            'duree_estimee': forms.NumberInput(attrs={'type': 'number', 'min': '0.5', 'max': '12', 'step': '0.5'}),
            'galleries_a_visiter': forms.CheckboxSelectMultiple()
        }
# Formulaire pour CulturalEvent
class CulturalEventForm(forms.ModelForm):
    class Meta:
        model = CulturalEvent
        fields = ['event_name', 'description', 'start_date', 'end_date', 'location']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter event description...', 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'placeholder': 'Enter location...', 'class': 'form-control'}),
        }
class WorkshopForm(forms.ModelForm):
    class Meta:
        model = CulturalWorkshop
        fields = ['name', 'description', 'date', 'start_time',  'duration', 'participant_limit']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'duration': forms.TimeInput(attrs={'type': 'time'}),
        }

class ArtImagesForm(forms.ModelForm):
    class Meta:
        model = ArtImages
        fields = ['name', 'type', 'year', 'description', 'art_image', 'artist']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    art_image = MultipleFileField(label='Select files', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        type_choices = ArtImages.objects.values_list('type', 'type').distinct()
        self.fields['type'] = forms.ChoiceField(
            choices=type_choices,
            label="Art Type",
            required=True
        )

        self.fields['artist'] = forms.ModelChoiceField(
            queryset=Artist.objects.all(),
            label="Artist",
            empty_label="Select an artist",
            required=True
        )
