import streamlit as st
import requests
from PIL import Image
import io
import numpy as np

st.title("Image Upload and Prediction")

with st.form(key='params_for_api'):
    upload_image = st.file_uploader("Choose an image to upload", type=["jpg", "jpeg", "png"])
    submit_button = st.form_submit_button('Make Prediction')

if submit_button and upload_image:
    # Prepare the files payload
    files = {'file': (upload_image.name, upload_image, upload_image.type)}

    # Call the API
    fake_spot_api_url = 'https://fake-spots-image-prod-853522169535.europe-west1.run.app/Predict'

    try:
        response = requests.post(fake_spot_api_url, files=files)
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)

        # Check the content type to determine how to process the response
        content_type = response.headers.get('Content-Type')

        if 'application/json' in content_type:
            # Handle JSON response
            prediction = response.json()

            # Extract data from the JSON response
            image_status = prediction.get('this_image_is', 'Unknown')
            probability = prediction.get('probability', 'N/A')
            image_data = prediction.get('image', None)

            # Display the prediction result
            st.header("Prediction Result")
            st.subheader("Image Status")
            st.write(f"The image is: **{image_status}**")
            st.write(f"Probability: **{probability}**")

            # Handle images
            if image_data is None or image_data == 0:
                st.warning("Image doesn't need to go through Grad Cam.")
            else:
                st.warning("Unexpected image data format.")

        elif 'image/png' in content_type:
            # Handle PNG image response for fake images
            image = Image.open(io.BytesIO(response.content))

            # Fetch prediction and probability from response headers
            prediction = response.headers.get('x-prediction', 'Unknown')
            probability = response.headers.get('x-probability', 'N/A')

            # Display result from headers before showing the image
            st.header("Prediction Result")
            st.subheader("Image Status")
            st.write(f"The image is: **{prediction}**")
            st.write(f"Probability: **{probability}**")

            # Rescale the image to be 30% smaller
            new_size = (int(image.width * 0.7), int(image.height * 0.7))
            image = image.resize(new_size, Image.LANCZOS)

            # Display the image
            st.image(image, caption='Processed Image (Fake Detected)', use_container_width=True)

        else:
            st.warning("Received unexpected content type from the API.")

    except requests.exceptions.HTTPError as err:
        st.error(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        st.error(f"Error during requests to {fake_spot_api_url}: {err}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
