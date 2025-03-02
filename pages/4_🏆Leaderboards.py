import datetime
import base64
import streamlit as st

from pathlib import Path
from PIL import Image
from streamlit_gsheets import GSheetsConnection

from utilities import assign_rank, categorize_age

BASE_DIR = Path(__file__).parent.parent
icon = Image.open(BASE_DIR / 'images/logo_TBSC.jpeg')

st.set_page_config(
    page_title='TBSC Dashboard',
    page_icon=icon,
    layout='wide'
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
# [data-testid="stAppViewContainer"] {{
# background-image: url("data:image/png;base64,{homepage_img}");
# background-size: cover;
# }}

[data-testid="stHeader"] {{
background: rgb(0, 0, 0, 0);
}}

# [data-testid="stAppViewBlockContainer"] {{
# background-color: #F0F2F6;
# opacity: 0.7;
# }}

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

st.title('Leaderboards')
st.write("Welcome to the Leaderboards page. Here you can find the best times and records for various events.")

conn = st.connection("gsheets", type=GSheetsConnection)

current_year = datetime.date.today().year

# Load data
current_year = datetime.date.today().year
df_records = conn.read(worksheet='Records', usecols=list(range(0,7))).dropna(axis=0, how='all')

df_athlete = conn.read(worksheet='Athlete').dropna(axis=0, how='all').dropna(axis=1, how='all')
df_statistic = conn.read(worksheet='Statistic').dropna(axis=0, how='all').dropna(axis=1, how='all')

# Filter out unwanted records
df_records['Current Age'] = current_year - df_records['Year of Birth']
df_records['Current Age'] = df_records['Current Age'].astype(int)
df_records['Age Group'] = df_records['Current Age'].apply(categorize_age)

drop = ['DNS', 'DQ', 'NS', 'NSS']
df_records = df_records[~df_records['Record'].isin(drop)]

include_inactive = st.checkbox('Include Inactive Athletes', value=False)

if not include_inactive:
    inactive = ['INACTIVE', 'TRANSFER']
    df_athlete = df_athlete[~df_athlete['Status'].isin(inactive)]

    df_records = df_records[df_records['Name'].isin(df_athlete['Name'].unique())]
    df_statistic = df_statistic[df_statistic['Name'].isin(df_athlete['Name'].unique())]

# --- Best Time Athletes @ Event ---
st.header('General Rankings')

df_best_time = df_records.copy()
time = df_best_time['Record'].str.split(':', n=1, expand=True)
df_best_time['Record (s)'] = time[0].astype(float)*60 + time[1].astype(float)

df_best_time = df_best_time.sort_values(by=['Name', 'Event', 'Record (s)'])
df_best_time = df_best_time.groupby(['Name', 'Event']).first().reset_index()

general_event = st.selectbox(
    'Choose event:',
    options=sorted(df_best_time['Event'].unique()),
    key='general_event'
)

best_time = df_best_time.query(
    "Event == @general_event"
)

general_input_colunms = st.columns(2)

with general_input_colunms[0]:
    general_age_group = st.selectbox(
        'Age Group:',
        options=['All'] + sorted(best_time['Age Group'].unique()),
        key='general_age_group'
    )

if general_age_group != 'All':
    best_time = best_time.query("`Age Group` == @general_age_group")

with general_input_colunms[1]:
    general_sex = st.selectbox(
        'Sex:',
        options=['All'] + sorted(best_time['Sex'].unique()),
        key='general_sex'
    )

if general_sex != 'All':
    best_time = best_time.query('Sex == @general_sex')

best_time = best_time.drop(columns='Event')
best_time = best_time.sort_values(by='Record (s)')
best_time = best_time.reset_index(drop=True)
best_time['Year of Birth'] = best_time['Year of Birth'].astype(str).replace('\.0', '', regex=True)
best_time.index.name = 'Rank'
best_time.index = best_time.index + 1

st.dataframe(best_time)

st.header('Statistics Rankings')

df_statistic['Current Age'] = current_year - df_statistic['Year of Birth']
df_statistic['Current Age'] = df_statistic['Current Age'].astype(int)
df_statistic['Age Group'] = df_statistic['Current Age'].apply(categorize_age)

statistic_input_colunms = st.columns(3)

with statistic_input_colunms[0]:
    statistic_age_group = st.selectbox(
        'Age Group:',
        options=['All'] + sorted(df_statistic['Age Group'].unique()),
        key='statistic_age_group'
    )

if statistic_age_group != 'All':
    df_statistic = df_statistic.query("`Age Group` == @statistic_age_group")

with statistic_input_colunms[1]:
    statistic_sex = st.selectbox(
        'Sex:',
        options=['All'] + sorted(df_statistic['Sex'].unique()),
        key='statistic_sex'
    )

if statistic_sex != 'All':
    df_statistic = df_statistic.query("`Sex` == @statistic_sex")

with statistic_input_colunms[2]:
    statistic_group = st.selectbox(
        'Group:',
        options=['Overall', 'Speed', 'Explosive', 'Versatility', 'Stamina'],
        key='statistic_group'
    )

df_statistic = df_statistic[[
    'Name',
    'Sex',
    'Year of Birth',
    'Age Group',
    f'{statistic_group} Score',
    f'{statistic_group} Rank',
]]

df_statistic['Average Score'] = df_statistic.groupby(['Age Group', 'Sex'])[f'{statistic_group} Score'].transform('mean')
df_statistic['Average Rank'] = df_statistic['Average Score'].apply(assign_rank)

df_statistic = df_statistic.sort_values(by=f'{statistic_group} Score', ascending=False)
df_statistic = df_statistic.reset_index(drop=True)
df_statistic.index.name = 'Rank'
df_statistic.index = df_statistic.index + 1

st.dataframe(df_statistic, use_container_width=True)