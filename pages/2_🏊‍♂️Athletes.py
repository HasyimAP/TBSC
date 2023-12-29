import base64
import datetime
import pandas as pd
import streamlit as st
import plotly.express as px

from PIL import Image
from pathlib import Path
from datetime import timedelta
from my_functions import categorize_age
from streamlit_gsheets import GSheetsConnection

BASE_DIR = Path(__file__).parent.parent
icon = Image.open(BASE_DIR / 'images/logo_TBSC.jpeg')

st.set_page_config(
    page_icon=icon,
    layout='wide'
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

st.title('Athletes List')

# --- Get All Data ---
conn = st.experimental_connection("gsheets", type=GSheetsConnection)

df_athletes = conn.read(worksheet='Athlete').dropna(axis=0, how='all')
df_athletes = df_athletes.dropna(axis=1, how='all')
df_competitions = conn.read(worksheet='Competitions').dropna(axis=1, how='all')
# df_records = conn.read(worksheet='Records', usecols=list(range(0,8)), ttl=5).dropna(axis=0, how='all')

current_year = datetime.date.today().year

# --- Total Current Athletes ---
df_athletes['Current Age'] = current_year - df_athletes['Year of Birth']
df_athletes['Current Age'] = df_athletes['Current Age'].astype(int)

df_athletes['Age Group'] = df_athletes['Current Age'].apply(categorize_age)

df_athletes = df_athletes.sort_values(by=['Year of Birth', 'Sex'])
df_athletes = df_athletes[['Name', 'Sex', 'Year of Birth', 'Current Age', 'Age Group', 'Status', 'Club', 'Province']]

total, active, semi_active, inactive = st.columns(4)

with total:
    st.write(f"**Total Athletes: {df_athletes['Name'].nunique()}**")

with active:
    st.write(f"*Active: {(df_athletes['Status'] == 'ACTIVE').sum()}*")

with semi_active:
    st.write(f"*Semi-Active: {(df_athletes['Status'] == 'SEMI-ACTIVE').sum()}*")

with inactive:
    st.write(f"*Inactive: {(df_athletes['Status'] == 'INACTIVE').sum()}*")

df_athletes.index = range(1, len(df_athletes) + 1)
st.dataframe(df_athletes.style.format({'Year of Birth': lambda x : '{:.0f}'.format(x)}), use_container_width=True)

# --- Athletes Distribution ---
col1, col2, col3 = st.columns(3)

with col1:
    sex_pie = px.pie(df_athletes, 
                     names='Sex', 
                     title='Sex Distribution', 
                     color_discrete_sequence=px.colors.qualitative.G10)

    st.plotly_chart(sex_pie, use_container_width=True)

with col2:
    age_pie = px.pie(df_athletes, 
                     names='Age Group', 
                     title='Age Group Distribution')

    st.plotly_chart(age_pie, use_container_width=True)

with col3:
    status_pie = px.pie(df_athletes, 
                        names='Status', 
                        title='Status Distribution',
                        color_discrete_sequence=px.colors.qualitative.T10)

    st.plotly_chart(status_pie, use_container_width=True)

# --- Competition Timeline ---
df_competitions = df_competitions.dropna(axis=0, how='all')

col_comp1, col_comp2 = st.columns([2, 3])

with col_comp1:
    st.dataframe(df_competitions.sort_values(by='End Date', ascending=False), hide_index=True)

with col_comp2:
    today = datetime.date.today()

    timeline = px.timeline(df_competitions.sort_values(by='End Date', ascending=False),
                           x_start='Start Date',
                           x_end='End Date',
                           y='Total Athletes',
                           color='Competition',
                           color_discrete_sequence=px.colors.qualitative.Dark24)

    timeline.update_yaxes(categoryorder="total ascending")
    timeline.update_layout(
        xaxis_title="Timeline",
        yaxis_title="Total Athletes",
        title="Swimming Competition",
    )

    timeline.update_xaxes(
        range=[
            (today - timedelta(days=90)).strftime('%Y-%m-%d'),
            today.strftime('%Y-%m-%d')
        ]
    )

    st.plotly_chart(timeline, use_container_width=True)
