from dotenv import load_dotenv
load_dotenv()
# For loading environment variables
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

# Configure the new Gemini model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function for loading our Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")  # Use the updated model

def get_gemini_response(input, image):
    if input != "":
        response = model.generate_content([input, image])
    else:
        response = model.generate_content(image)
    return response.text

st.set_page_config(page_title="Image Describer")

st.header("Image Describer")
input = st.text_input("Input:", key="input")
uploaded_file = st.file_uploader("Choose an image", type=["jpeg", "jpg", "png"])
image = ""

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

submit = st.button("Describe the image to me")

if submit:
    response = get_gemini_response(input, image)
    st.subheader("The response is")
    st.write(response)