import pandas as pd
import streamlit as st

from streamlit_gsheets import GSheetsConnection

st.set_page_config(
    layout='wide'
)

conn = st.experimental_connection("gsheets", type=GSheetsConnection)

df_records = conn.read(worksheet='Records', usecols=list(range(0,7))).dropna(axis=0, how='all')
df_national_records = conn.read(worksheet='National Records', usecols=list(range(0,3))).dropna(axis=0, how='all')
df_stats = conn.read(worksheet='Statistic', usecols=list(range(0,12))).dropna(axis=0, how='all')

df_stats_copy = df_stats.copy()
df_stats_copy = df_stats_copy.dropna(axis=1, how='all')

def assign_rank(score):
    if score > 98.0:
        return 'EX'
    elif score > 95:
        return 'S+'
    elif score > 92.5:
        return 'S'
    elif score > 90:
        return 'S-'
    elif score > 87:
        return 'A+'
    elif score > 83:
        return 'A'
    elif score > 80:
        return 'A-'
    elif score > 77:
        return 'B+'
    elif score > 73:
        return 'B'
    elif score > 70:
        return 'B-'
    elif score > 67:
        return 'C+'
    elif score > 63:
        return 'C'
    elif score > 60:
        return 'C-'
    elif score > 57:
        return 'D+'
    elif score > 53:
        return 'D'
    elif score > 50:
        return 'D-'
    elif score > 45:
        return 'E+'
    elif score > 35:
        return 'E'
    elif score > 25:
        return 'E-'
    else:
        return 'F'

# --- Best Time Athletes @ Event ---
df_best_time = df_records

time = df_best_time['Record'].str.split(':', n=1, expand=True)
df_best_time['Record (s)'] = time[0].astype(float)*60 + time[1].astype(float)

df_best_time = df_best_time.sort_values(by=['Name', 'Event', 'Record (s)'])
df_best_time = df_best_time.groupby(['Name', 'Event']).first().reset_index()

st.dataframe(df_best_time, use_container_width=True)

# --- National Record Time @ Event ---
time = df_national_records['Time'].str.split(':', n=1, expand=True)
df_national_records['Time (s)'] = time[0].astype(float)*60 + time[1].astype(float)
st.dataframe(df_national_records, use_container_width=True)

df_best_time = df_best_time.merge(df_national_records, on=['Event', 'Sex'], how='left')

df_best_time['Score'] = (df_best_time['Time (s)']/df_best_time['Record (s)'])*100
st.dataframe(df_best_time, use_container_width=True)

# --- Speed Score ---
df_speed = df_best_time[df_best_time['Event'] == '100M FREESTYLE']
df_speed = df_speed[['Name', 'Score']]
df_speed.reset_index(drop=True, inplace=True)
df_stats_copy = df_stats_copy.merge(df_speed, on='Name', how='left')
df_stats['Speed Score'] = df_stats_copy['Score'].fillna(0)

# --- Explosive Score ---
df_explo = df_best_time[df_best_time['Event'] == '50M FREESTYLE']
df_explo = df_explo[['Name', 'Score']]
df_explo = df_explo.rename(columns= {'Score':'Explosive Score'})
df_explo.reset_index(drop=True, inplace=True)
df_stats_copy = df_stats_copy.merge(df_explo, on='Name', how='left')
df_stats['Explosive Score'] = df_stats_copy['Explosive Score'].fillna(0)

df_stats['Speed Rank'] = df_stats['Speed Score'].apply(assign_rank)
df_stats['Explosive Rank'] = df_stats['Explosive Score'].apply(assign_rank)
st.dataframe(df_stats)

if st.button('update stats'):
    conn.update(worksheet='Statistic', data=df_stats)
