from dotenv import load_dotenv
import streamlit as st
import os
import requests
from PIL import Image
from io import BytesIO
import time

# Charger les variables d'environnement
load_dotenv()

# Configuration de l'API Hugging Face
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"
}

def generer_image(prompt, retries=5, wait=180):
    for attempt in range(retries):
        try:
            # Préparer le payload avec les paramètres de haute qualité
            payload = {
                "inputs": prompt,
                "parameters": {
                    "num_inference_steps": 50,  # Augmente le nombre d'étapes pour une meilleure qualité
                    "guidance_scale": 8.5      # Échelle de guidage pour la précision
                }
            }
            
            response = requests.post(
                API_URL,
                headers=headers,
                json=payload
            )
            
            # Gestion de l'erreur 503 pour réessayer
            if response.status_code == 503:
                st.warning("Le modèle est en cours de chargement, réessai dans quelques minutes...")
                time.sleep(wait)
                continue

            # Si la réponse n'est pas un succès
            if response.status_code != 200:
                st.error(f"Erreur API: {response.status_code} - {response.text}")
                return None
                
            # Convertir la réponse en image
            image = Image.open(BytesIO(response.content))
            return image
        except Exception as e:
            st.error(f"Erreur : {str(e)}")
            return None
    
    # Message d'erreur si toutes les tentatives échouent
    st.error("Le modèle n'a pas pu être chargé après plusieurs tentatives.")
    return None

# Zone de saisie avec plus de contexte
description = st.text_area(
    "Décrivez l'image que vous voulez créer :",
    placeholder="Exemple : Une galerie d'art moderne avec des peintures colorées et une ambiance lumineuse",
    height=100
)


if st.button("✨ Générer l'image"):
    if description:
        with st.spinner("🎨 Création de votre image en cours..."):
            image = generer_image(description)
            if image:
                # Disposition en colonnes pour afficher l'image et le bouton de téléchargement côte à côte
                col1, col2 = st.columns([3, 1])  # Ajustez les proportions si nécessaire
                with col1:
                    # Affiche l'image générée en taille réduite
                    st.image(image, caption="Image générée", width=300)
                with col2:
                    # Bouton de téléchargement à droite de l'image
                    buf = BytesIO()
                    image.save(buf, format='PNG')
                    st.download_button(
                        "💾 Télécharger l'image",
                        buf.getvalue(),
                        "image_generee.png",
                        "image/png"
                    )
    else:
        st.warning("⚠️ Veuillez entrer une description avant de générer une image")
# Afficher le statut du token API
if not HUGGINGFACE_API_TOKEN:
    st.error("⚠️ Token API non trouvé. Vérifiez votre fichier .env")

