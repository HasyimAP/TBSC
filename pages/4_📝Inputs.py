import re
import yaml
import tomli
import base64
import streamlit as st
import streamlit_authenticator as stauth

from PIL import Image
from pathlib import Path
from yaml import SafeLoader
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

# --- USER AUTHENTICATION ---
names = ['Hasyim', 'Kak Gede']
username = ['hasyim', 'kakde']

# --- Load Hashed Passwords ---
file_path = Path(__file__).parent.parent / 'config.yml'
with file_path.open('rb') as file:
     config = yaml.load(file, Loader=SafeLoader)

creds = dict(st.secrets.credentials)

authenticator = stauth.Authenticate(credentials=creds,
                                    cookie_name=st.secrets.cookie.name,
                                    key=st.secrets.cookie.key,
                                    cookie_expiry_days=1)


name, authentication_status, username = authenticator.login('Login', 'main')

# --- Necessary Function ---
def validate_input(input_text):
    pattern = r'\d{2}:\d{2}\.\d{2}$'
    return bool(re.match(pattern, input_text))

def get_sex(name):
    row = df_athletes[df_athletes['Name'] == name]
    return row.iloc[0]['Sex']

def get_yob(name):
    row = df_athletes[df_athletes['Name'] == name]
    return row.iloc[0]['Year of Birth']

if authentication_status == False:
     st.error('Username/Password is incorrect')

if authentication_status == None:
     st.warning('Please enter your username and password')
    
if authentication_status:
    authenticator.logout('Logout', 'main')
    st.title('Input Athlete Record')

    conn = st.experimental_connection("gsheets", type=GSheetsConnection)

    df_athletes = conn.read(worksheet='Athlete', usecols=list(range(0,6))).dropna(axis=0, how='all')
    df_records = conn.read(worksheet='Records', usecols=list(range(0,7))).dropna(axis=0, how='all')

    name = st.selectbox(
        'Athlete name:',
        options=sorted(df_athletes['Name'].unique())
    )

    event = st.selectbox(
        'Select event:',
        options=sorted(df_records['Event'].unique())
    )

    time = st.text_input(
        'Input the time (mn\:sc.ms):'
    )

    date = st.date_input(
        'Date:'
    )

    competition = st.text_input(
        'Competition:'
    )

    if not competition:
            competition = ''

    if validate_input(time):
        submit_button = st.button('Submit')
    else:
        submit_button = st.button('Submit', disabled=True)

    if submit_button:
        if not competition:
            competition = ''
        
        new_record = {
            'Name': name,
            'Sex': get_sex(name),
            'Year of Birth': get_yob(name),
            'Event': event,
            'Record': time,
            'Date': str(date),
            'Competition': competition.upper()
        }

        df_records = df_records.append(new_record, ignore_index=True)
        conn.update(worksheet='Records', data=df_records)
        st.success('Record added 🔥')

        show_update = df_records[df_records['Name'] == name].sort_values('Date', ascending=False)
        st.dataframe(show_update.style.format({'Year of Birth': lambda x : '{:.0f}'.format(x)}), hide_index=True, use_container_width=True)

        st.cache_data.clear()
