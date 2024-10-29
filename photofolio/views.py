from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from .forms import RegisterForm, ArtImages  , FormReservation, ArtGalleryForm, PlannedVisitForm ,WorkshopForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import User, ArtImages
from .models import Avis
from .forms import AvisForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Catalogue
from .forms import CatalogueForm
from .models import User, ArtImages, Exposition, Reservation, ArtGallery, PlannedVisit, CulturalEvent,CulturalWorkshop
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseRedirect 
import subprocess
import json
import google.generativeai as genai
import os
from .forms import ArtImagesForm
# Create your views here.

# login decorator to restrict users
genai.configure(api_key=os.getenv("GOOGLE_API_KEY_2"))
@login_required(login_url="login")


def home(request):
    data_from_db=ArtImages.objects.all()
    return render(request, 'index.html', {'images': data_from_db})


def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        try:
            send_mail(subject, message, email, ['said.atoui@esprit.tn'])
            return render(request, 'contact.html', {'message_name': name})
        except Exception as e:
            return render(request, 'contact.html', {'error': str(e)})
    return render(request, 'contact.html')


def services(request):
    return render(request, 'services.html')


def gallery(request, pk):
    print(pk)
    images_in_db=ArtImages.objects.filter(type=pk).all()
    print(images_in_db)
    count=ArtImages.objects.filter(type=str(pk)).count()

    return render(request, 'gallery.html', {'images':images_in_db, 'count': count, 'type': pk})

def art_gallery_detail(request, pk):
    image = get_object_or_404(ArtImages.objects.select_related('artist'), pk=pk)
    other_images = ArtImages.objects.filter(artist=image.artist).exclude(id=image.id).select_related('artist')

    return render(request, 'art_gallery_detail.html', {
        'image': image,
        'other_images': other_images,
    })

@login_required
def like_painting(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        painting_name = data.get('painting_name')

        user_profile = User.objects.get(username=request.user.username)

        print(painting_name)
        painting = get_object_or_404(ArtImages, name=painting_name)

        if painting_name and painting_name not in user_profile.liked_paintings.values_list('id', flat=True):
            user_profile.liked_paintings.add(painting)
            user_profile.save()
            return JsonResponse({'success': True, 'likedpaintings': list(user_profile.liked_paintings.values_list('name', flat=True))})
        return JsonResponse({'success': False, 'message': 'Already liked or invalid painting name.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@login_required
def get_liked_paintings(request):
    user_profile = User.objects.get(username=request.user.username)
    return JsonResponse({'success': True, 'likedpaintings': list(user_profile.liked_paintings.values_list('name', flat=True))})

def suggest_art(request):
    user = request.user

    liked_paintings = list(user.liked_paintings.all())
    if liked_paintings:
        liked_titles = ", ".join([painting.name for painting in liked_paintings])
        ai_prompt = f"Suggest 3 paintings similar to these: {liked_titles}. be very short and concise. start like this 1. 2. 3."
    else:
        suggestion = ArtImages.objects.order_by('?').first()
        if not suggestion:
            return JsonResponse({"error": "No suggestions available"}, status=404)
        ai_prompt = f"Suggest some paintings similar to {suggestion.name} by {suggestion.artist}."

    curl_command = [
        "curl",
        "-H", "Content-Type: application/json",
        "-d", f'{{"contents":[{{"parts":[{{"text":"{ai_prompt}"}}]}}]}}',
        "-X", "POST",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=AIzaSyDbtHCFPas7PN42C-kcRFGYMUWqMM3tDN8"
    ]

    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        response_json = json.loads(result.stdout)
        print(response_json)
        
        suggestion_text = response_json['candidates'][0]['content']['parts'][0]['text']

        suggestions_list = suggestion_text.split(",") 
        formatted_suggestions = "\n".join([s.strip() for s in suggestions_list])

    except subprocess.CalledProcessError as e:
        return JsonResponse({"error": f"Error executing cURL command: {e.stderr}"}, status=500)
    except (KeyError, IndexError, json.JSONDecodeError):
        return JsonResponse({"error": "Unexpected response format from AI"}, status=500)

    return JsonResponse({"suggestions": formatted_suggestions})


def galleryinner(request):
    return render(request, 'gallery-single.html')

def login_user_or_admin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_admin:
                return redirect('upload')
            return redirect('home')
        else:
            messages.info(request, 'Username or password is incorrect')
            return redirect('login')
    else:
        return render(request, 'login1.html')



def logout_user_or_admin(request):
    logout(request)
    return redirect('home')


@login_required(login_url='login')
def upload(request):
    user_profile = User.objects.get(username=request.user.username)
    liked_paintings = user_profile.liked_paintings.all()

    if request.method == "POST":
        form = ArtImagesForm(request.POST, request.FILES)
        
        if form.is_valid():
            artist = form.cleaned_data['artist']
            type = form.cleaned_data['type']
            name = form.cleaned_data['name']
            year = form.cleaned_data.get('year', None)
            description = form.cleaned_data.get('description', "")
            images = request.FILES.getlist('art_image')
            
            for instance in images:
                data = ArtImages(
                    name=name,
                    type=type,
                    year=year,
                    description=description,
                    art_image=instance,
                    artist=artist
                )
                data.save()
                
                request.user.liked_paintings.add(data)
            
            return redirect('home')
        else:
            messages.info(request, "Form is not valid")
            return redirect('upload')
    else:
        form = ArtImagesForm()
    

    return render(request, 'upload.html', {
        'form': form,
        'liked_paintings': liked_paintings
    })



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Registration failed. Please check the form for errors.')
    else:
        form = RegisterForm()
    return render(request, 'user_registration.html', {'form': form})


def upload_images(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_images = request.FILES.getlist('photo')
            for image in uploaded_images:
                image_instance = Image(photo=image)
                image_instance.save()
    else:
        form = ImageForm()

    return render(request, 'your_template.html', {'form': form})

@login_required(login_url='login')
def liste_avis(request):
    avis_utilisateur = Avis.objects.filter(utilisateur=request.user)

    query = request.GET.get('search', '')

    if query:
        avis_utilisateur = avis_utilisateur.filter(type_avis__icontains=query)

    paginator = Paginator(avis_utilisateur, 6)  
    page_number = request.GET.get('page')
    avis = paginator.get_page(page_number)

    return render(request, 'liste_avis.html', {'avis': avis, 'query': query})




@login_required(login_url='login')
def creer_avis(request):
    if request.method == 'POST':
        form = AvisForm(request.POST)
        if form.is_valid():
            avis = form.save(commit=False)
            avis.utilisateur = request.user 
            avis.save()  
            return redirect('liste_avis')  
    else:
        form = AvisForm()  
    return render(request, 'creer_avis.html', {'form': form})  


@login_required(login_url='login')
def mettre_a_jour_avis(request, avis_id):
    avis = get_object_or_404(Avis, id=avis_id)  
    
    if request.method == 'POST':
        form = AvisForm(request.POST, instance=avis) 
        if form.is_valid():
            form.save()  
            messages.success(request, "L'avis a été mis à jour avec succès.")
            return redirect('liste_avis') 
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = AvisForm(instance=avis) 

    context = {
        'form': form,
        'avis': avis,  
    }
    return render(request, 'mettre_a_jour_avis.html', context)



@login_required(login_url='login')
def supprimer_avis(request, avis_id):
    avis = get_object_or_404(Avis, id=avis_id)
    if request.method == 'POST':
        avis.delete()  
        return redirect('liste_avis')  
    return render(request, 'supprimer_avis.html', {'avis': avis})  

@login_required(login_url='login')
def liste_catalogues(request):
    catalogues_utilisateur = Catalogue.objects.filter(utilisateur=request.user)

    query = request.GET.get('search', '')

    if query:
        catalogues_utilisateur = catalogues_utilisateur.filter(titre__icontains=query)

    paginator = Paginator(catalogues_utilisateur, 6)  
    page_number = request.GET.get('page')
    catalogues = paginator.get_page(page_number)

    return render(request, 'liste_catalogues.html', {'catalogues': catalogues, 'query': query})


@login_required(login_url='login')
def creer_catalogue(request):
    if request.method == 'POST':
        form = CatalogueForm(request.POST)
        if form.is_valid():
            catalogue = form.save(commit=False)
            catalogue.utilisateur = request.user
            catalogue.save()
            form.save_m2m()  # Sauvegarde les relations ManyToMany
            return redirect('liste_catalogues')
    else:
        form = CatalogueForm()

    return render(request, 'creer_catalogue.html', {'form': form})


@login_required(login_url='login')
def mettre_a_jour_catalogue(request, catalogue_id):
    catalogue = get_object_or_404(Catalogue, id=catalogue_id)

    if request.method == 'POST':
        form = CatalogueForm(request.POST, instance=catalogue)
        if form.is_valid():
            form.save()
            messages.success(request, "Le catalogue a été mis à jour avec succès.")
            return redirect('liste_catalogues') 
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = CatalogueForm(instance=catalogue)

    context = {
        'form': form,
        'catalogue': catalogue,  
    }
    return render(request, 'mettre_a_jour_catalogue.html', context)


@login_required(login_url='login')
def supprimer_catalogue(request, catalogue_id):
    catalogue = get_object_or_404(Catalogue, id=catalogue_id)
    if request.method == 'GET':
        catalogue.delete()
        return redirect('liste_catalogues')  
    
def ia_view(request):
    return render(request, 'ia.html')

def ia_view2(request):
    return render(request, 'ia2.html')


def expositions(request):
    all_expositions = Exposition.objects.all()  # Get all expositions from the database
    return render(request, 'expositions.html', {'expositions': all_expositions})

@login_required(login_url='login')
def reservations(request):
    # Get the reservations for the authenticated user
    user_reservations = Reservation.objects.filter(user=request.user)  # Filter by the logged-in user
    return render(request, 'reservations.html', {'reservations': user_reservations})

def reserve(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    # Logic to handle reservation (e.g., change status, etc.)
    reservation.status = 'Cancel'  # Example logic; adjust based on your needs
    reservation.save()
    
    return redirect('reservations')  # Redirect back to the reservations page

@login_required  # Ensure only logged-in users can access this view
def add_reservation(request):
    if request.method == 'POST':
        form = FormReservation(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)  # Don't save to the database yet
            reservation.user = request.user  # Set the user field to the current user
            reservation.save()  # Now save the reservation
            messages.success(request, 'Reservation added successfully!')
            return redirect('reservations')  # Redirect to your reservations page
    else:
        # Create a form instance and set the user to the currently logged-in user
        form = FormReservation(initial={'user': request.user})

    return render(request, 'reservations.html', {'form': form})

def add_gallery(request):
    if request.method == 'POST':
        form = ArtGalleryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gallery_list')
    else:
        form = ArtGalleryForm()
    return render(request, 'add_gallery.html', {'form': form})

def gallery_list(request):
    galleries = ArtGallery.objects.all()
    return render(request, 'gallery_list.html', {'galleries': galleries})

def gallery_view(request):
    galleries = ArtGallery.objects.all()  # Récupérer toutes les galeries
    return render(request, 'your_template.html', {'galleries': galleries})

def add_visit(request):
    if request.method == 'POST':
        form = PlannedVisitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('visit_list')
    else:
        form = PlannedVisitForm()
    return render(request, 'add_visit.html', {'form': form})


def visit_list(request):
    visits = PlannedVisit.objects.prefetch_related('galleries_a_visiter').all()  # Récupérer toutes les visites planifiées avec les galeries associées
    return render(request, 'visit_list.html', {'visits': visits})

# Edit ArtGallery
def edit_art_gallery(request, pk):
    gallery = get_object_or_404(ArtGallery, pk=pk)
    if request.method == "POST":
        form = ArtGalleryForm(request.POST, request.FILES, instance=gallery)
        if form.is_valid():
            form.save()
            return redirect('gallery_list')
    else:
        form = ArtGalleryForm(instance=gallery)
    return render(request, 'edit_gallery.html', {'form': form, 'gallery': gallery})

# Delete ArtGallery
def delete_art_gallery(request, pk):
    gallery = get_object_or_404(ArtGallery, pk=pk)
    if request.method == "POST":
        gallery.delete()
        return redirect('gallery_list')
    return render(request, 'delete_gallery.html', {'gallery': gallery})

# Edit PlannedVisit
def edit_planned_visit(request, pk):
    visit = get_object_or_404(PlannedVisit, pk=pk)
    if request.method == "POST":
        form = PlannedVisitForm(request.POST, instance=visit)
        if form.is_valid():
            form.save()
            return redirect('visit_list')
    else:
        form = PlannedVisitForm(instance=visit)
    return render(request, 'edit_visit.html', {'form': form, 'visit': visit})

# Delete PlannedVisit
def delete_planned_visit(request, pk):
    visit = get_object_or_404(PlannedVisit, pk=pk)
    if request.method == "POST":
        visit.delete()
        return redirect('visit_list')
    return render(request, 'delete_visit.html', {'visit': visit})

def redirect_to_streamlit(request):
    return HttpResponseRedirect("http://localhost:8502")  # Redirect to Streamlit


def gallery_list(request):
    galleries = ArtGallery.objects.all()  # Récupérer toutes les galeries d'art
    return render(request, 'gallery_list.html', {'galleries': galleries})  # Assurez-vous de passer les galeries au template
@login_required(login_url='login')
def cultural_event_list(request):
    events = CulturalEvent.objects.all()
    return render(request, 'cultural_event.html', {'events': events})

@login_required(login_url='login')
def edit_workshop(request, event_id, workshop_id):
    event = get_object_or_404(CulturalEvent, id=event_id)
    workshop = get_object_or_404(CulturalWorkshop, id=workshop_id)

    if request.method == 'POST':
        form = WorkshopForm(request.POST, instance=workshop)
        if form.is_valid():
            form.save()
            messages.success(request, 'Atelier mis à jour avec succès!')
            return redirect('view_workshops', event_id=event.id)
        else:
            messages.error(request, 'Erreur lors de la mise à jour de l\'atelier. Veuillez vérifier le formulaire.')
            print(form.errors)  # Ajoutez cette ligne pour afficher les erreurs dans la console
    else:
        form = WorkshopForm(instance=workshop)

    return render(request, 'edit_workshop.html', {'form': form, 'event': event, 'workshop': workshop})

@login_required(login_url='login')
def delete_workshop(request, event_id, workshop_id):
    workshop = get_object_or_404(CulturalWorkshop, id=workshop_id)

    if request.method == 'POST':
        workshop.delete()
        return redirect('view_workshops', event_id=event_id)

    return render(request, 'confirm_delete.html', {'workshop': workshop})

# Afficher les ateliers d'un événement
@login_required(login_url='login')
def view_workshops(request, event_id):
    event = get_object_or_404(CulturalEvent, id=event_id)
    workshops = event.workshops.all()  # Obtenez les ateliers associés
    return render(request, 'view_workshops.html', {'event': event, 'workshops': workshops})




@login_required(login_url='login')
def add_workshop(request, event_id):
    event = get_object_or_404(CulturalEvent, id=event_id)

    if request.method == 'POST':
        form = WorkshopForm(request.POST)
        if form.is_valid():
            workshop = form.save(commit=False)
            workshop.cultural_event = event
            workshop.save()
            return redirect('view_workshops', event_id=event.id)
    else:
        form = WorkshopForm()

    return render(request, 'add_workshop.html', {'form': form, 'event': event})

def ai_generate_workshop_program(event, workshop):
    # Récupérer les caractéristiques de l'événement
    location = event.location
    event_name = event.event_name
    event_date = event.start_date.strftime("%d %B %Y")

    # Construire un prompt pour Gemini en tenant compte des détails de l'atelier
    prompt = (
        f"Crée un programme détaillé et formaté pour l'atelier '{workshop.name}' dans l'événement culturel '{event_name}' "
        f"qui se déroulera à {location} le {event_date}. "
        f"Voici les détails de l'atelier : \n"
        f"Description : {workshop.description}, \n"
        f"Heure de début : {workshop.start_time.strftime('%H:%M')}\n, "
        f"Durée : {workshop.duration}, "
        f"Limite de participants : {workshop.participant_limit}.\n"
        f"Propose des activités et des horaires pour ce niveau d'expérience.\n"
        f"Assure-toi de mettre chaque partie du programme sur une ligne distincte."
         f"merci de faire un programme claire en 3 ligne  ."
    )

    # Appel à Gemini pour générer le contenu
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    # Formatage de la réponse pour s'assurer que chaque section est sur une ligne distincte
    formatted_response = "\n".join(line.strip() for line in response.text.splitlines() if line.strip())

    return formatted_response  # Retourne le programme formaté


@login_required(login_url='login')
def generate_workshop_program(request, event_id):
    # Récupérer l'événement à partir de l'ID
    event = get_object_or_404(CulturalEvent, id=event_id)

    # Vérifier si la requête est un POST
    if request.method == 'POST':
        workshop_id = request.POST.get('workshop_id')  # Récupérer l'ID de l'atelier à partir de la requête
        workshop = get_object_or_404(CulturalWorkshop, id=workshop_id)  # Récupérer l'atelier à partir de l'ID

        # Rediriger vers la vue pour afficher le programme généré
        return redirect('view_workshop_program', event_id=event_id, workshop_id=workshop_id)

    # Si ce n'est pas une requête POST, redirigez vers la liste des ateliers
    return redirect('view_workshops', event_id=event_id)


@login_required(login_url='login')
def view_workshop_program(request, event_id, workshop_id):
    # Récupérer l'événement et l'atelier à partir de l'ID
    event = get_object_or_404(CulturalEvent, id=event_id)
    workshop = get_object_or_404(CulturalWorkshop, id=workshop_id)

    # Vérifier si la requête est un POST pour mettre à jour le programme
    if request.method == 'POST':
        modified_program = request.POST.get('modified_program', '')
        workshop.update_program(modified_program)  # Appelle la méthode pour mettre à jour le programme
        return redirect('view_workshops', event_id=event.id)  # Redirige vers la liste des ateliers

    # Générer le programme de l'atelier
    workshop.program = ai_generate_workshop_program(event, workshop)

    return render(request, 'workshop_program.html', {
        'event': event,
        'workshop': workshop,
        'workshop.program': workshop.program,
    })
@login_required(login_url='login')
def view_workshop(request, event_id, workshop_id):
    # Récupérer l'événement et l'atelier à partir de l'ID
    event = get_object_or_404(CulturalEvent, id=event_id)
    workshop = get_object_or_404(CulturalWorkshop, id=workshop_id)

    # Vérifier si la requête est un POST pour mettre à jour le programme
    if request.method == 'POST':
        modified_program = request.POST.get('modified_program', '')
        workshop.program = modified_program  # Met à jour le programme de l'atelier
        workshop.save()  # Assurez-vous de sauvegarder l'atelier après la mise à jour
        return redirect('view_workshops', event_id=event.id)  # Redirige vers la liste des ateliers

    return render(request, 'workshop_program.html', {
        'event': event,
        'workshop': workshop,
    })



def delete_artimage_view(request, image_id):

    art_image = get_object_or_404(ArtImages, id=image_id)
    art_image.delete()
    return redirect('http://127.0.0.1:8000/admin/photofolio/artimages/')
