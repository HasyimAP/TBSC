import base64
import streamlit as st

from PIL import Image
from pathlib import Path
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

BASE_DIR = Path(__file__).parent.parent
icon = Image.open(BASE_DIR / 'images/logo_TBSC.jpeg')

st.set_page_config(
    page_icon=icon,
    layout='centered'
)

@st.cache_data
def get_img_as_base64(file):
    with open(file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

sidebar_img = get_img_as_base64('images/sidebar.jpg')

page_bg_img = f'''
<style>
[data-testid="stSidebar"] {{
background-image: url("data:image/png;base64,{sidebar_img}");
background-size: cover;
}}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

conn = st.experimental_connection("gsheets", type=GSheetsConnection)

df_form = conn.read(worksheet='Form').dropna(axis=0, how='all')
df_form = df_form.dropna(axis=1, how='all')

st.header('Join Us!!!')

name = st.text_input('Name:', placeholder='Nickname or fullname')
wa = "\'" + st.text_input('Whatsapp:', placeholder='08xx-xxxx-xxxx')
email = st.text_input('Email (optional):', placeholder='my@email.com')
socmed = st.text_input('Social Media (optional):', placeholder='instagram/facebook/tiktok')
note = st.text_area('Note:',
                    placeholder='Tell us about yourself and your motivation')

if st.button('Submit'):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    regist = {
        'Date': formatted_datetime,
        'Name': name,
        'Whatsapp Number': wa,
        'Email': email,
        'Social Media': socmed,
        'Note': note
    }

    df_form = df_form.append(regist, ignore_index=True)
    conn.update(worksheet='Form', data=df_form)

    st.cache_data.clear()
