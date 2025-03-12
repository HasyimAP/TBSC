import pandas as pd
import streamlit as st

from streamlit_gsheets import GSheetsConnection

conn = st.connection("gsheets", type=GSheetsConnection)

df_competition = conn.read(worksheet='Competitions')
df_records = conn.read(worksheet='Records').dropna(axis=0, how='all').dropna(axis=1, how='all')

drop = ['DNS', 'DQ', 'NS', 'NSS']
comp_list = df_records['Competition'].unique()
level = []
start_date = []
end_date = []
total_athletes = []

for comp in comp_list:
    df_temp = df_records[df_records['Competition'] == comp]
    level.append(df_temp['Level'].unique()[0])
    start_date.append(df_temp['Date'].min())
    end_date.append(df_temp['Date'].max())
    total_athletes.append(df_temp['Name'].nunique())

df_competition = pd.DataFrame()

df_competition['Competition'] = comp_list
df_competition['Level'] = level
df_competition['Start Date'] = start_date
df_competition['End Date'] = end_date
df_competition['Total Athletes'] = total_athletes

df_competition = df_competition.dropna(axis=1, how='all')
df_competition = df_competition.sort_values(by='End Date', ascending=False)
st.dataframe(df_competition.sort_values(by='End Date', ascending=False), use_container_width=True)

# --- UPDATE DATA ---
if st.button('update competition'):
    conn.update(worksheet='Competitions', data=df_competition)

    st.success('Competition updated')

