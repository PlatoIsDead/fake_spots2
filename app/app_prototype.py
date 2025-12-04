import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import os
import time
import traceback

#api and default image paths
API_URL = "https://fake-spots-image-prod-853522169535.europe-west1.run.app/Predict"
DEFAULT_IMAGE_PATH = "/home/nikita/code/PlatoIsDead/fake_spots2/app/test_image.jpg"  # change if needed

#page layout
st.set_page_config(layout="wide", page_title="Face Retouching Detector")

st.write("## Face Retouching Detector")
st.write(
    "Upload an image with a face. The API will predict whether it is "
    "**Original** or **Modified** and may return a heatmap for edited areas."
)
st.sidebar.write("## Upload image")

#user upload image + submit button
with st.sidebar.form(key="upload_form"):
    uploaded_file = st.file_uploader(
        "Upload a face image", type=["png", "jpg", "jpeg"]
    )
    submit_button = st.form_submit_button("Make prediction")

#little explanation on image requirements
with st.sidebar.expander("ℹ️ Image Guidelines"):
    st.write("""
    - Use close-up face photos
    - Very blurry images may give unreliable results
    - Supported formats: PNG, JPG, JPEG
    """)


#call api
def call_api(image_bytes):
    """
    simple helper around the fastapi endpoint
    """
    files = {"file": ("image.png", image_bytes, "image/png")}
    response = requests.post(API_URL, files=files)
    response.raise_for_status()

    content_type = response.headers.get("content-type", "")

    #modified image -> api returns gradcam png + info in headers
    if content_type.startswith("image/"):
        gradcam_img = Image.open(BytesIO(response.content)).convert("RGB")
        prediction = response.headers.get("x-prediction", "Modified")
        probability = response.headers.get("x-probability", "")
        return prediction, probability, gradcam_img

    #original image -> api returns json with label + proba
    data = response.json()
    prediction = data.get("this_image_is", "Unknown")
    probability = data.get("probability", "")
    return prediction, probability, None


#main logic
def process_image(upload, is_demo=False):
    try:
        #two columns for layout (created inside so they always exist when we draw)
        col1, col2 = st.columns(2)

        start_time = time.time()
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()

        if is_demo:
            status_text.text("Loading demo image...")
        else:
            status_text.text("Loading image...")

        progress_bar.progress(20)

        #read image bytes
        if isinstance(upload, str):
            if not os.path.exists(upload):
                st.error(f"Image not found at path: {upload}")
                return
            with open(upload, "rb") as f:
                image_bytes = f.read()
        else:
            image_bytes = upload.getvalue()

        image = Image.open(BytesIO(image_bytes)).convert("RGB")

        status_text.text("Calling api...")
        progress_bar.progress(60)

        prediction, probability, gradcam_img = call_api(image_bytes)

        progress_bar.progress(90)
        status_text.text("Displaying results...")

        #left is original image
        title_left = "Demo image" if is_demo else "Uploaded image"
        col1.write(title_left)
        col1.image(image, use_container_width=True)

        #right is drivers of model decision
        col2.write("Drivers of model decision")
        if gradcam_img is not None:
            col2.image(gradcam_img, use_container_width=True)
        else:
            col2.info("No heatmap returned by API (image seems original).")

        #prediction block in sidebar
        with st.sidebar:
            st.write("### Prediction")
            st.write(f"**{prediction}**")
            if probability:
                st.write(f"Probability: {probability}")

        progress_bar.progress(100)
        elapsed = time.time() - start_time
        status_text.text(f"Completed in {elapsed:.2f} seconds")

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.sidebar.error("Failed to process image")
        print("Error in process_image:", traceback.format_exc())


#routing logic
if submit_button and uploaded_file is not None:
    #user clicked submit -> use uploaded image
    process_image(uploaded_file, is_demo=False)

elif uploaded_file is None:
    #no upload yet -> show default demo image on load
    if os.path.exists(DEFAULT_IMAGE_PATH):
        st.info("No upload detected. Showing demo on test_image.jpg.")
        process_image(DEFAULT_IMAGE_PATH, is_demo=True)
    else:
        st.info("Please upload an image to get started.")

else:
    #user chose a file but did NOT press submit yet -> keep demo visible
    if os.path.exists(DEFAULT_IMAGE_PATH):
        st.info("Choose 'Make prediction' to analyze your image. Demo shown below.")
        process_image(DEFAULT_IMAGE_PATH, is_demo=True)
    else:
        st.info("Choose 'Make prediction' to analyze your image.")
