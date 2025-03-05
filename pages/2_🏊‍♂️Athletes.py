import base64
import datetime
import sys
import pandas as pd
import sentry_sdk
import streamlit as st
import plotly.express as px

from PIL import Image
from pathlib import Path
from datetime import timedelta
from utilities import categorize_age, exception_handler
from streamlit_gsheets import GSheetsConnection


sentry_sdk.init()

error_util = sys.modules['streamlit.error_util']
error_util.handle_uncaught_app_exception.__code__ = exception_handler.__code__


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

[data-testid="stSidebarNavLink"] {{
background-color: rgba(197, 239, 247, 0.75);
}}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

st.title('Athletes List')

# --- Get All Data ---
conn = st.connection("gsheets", type=GSheetsConnection)

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

total, active, semi_active, inactive, transfer = st.columns(5)

with total:
    st.write(f"**Total Athletes: {df_athletes['Name'].nunique()}**")

with active:
    st.write(f"*Active: {(df_athletes['Status'] == 'ACTIVE').sum()}*")

with semi_active:
    st.write(f"*Semi-Active: {(df_athletes['Status'] == 'SEMI-ACTIVE').sum()}*")

with inactive:
    st.write(f"*Inactive: {(df_athletes['Status'] == 'INACTIVE').sum()}*")

with transfer:
    st.write(f"*Transferred: {(df_athletes['Status'] == 'TRANSFER').sum()}*")

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
    age_count_df = pd.DataFrame()
    age_count_df['Age Group'] = df_athletes['Age Group'].unique().tolist()
    age_count_df['Count'] = age_count_df['Age Group'].apply(lambda x: (df_athletes['Age Group'] == x).sum())
    age_bar = px.bar(
        age_count_df,
        x='Age Group',
        y='Count',
        title='Age Group Distribution',
        color='Age Group',
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    age_bar.update_layout(showlegend=False)

    st.plotly_chart(age_bar, use_container_width=True)

with col3:
    status_pie = px.pie(df_athletes, 
                        names='Status', 
                        title='Status Distribution',
                        color_discrete_sequence=px.colors.qualitative.T10)

    st.plotly_chart(status_pie, use_container_width=True)

# --- Competition Timeline ---
df_competitions = df_competitions.dropna(axis=0, how='all')
df_competitions = df_competitions.sort_values(by='End Date', ascending=False)

col_comp1, col_comp2 = st.columns([3, 4])

with col_comp1:
    st.dataframe(df_competitions, hide_index=True)

with col_comp2:
    today = datetime.date.today()
    
    timeline = px.bar(
        df_competitions,
        x='Competition',
        y='Total Athletes',
        range_x=[len(df_competitions)-10, len(df_competitions)],
        # title='Age Group Distribution',
        color='Competition',
        color_discrete_sequence=px.colors.qualitative.Dark24
    )

    timeline.update_layout(
        xaxis_title="Competition",
        yaxis_title="Total Athletes",
        title="Swimming Competition",
        showlegend=False
    )

    st.plotly_chart(timeline, use_container_width=True)
