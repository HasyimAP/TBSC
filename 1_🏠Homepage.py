import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(
    page_title='TBSC Analysis',
    # page_icon=icon,
    layout='wide'
)

st.title('Welcome to TBSC Dashboard')

# conn = st.experimental_connection("gsheets", type=GSheetsConnection)

# data1 = conn.read(worksheet='Athlete')
# data2 = conn.read(worksheet='Records')
# st.dataframe(data1)
# st.dataframe(data2)

