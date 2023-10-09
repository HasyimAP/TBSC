import re
import streamlit as st

from streamlit_gsheets import GSheetsConnection

st.set_page_config(
    layout='wide'
)

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

def validate_input(input_text):
    pattern = r'\d{2}:\d{2}\.\d{2}$'
    return bool(re.match(pattern, input_text))

def get_sex(name):
    row = df_athletes[df_athletes['Name'] == name]
    return row.iloc[0]['Sex']

def get_yob(name):
    row = df_athletes[df_athletes['Name'] == name]
    return row.iloc[0]['Year of Birth']

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
        'Competition': competition
    }

    df_records = df_records.append(new_record, ignore_index=True)
    conn.update(worksheet='Records', data=df_records)
    st.success('Record added 🔥')

    show_update = df_records[df_records['Name'] == name].sort_values('Date', ascending=False)
    st.dataframe(show_update.style.format({'Year of Birth': lambda x : '{:.0f}'.format(x)}), hide_index=True)

    st.cache_data.clear()