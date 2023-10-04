import datetime
import streamlit as st

from streamlit_gsheets import GSheetsConnection

st.set_page_config(
    layout='wide'
)

st.title('Athletes List')

conn = st.experimental_connection("gsheets", type=GSheetsConnection)

df_athletes = conn.read(worksheet='Athlete', usecols=list(range(0,5))).dropna(axis=0, how='all')
df_records = conn.read(worksheet='Records', usecols=list(range(0,8))).dropna(axis=0, how='all')

current_year = datetime.date.today().year

df_athletes['Current Age'] = current_year - df_athletes['Year of Birth']
df_athletes['Current Age'] = df_athletes['Current Age'].astype(int)

def categorize_age(age):
    if age >= 19:
        return 'Senior'
    elif age >= 16:
        return 'AG 1'
    elif age >= 14:
        return 'AG 2'
    elif age >= 12:
        return 'AG 3'
    elif age >= 10:
        return 'AG 4'
    elif age >= 8:
        return 'AG 5'
    else:
        return 'Beginner'
    
df_athletes['Age Group'] = df_athletes['Current Age'].apply(categorize_age)

df_athletes = df_athletes.sort_values(by=['Name'])
df_athletes = df_athletes[['Name', 'Sex', 'Year of Birth', 'Current Age', 'Age Group', 'Club', 'Province']]
st.dataframe(df_athletes.style.format({'Year of Birth': lambda x : '{:.0f}'.format(x)}), hide_index=True)