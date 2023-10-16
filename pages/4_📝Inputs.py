import re
import yaml
import pickle
import streamlit as st
import streamlit_authenticator as stauth

from pathlib import Path
from yaml import SafeLoader
from streamlit_gsheets import GSheetsConnection

st.set_page_config(
    layout='wide'
)

# --- USER AUTHENTICATION ---
names = ['Hasyim', 'Kak Gede']
username = ['hasyim', 'kakde']

# --- Load Hashed Passwords ---
file_path = Path(__file__).parent.parent / 'config.yml'
with file_path.open('rb') as file:
     config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(config['credentials'],
                                    config['cookie']['name'], 
                                    config['cookie']['key'],
                                    cookie_expiry_days=1)

name, authentication_status, username = authenticator.login('Login', 'main')

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
        'Who are you?',
        options=sorted(df_athletes['Name'].unique())
    )

    event = st.selectbox(
        'Select event:',
        options=sorted(df_records['Event'].unique())
    )

    time = st.text_input(
        'Input your time (mm\:ss.ms):'
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
