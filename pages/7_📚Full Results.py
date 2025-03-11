import base64
import os
import sys
import sentry_sdk
import streamlit as st

from pathlib import Path
from PIL import Image
from streamlit_gsheets import GSheetsConnection

from utilities import exception_handler


sentry_sdk.init()

error_util = sys.modules['streamlit.error_util']
error_util.handle_uncaught_app_exception.__code__ = exception_handler.__code__


BASE_DIR = Path(__file__).parent.parent
icon = Image.open(BASE_DIR / 'images/logo_TBSC.jpeg')

st.set_page_config(
    page_title='Full result',
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
opacity: 0.8;
}}

[data-testid="stSidebar"] {{
background-image: url("data:image/png;base64,{sidebar_img}");
background-size: cover;
}}

[data-testid="stSidebarNavLink"] {{
background-color: rgba(197, 239, 247, 0.75);
}}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

st.title("Download Full Result PDF ")

conn = st.connection("gsheets", type=GSheetsConnection)
df_competitions = conn.read(worksheet='Competitions').dropna(axis=1, how='all')

# Get the list of PDF files
PDF_FOLDER = 'full_result'
pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]

competition_to_pdf = {comp.upper(): pdf for pdf in pdf_files for comp in df_competitions['Competition'] if comp.upper() in pdf.upper()}

# Sort the PDF files based on the order in df_competitions
sorted_pdf_files = [competition_to_pdf[comp] for comp in df_competitions['Competition'] if comp.upper() in competition_to_pdf]

if not pdf_files:
    st.write("No PDF files found in the specified folder.")
else:
    st.write("Click on the links below to download the result files:")
    
    # Create columns for layout
    num_columns = 4  # Number of columns
    cols = st.columns(num_columns)
    
    # Iterate over PDF files and place download buttons in columns
    for i, pdf_file in enumerate(sorted_pdf_files):
        file_path = os.path.join(PDF_FOLDER, pdf_file)
        with open(file_path, "rb") as f:
            col_idx = i % num_columns  # Determine the column index
            cols[col_idx].download_button(
                label=f"{pdf_file}",
                data=f,
                file_name=pdf_file,
                mime="application/pdf"
            )