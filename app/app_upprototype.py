import streamlit as st
from fastai.vision.all import load_learner, PILImage
from PIL import Image
import os
import traceback
import time

#model and default image paths

MODEL_PATH = "/home/nikita/code/PlatoIsDead/Project/Models/fastai_all_data.pkl"
DEFAULT_IMAGE_PATH = "/home/nikita/code/PlatoIsDead/fake_spots2/app/test_image.jpg"
DEFAULT_IMAGE_PATH2 = "/home/nikita/code/PlatoIsDead/fake_spots2/app/output.png"

if os.path.exists(DEFAULT_IMAGE_PATH):
    default_img = Image.open(DEFAULT_IMAGE_PATH).convert("RGB")
#page layout
st.set_page_config(layout="wide", page_title="Face Retouching Detector")

st.write("## Face Retouching Detector")
st.write(
    "Upload an image with a face. The model will predict whether it is **Original** or **Retouched**."
)
st.sidebar.write("## Upload image")

#fastai model cached and prediction logic

@st.cache_resource
def load_model(path: str):
    return load_learner(path)

model = load_model(MODEL_PATH)

def run_prediction(pil_img: Image.Image):
    img = PILImage.create(pil_img)
    pred_class, pred_idx, probs = model.predict(img)
    return pred_class, pred_idx, probs

#two columns for layout

col1, col2 = st.columns(2)

#main logic

def process_image(upload):
    try:
        start_time = time.time()
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()

        status_text.text("Loading image...")
        progress_bar.progress(20)

        #(no resizing)
        if isinstance(upload, str):
            if not os.path.exists(upload):
                st.error(f"Default image not found at path: {upload}")
                return
            image = Image.open(upload).convert("RGB")
        else:
            image = Image.open(upload).convert("RGB")

        status_text.text("Running model...")
        progress_bar.progress(60)

        pred_class, pred_idx, probs = run_prediction(image)

        progress_bar.progress(90)
        status_text.text("Displaying results...")

        #LEFT IS ORIGINAL IMAGE
        col1.write("Uploaded image")
        col1.image(image, use_container_width=True)

        #FIX LATER
        #EITHER CROPPED IMAGE OR PHOTOPHOP PIXELS HIGHLIGHT
        col2.write("Drivers of model decision")

        #needs rework loads default after processing
        if os.path.exists(DEFAULT_IMAGE_PATH2):
            output_img = Image.open(DEFAULT_IMAGE_PATH2).convert("RGB")
            col2.image(output_img, use_container_width=True)
        else:
            col2.warning("Output image not found.")


        with st.sidebar:
            st.write("### Prediction")
            st.write(f"**{pred_class}**")

            #class proba
            if hasattr(model, "dls") and hasattr(model.dls, "vocab"):
                labels = list(model.dls.vocab)
                st.write("Probability:")
                for label, prob in zip(labels, probs):
                    st.write(f"- {label}: {float(prob):.2%}")
            else:
                st.write(probs)

        progress_bar.progress(100)
        elapsed = time.time() - start_time
        status_text.text(f"Completed in {elapsed:.2f} seconds")

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.sidebar.error("Failed to process image")
        print("Error in process_image:", traceback.format_exc())

#user upload image

uploaded_file = st.sidebar.file_uploader(
    "Upload a face image", type=["png", "jpg", "jpeg"]
)

#little explanation on image requirments
with st.sidebar.expander("ℹ️ Image Guidelines"):
    st.write("""
    - Largest face will automatically be found
    - If image is too blurry prediction cannot be made
    - Supported formats: PNG, JPG, JPEG
    """)

#

if uploaded_file is not None:
    else:
        process_image(uploaded_file)
else:
    #use test_image as default
    if os.path.exists(DEFAULT_IMAGE_PATH):
        process_image(DEFAULT_IMAGE_PATH)
    else:
        st.info("Please upload an image to get started!")
