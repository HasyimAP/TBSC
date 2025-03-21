import datetime
import pandas as pd
import streamlit as st

from streamlit_gsheets import GSheetsConnection

from utilities import assign_rank

st.set_page_config(
    layout='wide'
)

conn = st.connection("gsheets", type=GSheetsConnection)

df_athletes = conn.read(worksheet='Athlete').dropna(axis=0, how='all')
df_athletes = df_athletes.dropna(axis=1, how='all')
df_records = conn.read(worksheet='Records', usecols=list(range(0,7))).dropna(axis=0, how='all')

drop = ['DNS', 'DQ', 'NS', 'NSS']
df_records = df_records[~df_records['Record'].isin(drop)]
df_national_records = conn.read(worksheet='National Records', usecols=list(range(0,3))).dropna(axis=0, how='all')
df_stats = df_athletes[['Name', 'Sex', 'Year of Birth']].copy()

df_stats_copy = df_stats.copy()

# --- Best Time Athletes @ Event ---
df_best_time = df_records

time = df_best_time['Record'].str.split(':', n=1, expand=True)
df_best_time['Record (s)'] = time[0].astype(float)*60 + time[1].astype(float)

df_best_time = df_best_time.sort_values(by=['Name', 'Event', 'Record (s)'])
df_best_time = df_best_time.groupby(['Name', 'Event']).first().reset_index()

'''Individual Records'''
st.dataframe(df_best_time, use_container_width=True)

# --- National Record Time @ Event ---
time = df_national_records['Time'].str.split(':', n=1, expand=True)
df_national_records['Time (s)'] = time[0].astype(float)*60 + time[1].astype(float)

'''National Records'''
st.dataframe(df_national_records, use_container_width=True)

df_best_time = df_best_time.merge(df_national_records, on=['Event', 'Sex'], how='left')

df_best_time['Score'] = (df_best_time['Time (s)']/df_best_time['Record (s)'])*100
st.dataframe(df_best_time, use_container_width=True)

# --- Speed Score ---
df_speed = df_best_time[df_best_time['Event'] == '100M FREESTYLE']
df_speed = df_speed[['Name', 'Score']]
df_speed.reset_index(drop=True, inplace=True)
df_speed.rename(columns={'Score':'Speed Score'}, inplace=True)
df_stats_copy = df_stats_copy.merge(df_speed, on='Name', how='left')
df_stats['Speed Score'] = df_stats_copy['Speed Score'].fillna(0)

# --- Explosive Score ---
df_explo = df_best_time[df_best_time['Event'] == '50M FREESTYLE']
df_explo = df_explo[['Name', 'Score']]
df_explo.reset_index(drop=True, inplace=True)
df_explo.rename(columns={'Score':'Explosive Score'}, inplace=True)
df_stats_copy = df_stats_copy.merge(df_explo, on='Name', how='left')
df_stats['Explosive Score'] = df_stats_copy['Explosive Score'].fillna(0)

# --- Versatility Score ---
df_50free = df_best_time[df_best_time['Event'] == '50M FREESTYLE'][['Name', 'Score']]
df_50free.rename(columns={'Score':'50M Free Score'}, inplace=True)
df_50fly = df_best_time[df_best_time['Event'] == '50M BUTTERFLY'][['Name', 'Score']]
df_50fly.rename(columns={'Score':'50M Fly Score'}, inplace=True)
df_50back = df_best_time[df_best_time['Event'] == '50M BACKSTROKE'][['Name', 'Score']]
df_50back.rename(columns={'Score':'50M Back Score'}, inplace=True)
df_50breast = df_best_time[df_best_time['Event'] == '50M BREASTSTROKE'][['Name', 'Score']]
df_50breast.rename(columns={'Score':'50M Breast Score'}, inplace=True)
df_200im = df_best_time[df_best_time['Event'] == '200M INDIVIDUAL MEDLEY'][['Name', 'Score']]
df_200im.rename(columns={'Score':'200M IM Score'}, inplace=True)
df_versatile = df_stats_copy[['Name']].merge(df_50free, on='Name', how='left').fillna(0)
df_versatile = df_versatile.merge(df_50fly, on='Name', how='left').fillna(0)
df_versatile = df_versatile.merge(df_50back, on='Name', how='left').fillna(0)
df_versatile = df_versatile.merge(df_50breast, on='Name', how='left').fillna(0)
df_versatile = df_versatile.merge(df_200im, on='Name', how='left').fillna(0)
df_versatile['Versatility Score'] = df_versatile[['50M Free Score',
                                                  '50M Fly Score',
                                                  '50M Back Score',
                                                  '50M Breast Score',
                                                  '200M IM Score']].mean(axis=1)
df_stats['Versatility Score'] = df_versatile['Versatility Score']

# --- Stamina Score ---
df_200free = df_best_time[df_best_time['Event'] == '200M FREESTYLE'][['Name', 'Score']]
df_200free.rename(columns={'Score':'200M Free Score'}, inplace=True)
df_400free = df_best_time[df_best_time['Event'] == '400M FREESTYLE'][['Name', 'Score']]
df_400free.rename(columns={'Score':'400M Free Score'}, inplace=True)

df_stamina = df_stats_copy[['Name']].merge(df_200free, on='Name', how='left').fillna(0)
df_stamina = df_stamina.merge(df_400free, on='Name', how='left').fillna(0)
df_stamina['Stamina Score'] = (0.4 * df_stamina['200M Free Score']) + (0.6 * df_stamina['400M Free Score'])
df_stats_copy = df_stats_copy.merge(df_stamina, on='Name', how='left')
df_stats['Stamina Score'] = df_stats_copy['Stamina Score'].fillna(0)

# --- Overall Stats ---
df_stats['Overall Score'] = df_stats[['Speed Score',
                                      'Explosive Score',
                                      'Versatility Score',
                                      'Stamina Score']].mean(axis=1)

# --- Check New Stats ---
df_stats['Speed Rank'] = df_stats['Speed Score'].apply(assign_rank)
df_stats['Explosive Rank'] = df_stats['Explosive Score'].apply(assign_rank)
df_stats['Versatility Rank'] = df_stats['Versatility Score'].apply(assign_rank)
df_stats['Stamina Rank'] = df_stats['Stamina Score'].apply(assign_rank)
df_stats['Overall Rank'] = df_stats['Overall Score'].apply(assign_rank)

# --- Distance Specialization ---
df_100free = df_best_time[df_best_time['Event'] == '100M FREESTYLE'][['Name', 'Score']]
df_100free.rename(columns={'Score':'100M Free Score'}, inplace=True)
df_800free = df_best_time[df_best_time['Event'] == '800M FREESTYLE'][['Name', 'Score']]
df_800free.rename(columns={'Score':'800M Free Score'}, inplace=True)
df_1500free = df_best_time[df_best_time['Event'] == '1500M FREESTYLE'][['Name', 'Score']]
df_1500free.rename(columns={'Score':'1500M Free Score'}, inplace=True)
df_distance = df_stats_copy[['Name']].merge(df_50free, on='Name', how='left').fillna(0)
df_distance['50M Free Rank'] = df_distance['50M Free Score'].apply(assign_rank)
df_distance = df_distance.merge(df_100free, on='Name', how='left').fillna(0)
df_distance['100M Free Rank'] = df_distance['100M Free Score'].apply(assign_rank)
df_distance = df_distance.merge(df_200free, on='Name', how='left').fillna(0)
df_distance['200M Free Rank'] = df_distance['200M Free Score'].apply(assign_rank)
df_distance = df_distance.merge(df_400free, on='Name', how='left').fillna(0)
df_distance['400M Free Rank'] = df_distance['400M Free Score'].apply(assign_rank)
df_distance = df_distance.merge(df_800free, on='Name', how='left').fillna(0)
df_distance['800M Free Rank'] = df_distance['800M Free Score'].apply(assign_rank)
df_distance = df_distance.merge(df_1500free, on='Name', how='left').fillna(0)
df_distance['1500M Free Rank'] = df_distance['1500M Free Score'].apply(assign_rank)
df_stats = df_stats.merge(df_distance, on='Name', how='left')

# --- Stroke Specialization ---
df_100fly = df_best_time[df_best_time['Event'] == '100M BUTTERFLY'][['Name', 'Score']]
df_100fly.rename(columns={'Score':'100M Fly Score'}, inplace=True)
df_200fly = df_best_time[df_best_time['Event'] == '200M BUTTERFLY'][['Name', 'Score']]
df_200fly.rename(columns={'Score':'200M Fly Score'}, inplace=True)
df_100back = df_best_time[df_best_time['Event'] == '100M BACKSTROKE'][['Name', 'Score']]
df_100back.rename(columns={'Score':'100M Back Score'}, inplace=True)
df_200back = df_best_time[df_best_time['Event'] == '200M BACKSTROKE'][['Name', 'Score']]
df_200back.rename(columns={'Score':'200M Back Score'}, inplace=True)
df_100breast = df_best_time[df_best_time['Event'] == '100M BREASTSTROKE'][['Name', 'Score']]
df_100breast.rename(columns={'Score':'100M Breast Score'}, inplace=True)
df_200breast = df_best_time[df_best_time['Event'] == '200M BREASTSTROKE'][['Name', 'Score']]
df_200breast.rename(columns={'Score':'200M Breast Score'}, inplace=True)
df_400im = df_best_time[df_best_time['Event'] == '400M INDIVIDUAL MEDLEY'][['Name', 'Score']]
df_400im.rename(columns={'Score':'400M IM Score'}, inplace=True)

df_stroke = df_stats_copy[['Name']].merge(df_50fly, on='Name', how='left').fillna(0)
df_stroke['50M Fly Rank'] = df_stroke['50M Fly Score'].apply(assign_rank)
df_stroke = df_stroke.merge(df_100fly, on='Name', how='left').fillna(0)
df_stroke['100M Fly Rank'] = df_stroke['100M Fly Score'].apply(assign_rank)
df_stroke = df_stroke.merge(df_200fly, on='Name', how='left').fillna(0)
df_stroke['200M Fly Rank'] = df_stroke['200M Fly Score'].apply(assign_rank)

df_stroke = df_stroke.merge(df_50back, on='Name', how='left').fillna(0)
df_stroke['50M Back Rank'] = df_stroke['50M Back Score'].apply(assign_rank)
df_stroke = df_stroke.merge(df_100back, on='Name', how='left').fillna(0)
df_stroke['100M Back Rank'] = df_stroke['100M Back Score'].apply(assign_rank)
df_stroke = df_stroke.merge(df_200back, on='Name', how='left').fillna(0)
df_stroke['200M Back Rank'] = df_stroke['200M Back Score'].apply(assign_rank)

df_stroke = df_stroke.merge(df_50breast, on='Name', how='left').fillna(0)
df_stroke['50M Breast Rank'] = df_stroke['50M Breast Score'].apply(assign_rank)
df_stroke = df_stroke.merge(df_100breast, on='Name', how='left').fillna(0)
df_stroke['100M Breast Rank'] = df_stroke['100M Breast Score'].apply(assign_rank)
df_stroke = df_stroke.merge(df_200breast, on='Name', how='left').fillna(0)
df_stroke['200M Breast Rank'] = df_stroke['200M Breast Score'].apply(assign_rank)

df_stroke = df_stroke.merge(df_200im, on='Name', how='left').fillna(0)
df_stroke['200M IM Rank'] = df_stroke['200M IM Score'].apply(assign_rank)
df_stroke = df_stroke.merge(df_400im, on='Name', how='left').fillna(0)
df_stroke['400M IM Rank'] = df_stroke['400M IM Score'].apply(assign_rank)

df_stats = df_stats.merge(df_stroke, on='Name', how='left')

'''Stats preview'''
st.dataframe(df_stats)

if st.button('update stats'):
    conn.update(worksheet='Statistic', data=df_stats)
    st.success('Statistic updated')
