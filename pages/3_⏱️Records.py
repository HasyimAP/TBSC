import base64
import datetime
import pandas as pd
import streamlit as st
import plotly.express as px

from PIL import Image
from pathlib import Path
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

st.title('Athlete Records')

conn = st.experimental_connection("gsheets", type=GSheetsConnection)

df_athletes = conn.read(worksheet='Athlete', usecols=list(range(0,6))).dropna(axis=0, how='all')
df_records = conn.read(worksheet='Records', usecols=list(range(0,7))).dropna(axis=0, how='all')
df_stats = conn.read(worksheet='Statistic').dropna(axis=0, how='all')
df_stats = df_stats.dropna(axis=1, how='all')

athlete = st.selectbox(
    'Choose athlete:',
    options=sorted(df_athletes['Name'].unique())
)

# --- Athlete Statistic ---
col1, col2 = st.columns(2)

df_stats = df_stats.query(
        'Name == @athlete'
    ).reset_index()

with col1:
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

    f'''
    Sex:
        
        {df_athletes.loc[df_athletes['Name'] == athlete, 'Sex'].values[0] if athlete in df_athletes['Name'].values else None}

    Age Group:

        {df_athletes.loc[df_athletes['Name'] == athlete, 'Age Group'].values[0] if athlete in df_athletes['Name'].values else None}

    Overall Score:

        {round(df_stats['Overall Score'][0], 2)}
    
    Overall Rank:

        {df_stats['Overall Rank'][0]}
    '''

with col2:
    radar_data = {
        'Category': [f'Speed ({df_stats["Speed Rank"][0]})',
                    f'Explosive ({df_stats["Explosive Rank"][0]})',
                    f'Versatility ({df_stats["Versatility Rank"][0]})'],
        'Values': [df_stats["Speed Score"][0],
                df_stats["Explosive Score"][0],
                df_stats["Versatility Score"][0]]
    }

    df_radar = pd.DataFrame(radar_data)
    radar = px.line_polar(df_radar, r='Values', theta='Category', line_close=True)
    radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        polar_angularaxis=dict(
            tickfont=dict(size=24)  # Adjust the size and weight (bold) of the text
        ),
        showlegend=True
    )

    st.plotly_chart(radar)

# --- DATAFRAME BEST TIME ---
df_records = df_records.query(
    'Name == @athlete'
).sort_values(['Date'], ascending=False)

df_best_time = df_records

time = df_best_time['Record'].str.split(':', n=1, expand=True)
df_best_time['Record (s)'] = time[0].astype(float)*60 + time[1].astype(float)

idx = df_best_time.groupby('Event')['Record (s)'].idxmin()
df_best_time = df_best_time.loc[idx]
df_best_time.reset_index(drop=True, inplace=True)
df_best_time = df_best_time[['Event', 'Record', 'Competition', 'Date']]

'''
## Best Times
'''

st.dataframe(
    df_best_time,
    hide_index=True, 
    use_container_width=True
)

# Track Records
'''
## Track Records
'''

event = st.selectbox(
    'Choose event:',
    options=sorted(df_records['Event'].unique())
)

time = df_records['Record'].str.split(':', n=1, expand=True)
df_records['Record (s)'] = time[0].astype(float)*60 + time[1].astype(float)

df_records = df_records.query(
    'Event == @event'
)

df_progress = df_records.sort_values(['Date'])
sorted_record = df_progress['Record'].unique().sort()

fig_progress = px.line(df_progress, 
                       x='Date', 
                       y='Record (s)',
                       markers=True,
                       text='Record',
                       hover_data=['Competition'])
fig_progress.update_traces(textposition='bottom center')
fig_progress.update_layout(hovermode='x unified')
y_labels = df_progress['Record'].tolist()

fig_progress.update_yaxes(autorange='reversed',
                          categoryorder='array',
                          categoryarray=y_labels
                          )

st.plotly_chart(fig_progress, use_container_width=True)

