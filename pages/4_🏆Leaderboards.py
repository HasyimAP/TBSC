import os
import base64
import streamlit as st

from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).parent.parent
icon = Image.open(BASE_DIR / 'images/logo_TBSC.jpeg')

st.set_page_config(
    page_title='TBSC Dashboard',
    page_icon=icon,
    layout='centered'
)

@st.cache_data
def get_img_as_base64(file):
    with open(file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

homepage_img = get_img_as_base64('images/main_page.jpg')
sidebar_img = get_img_as_base64('images/sidebar.jpg')

page_bg_img = f'''
<style>
[data-testid="stAppViewContainer"] {{
background-image: url("data:image/png;base64,{homepage_img}");
background-size: cover;
}}

[data-testid="stHeader"] {{
background: rgb(0, 0, 0, 0);
}}

[data-testid="stAppViewBlockContainer"] {{
background-color: #F0F2F6;
opacity: 0.7;
}}

[data-testid="stSidebar"] {{
background-image: url("data:image/png;base64,{sidebar_img}");
background-size: cover;
}}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

st.title('Coming Soon...')