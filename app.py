import streamlit as st
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import torchvision.transforms as T
from SmArtGenerative.utils import loader, unloader
from SmArtGenerative.trainer_segmentation import TrainerSegmentation
from SmArtGenerative.params import vgg_model_path, segmentation_model_path
from SmArtGenerative.image_utils import load_uploaded_image, load_img, tensor_to_image, load_styles, STYLES
from SmArtGenerative.transfer_functions import multiple_styles
from SmArtGenerative.tf_styletransfer import Transfer
import streamlit.components.v1 as components
import random

# streamlit setting
st.set_option('deprecation.showfileUploaderEncoding', False)

# page title
st.title("SmART Generator")
st.write("Transform your photos into art using deep learning!")


@st.cache
def style_transfer(content_img, style_img, style_weight, content_weight):
    model = Transfer(content_img, style_img, n_epochs=1, n_steps=3)
    model.transfer()
    img = tensor_to_image(model.image)
    return img


@st.cache
def load_style_images():
    style_list = load_styles()
    return style_list


@st.cache
def random_image():
    style_list = load_style_images()
    style = random.choice(style_list)
    return style


upload_style_weights = [1e-1, 1e1, 1e4]
upload_content_weights =[1e8, 1e8, 1e1]

##### EXAMPLE SLIDESHOW #########

components.html(
    """

    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
    <div id="Examples" class="carousel slide" data-ride="carousel">
      <div class="carousel-inner">
        <div class="carousel-item active">
          <img class="d-block w-100" src="https://storage.googleapis.com/smartgenerative/style/example-0.png" alt=" Zeroth slide">
        </div>
        <div class="carousel-item">
          <img class="d-block w-100" src="https://storage.googleapis.com/smartgenerative/style/example-4.png" alt="First slide">
        </div>
        <div class="carousel-item">
          <img class="d-block w-100" src="https://storage.googleapis.com/smartgenerative/style/example-2.png" alt="Second slide">
        </div>
        <div class="carousel-item">
          <img class="d-block w-100" src="https://storage.googleapis.com/smartgenerative/style/example-3.png" alt="Third slide">
        </div>
        <div class="carousel-item">
          <img class="d-block w-100" src="https://storage.googleapis.com/smartgenerative/style/example-1.png" alt="Fourth slide">
        </div>
      </div>
    </div>
    <style>
      .carousel-item img {
        max-width: 100%;
        max-height: 100%;
      }
    </style>
    """,
    height=425, width=700,
)

##### STYLE TRANSFER #########

content_up = st.file_uploader("Upload an image:", type=['png', 'jpg', 'jpeg'])

if content_up is not None:

    content_img = load_uploaded_image(content_up)

    options = ['I want to upload my own style image',
                'Choose a style from the gallery',
                'Surprise me!']

    option = st.radio('Pick a style option', options)
    if option == 'I want to upload my own style image':
        style_up = st.file_uploader("Upload the image to transfer style from", type=['png', 'jpg', 'jpeg'])

        if style_up is not None:
            style_img = load_uploaded_image(style_up)

            weights = st.radio('Preference', ('Style Heavy', 'Balanced', 'Content Heavy'))
            if weights == 'Style Heavy':
                style_weight = upload_style_weights[-1]
                content_weight = upload_content_weights[-1]

            if weights == 'Balanced':
                style_weight = upload_style_weights[1]
                content_weight = upload_content_weights[1]

            if weights == 'Content Heavy':
                style_weight = upload_style_weights[0]
                content_weight = upload_content_weights[0]

            if st.button('Start Transfer'):
                img = style_transfer(content_img, style_img, style_weight, content_weight)
                st.success('Style Transfer Complete!')
                st.image(img, 'Voila!')

    if option == 'Choose a style from the gallery':

        pics = [x for x in range(1,22)]
        st.write('You can pick from the following styles:')
        st.image('https://storage.googleapis.com/smartgenerative/style/style-gallery.png')
        st.image('https://storage.googleapis.com/smartgenerative/style/style-gallery-2.png')
        style_list = load_style_images()

        option = st.selectbox('Which style would you like', pics)
        option = option - 1  #Index starts at 0

        'Chosen style:'
        st.image(style_list[option], STYLES[option]['name'])
        style_img = load_uploaded_image(style_list[option], style=True)

        weights = st.radio('Preference', ('Style Heavy', 'Balanced', 'Content Heavy'), index=1)
        if weights == 'Style Heavy':
            style_weight = STYLES[option]['style'][0]
            content_weight = STYLES[option]['style'][1]

        if weights == 'Balanced':
            style_weight = STYLES[option]['balanced'][0]
            content_weight = STYLES[option]['balanced'][1]

        if weights == 'Content Heavy':
            style_weight = STYLES[option]['content'][0]
            content_weight = STYLES[option]['content'][1]

        if st.button('Start Transfer'):
            img = style_transfer(content_img, style_img, style_weight, content_weight)
            st.success('Style Transfer Complete!')
            st.image(img, 'Voila!')

    if option == 'Surprise me!':
        style_list = load_style_images()
        # style = random.choice(style_list)
        style = random_image()

        ind = style_list.index(style)
        style_weight = STYLES[ind]['balanced'][0]
        content_weight = STYLES[ind]['balanced'][1]

        style_img = load_uploaded_image(style, style=True)
        if st.button('Start Transfer'):
            img = style_transfer(content_img, style_img, style_weight, content_weight)
            st.success('Style Transfer Complete!')
            st.image(img, f"Voila! Your image in the style of {STYLES[ind]['name']}")


test = st.radio('Cache', ('Option 1', 'Option 2'))
if test == 'Option 2':
    img = style_transfer(content_img, style_img, style_weight, content_weight)
    st.image(img)


##### STYLE TRANSFER #########
