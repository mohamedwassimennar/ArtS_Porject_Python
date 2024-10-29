from django.contrib import admin
from .models import User, Artist, ArtImages , Exposition, Reservation, ArtGallery, PlannedVisit
from django.utils.html import format_html
from django.http import HttpResponse
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from .models import User, Artist, ArtImages, Exposition, Reservation, ArtGallery, PlannedVisit,Avis,Catalogue,CulturalEvent, CulturalWorkshop
from django.utils.html import format_html
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin, messages
from django.shortcuts import redirect, get_object_or_404


# Configuration de l'interface d'administration pour le modèle Avis
class AvisAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'contenu', 'note', 'date', 'type_avis')
    list_filter = ('note', 'date', 'type_avis')
    
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    # Action personnalisée pour télécharger un PDF
    actions = ["download_pdf"]

    def download_pdf(self, request, queryset):
        # Créer un buffer en mémoire
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Définir les styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']

        # Titre
        elements = []
        elements.append(Paragraph("Rapport des Avis", title_style))
        elements.append(Spacer(1, 0.2 * inch))

        # En-tête de tableau
        data = [["Utilisateur", "Note", "Date", "Type d'avis"]]
        
        # Ajouter chaque avis au tableau, omettant le champ "Contenu"
        for avis in queryset:
            data.append([
                str(avis.utilisateur),
                str(avis.note),
                avis.date.strftime('%d/%m/%Y'),
                avis.type_avis
            ])
        
        # Configurer le style du tableau
        table = Table(data, colWidths=[1.5*inch, 0.8*inch, 1.2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Arrière-plan de l'en-tête
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        elements.append(table)

        # Fonction de pied de page
        def add_footer(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 8)
            canvas.drawString(inch, 0.75 * inch, "Rapport des Avis - Généré par Admin")
            canvas.drawRightString(7.5 * inch, 0.75 * inch, f"Page {doc.page}")
            canvas.restoreState()

        # Générer le PDF avec en-tête et pied de page sur chaque page
        doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)

        # Préparer la réponse pour télécharger le PDF
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="rapport_avis.pdf"'
        return response

    download_pdf.short_description = "Télécharger PDF des avis sélectionnés"

# Configuration de l'interface d'administration pour le modèle Catalogue
class CatalogueAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'titre', 'description', 'type_catalogue')
    search_fields = ('utilisateur__username', 'titre', 'type_catalogue')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    # Définir une action pour exporter en Excel
    def export_as_excel(self, request, queryset):
        # Créer un fichier Excel
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Catalogue"

        # Définir les en-têtes
        headers = ['Utilisateur', 'Titre', 'Description', 'Type de Catalogue']
        worksheet.append(headers)

        # Ajouter les données
        for obj in queryset:
            worksheet.append([
                obj.utilisateur.username,
                obj.titre,
                obj.description,
                obj.type_catalogue,
            ])

        # Préparer la réponse HTTP pour télécharger le fichier
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=Catalogue.xlsx'
        workbook.save(response)
        return response

    export_as_excel.short_description = "Télécharger la sélection en format Excel"
    
    # Ajouter l'action au modèle d'administration
    actions = [export_as_excel]

class ExpositionAdmin(admin.ModelAdmin):
    list_display = ('nom', 'start_date', 'end_date')  
    search_fields = ('nom', 'description')  
    list_filter = ('start_date', 'end_date')  

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'exposition', 'date', 'entry_time')  
    search_fields = ('user__username', 'exposition__nom', 'status')  
    list_filter = ('status', 'date')  

# Configuration de l'interface d'administration pour le modèle ArtGallery
class ArtGalleryAdmin(admin.ModelAdmin):
    list_display = ('nom', 'adresse', 'heures_ouverture', 'heures_fermeture')  # Affichage dans la liste
    search_fields = ('nom', 'adresse')  # Champs de recherche
    list_filter = ('heures_ouverture', 'heures_fermeture')  # Filtres sur la droite
    filter_horizontal = ('expositions',)  # Champ expositions avec une sélection horizontale pour plusieurs choix

# Configuration de l'interface d'administration pour le modèle PlannedVisit
class PlannedVisitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_visite', 'duree_estimee', 'statut_visite')  # Affichage dans la liste
    search_fields = ('nom', 'statut_visite')  # Champs de recherche
    list_filter = ('statut_visite', 'date_visite')  # Filtres sur la droite
    filter_horizontal = ('galleries_a_visiter',)  # Champ galleries_a_visiter avec une sélection horizontale


class CulturalEventAdmin(admin.ModelAdmin):
    # Attributs à afficher dans la liste
    list_display = ('event_name', 'event_type', 'start_date', 'end_date', 'location')  
    # Champs de recherche
    search_fields = ('event_name', 'description', 'location')  
    # Filtres disponibles sur le côté droit
    list_filter = ('event_type', 'start_date', 'end_date')  

class CulturalWorkshopAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'start_time','participant_limit', 'cultural_event')  # Attributs à afficher
    search_fields = ('name', 'description', 'cultural_event__event_name')  # Champs de recherche
    list_filter = ('date', 'cultural_event')  
# Enregistrer vos modèles avec les classes d'administration personnalisées

class ArtistFilter(admin.SimpleListFilter):
    title = 'Artist'
    parameter_name = 'artist'

    def lookups(self, request, model_admin):
        artists = Artist.objects.all()
        return [(artist.id, artist.name) for artist in artists]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(artist__id=self.value())
        return queryset

class TypeFilter(admin.SimpleListFilter):
    title = 'Type'
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        types = ArtImages.objects.values_list('type', flat=True).distinct()
        return [(t, t) for t in types if t]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(type=self.value())
        return queryset

class YearRangeFilter(admin.SimpleListFilter):
    title = 'Year Range'
    parameter_name = 'year_range'

    def lookups(self, request, model_admin):
        return [
            ('1000-1300', '1000-1300'),
            ('1301-1600', '1301-1600'),
            ('1601-1900', '1601-1900'),
            ('1901-2024', '1901-2024'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            start_year, end_year = map(int, self.value().split('-'))
            return queryset.filter(year__gte=start_year, year__lte=end_year)
        return queryset

class ArtImagesAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'year', 'artist', 'image_preview', 'delete_button')
    search_fields = ('name', 'type', 'artist__name')
    list_filter = (YearRangeFilter, ArtistFilter, TypeFilter)
    actions = ['delete_selected_images']

    def image_preview(self, obj):
        if obj.art_image:
            return format_html('<img src="{}" style="width: 50px; height: 50px;" />', obj.art_image.url)
        return "-"
    
    image_preview.short_description = "Image Preview"

    def delete_button(self, obj):
        delete_url = reverse('delete_artimage', args=[obj.id])
        return format_html('<a href="{}" class="button">Delete</a>', delete_url)

    delete_button.short_description = "Delete"

def delete_artimage_view(self, request, image_id):
    image = get_object_or_404(ArtImages, id=image_id)
    image_name = image.name
    image.delete()
    self.message_user(request, f"Image '{image_name}' deleted successfully.", messages.SUCCESS)
    return redirect('admin:photofolio_artimages_changelist')  # Update with your app label and model name

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('delete/<int:image_id>/', self.admin_site.admin_view(self.delete_artimage_view), name='delete_artimage'),
        ]
        return custom_urls + urls

    

class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'bio_snippet')
    search_fields = ('name',)

    def bio_snippet(self, obj):
        return obj.bio[:100] + '...' if obj.bio and len(obj.bio) > 100 else obj.bio
    bio_snippet.short_description = 'Bio Snippet'


admin.site.register(User)
admin.site.register(ArtImages, ArtImagesAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Avis, AvisAdmin)
admin.site.register(Catalogue, CatalogueAdmin)
admin.site.register(Exposition, ExpositionAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(ArtGallery, ArtGalleryAdmin)
admin.site.register(PlannedVisit, PlannedVisitAdmin)
admin.site.register(CulturalEvent, CulturalEventAdmin)
admin.site.register(CulturalWorkshop, CulturalWorkshopAdmin)