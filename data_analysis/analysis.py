import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt

from PIL import Image

# page settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
icon = Image.open(BASE_DIR + '/logo TBSC.jpeg')

st.set_page_config(
    page_title='TBSC Analysis',
    page_icon=icon,
    layout='wide'
)

# get data
db_path = os.path.join(BASE_DIR, 'instance/database.db')
cnx = sqlite3.connect(db_path)

df_athlete = pd.read_sql_query('SELECT * FROM athlete', cnx)
df_record = pd.read_sql_query("SELECT * FROM record", cnx)

# ============================================= #

'''
# Overall Progress
'''

df_progress = df_record.copy()
df_progress = df_progress.drop('rec_id', axis=1)

time = df_progress['record'].str.split(':', n=1, expand=True)
df_progress['record (s)'] = time[0].astype(float)*60 + time[1].astype(float)
df_progress = df_progress.sort_values(['name'])

col_1, col_2 = st.columns([3,1])

with col_1:
    athletes = st.multiselect(
        'Select athlete(s):',
        options=df_progress['name'].unique()
    )

with col_2:
    event = st.selectbox(
        'Select event:',
        df_progress.sort_values(['event'])['event'].unique()
    )

df_progress = df_progress.query(
    'name == @athletes'
)

df_progress = df_progress.query(
    'event == @event'
)

df_progress = df_progress.sort_values(['date'])
sorted_record = df_progress['record'].unique().sort()

fig_progress = px.line(df_progress, 
                       x='date', 
                       y='record (s)', 
                       color='name', 
                       width=1280, 
                       height=480,
                       markers=True,
                       text='record',
                       hover_data=['competition'])
fig_progress.update_traces(textposition='bottom center')
fig_progress.update_layout(hovermode='x unified')
y_labels = df_progress['record'].tolist()

fig_progress.update_yaxes(autorange='reversed',
                          categoryorder='array',
                          categoryarray=y_labels
                          )

st.plotly_chart(fig_progress)

# ============================================= #
# '''
# ## Event Timeline
# '''

# competition = df_record['competition'].unique().tolist()

# df_competition = pd.DataFrame({
#     'content': competition
# })

# df_competition['start'] = df_competition.apply(lambda x: min_date(df_record), axis=1)
# df_competition['end'] = df_competition.apply(lambda x: max_date(df_record), axis=1)

# df_competition

# comp_tl = timeline(df_competition.to_json())
# st.write(comp_tl)

# ============================================= #

# '''
# ## Individual Performance
# '''

# individual_records = df_record.copy()
# individual_records = individual_records.drop('rec_id', axis=1)

# time = individual_records['record'].str.split(':', n=1, expand=True)
# individual_records['record (s)'] = time[0].astype(float)*60 + time[1].astype(float)
# individual_records = individual_records.sort_values(['name'])

# athlete = st.selectbox(
#     'Select athlete:',
#     options=individual_records['name'].unique()
# )

# individual_records = individual_records.query(
#     'name == @athlete'
# )

# individual_records = individual_records.sort_values(['date'])
# sorted_record = individual_records['record'].unique().sort()

# fig_ind_records = px.line(individual_records, 
#                        x='date', 
#                        y='record (s)', 
#                        color='event', 
#                        width=1280, 
#                        height=480,
#                        markers=True,
#                        text='record',
#                        hover_data=['competition'])
# fig_ind_records.update_traces(textposition='bottom center')
# # fig_ind_records.update_layout(hovermode='x unified')
# y_labels = individual_records['record'].tolist()

# fig_ind_records.update_yaxes(autorange='reversed',
#                           categoryorder='array',
#                           categoryarray=y_labels
#                           )

# st.plotly_chart(fig_ind_records)