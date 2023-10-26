import streamlit as st

from streamlit_gsheets import GSheetsConnection

conn = st.experimental_connection("gsheets", type=GSheetsConnection)

df_competition = conn.read(worksheet='Competitions')
df_records = conn.read(worksheet='Records', usecols=list(range(0,7))).dropna(axis=0, how='all')

comp_list = df_records['Competition'].unique()
start_date = []
end_date = []
total_athletes = []

for comp in comp_list:
    df_temp = df_records[df_records['Competition'] == comp]
    start_date.append(df_temp['Date'].min())
    end_date.append(df_temp['Date'].max())
    total_athletes.append(df_temp['Name'].nunique())

df_competition = df_competition.head(len(comp_list))

df_competition['Competition'] = comp_list
df_competition['Start Date'] = start_date
df_competition['End Date'] = end_date
df_competition['Total Athletes'] = total_athletes

df_competition = df_competition.dropna(axis=1, how='all')
st.dataframe(df_competition.sort_values(by='End Date', ascending=False), use_container_width=True)

# --- UPDATE DATA ---
if st.button('update competition'):
    conn.update(worksheet='Competitions', data=df_competition)

    st.success('Competition updated')

