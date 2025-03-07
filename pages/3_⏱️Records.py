import base64
import datetime
import json
import sys
import pandas as pd
import sentry_sdk
import streamlit as st
import plotly.express as px

from PIL import Image
from pathlib import Path
from datetime import timedelta
from ai_analysis import analyze_athlete_stats
from utilities import assign_rank, categorize_age, exception_handler
from streamlit_gsheets import GSheetsConnection

sentry_sdk.init()

error_util = sys.modules['streamlit.error_util']
error_util.handle_uncaught_app_exception.__code__ = exception_handler.__code__

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

[data-testid="stSidebarNavLink"] {{
background-color: rgba(197, 239, 247, 0.75);
}}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

st.title('Athlete Records')

conn = st.connection("gsheets", type=GSheetsConnection)

df_athletes = conn.read(worksheet='Athlete', usecols=list(range(0,6))).dropna(axis=0, how='all')
df_records = conn.read(worksheet='Records', usecols=list(range(0,7))).dropna(axis=0, how='all')
df_stats = conn.read(worksheet='Statistic').dropna(axis=0, how='all').dropna(axis=1, how='all')

drop = ['DNS', 'DQ', 'NS', 'NSS']
df_records = df_records[~df_records['Record'].isin(drop)]

athlete = st.selectbox(
    'Choose athlete:',
    options=sorted(df_athletes['Name'].unique())
)

# --- Athlete Statistic ---
col1, col2 = st.columns([1,3])

df_stats = df_stats.query('Name == @athlete').reset_index()

with col1:
    current_year = datetime.date.today().year
    df_athletes['Current Age'] = current_year - df_athletes['Year of Birth']
    df_athletes['Current Age'] = df_athletes['Current Age'].astype(int)
    df_athletes['Age Group'] = df_athletes['Current Age'].apply(categorize_age)

    athlete_data = f"""
    **Status:** {df_athletes.loc[df_athletes['Name'] == athlete, 'Status'].values[0] if athlete in df_athletes['Name'].values else None}

    **Sex:** {df_athletes.loc[df_athletes['Name'] == athlete, 'Sex'].values[0] if athlete in df_athletes['Name'].values else None}

    **Year of Birth:** {str(df_athletes.loc[df_athletes['Name'] == athlete, 'Year of Birth'].values[0]).replace('.0', '') if athlete in df_athletes['Name'].values else None}

    **Current Age:** {df_athletes.loc[df_athletes['Name'] == athlete, 'Current Age'].values[0] if athlete in df_athletes['Name'].values else None}

    **Age Group:** {df_athletes.loc[df_athletes['Name'] == athlete, 'Age Group'].values[0] if athlete in df_athletes['Name'].values else None}

    **Overall Score:** {round(df_stats['Overall Score'][0], 2)}

    **Overall Rank:** {df_stats['Overall Rank'][0]}
    """

    st.markdown(athlete_data)

    with st.expander('Scoring System'):
        st.write('The scoring system is based on the athlete\'s performance in each event. The athlete\'s score is calculated by the following formula:')
        st.latex(r'Score = \frac{National Record}{Personal Best} \times 100')

with col2:
    radar_data = {
        'Category': [f'Speed ({df_stats["Speed Rank"][0]})',
                    f'Explosive ({df_stats["Explosive Rank"][0]})',
                    f'Stamina ({df_stats["Stamina Rank"][0]})',
                    f'Versatility ({df_stats["Versatility Rank"][0]})'],
        'Values': [df_stats["Speed Score"][0],
                   df_stats["Explosive Score"][0],
                   df_stats["Stamina Score"][0],
                   df_stats["Versatility Score"][0]]
    }

    df_radar = pd.DataFrame(radar_data)
    radar = px.line_polar(df_radar, r='Values', theta='Category', line_close=True)
    radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        polar_angularaxis=dict(
            tickfont=dict(size=24)
        ),
        showlegend=True
    )

    st.plotly_chart(radar, use_container_width=True)

with st.expander('Ranking System'):
    st.write('The athlete\'s rank is based on the athlete\'s score in each category. The athlete\'s rank is grouped into the following categories:')
    
    rs_col1, rs_col2, rs_col3, rs_col4, rs_col5 = st.columns(5)

    with rs_col1:
        st.markdown("""
        - 100.00 - 98.00: EX
        - 98.00 - 95.00: S+
        - 95.00 - 92.50: S
        - 92.50 - 90.00: S-
        """)

    with rs_col2:
        st.markdown("""
        - 87.00 - 90.00: A+
        - 83.00 - 87.00: A
        - 80.00 - 83.00: A-
        - 77.00 - 80.00: B+
        """)

    with rs_col3:
        st.markdown("""
        - 73.00 - 77.00: B
        - 70.00 - 73.00: B-
        - 67.00 - 70.00: C+
        - 63.00 - 67.00: C
        """)

    with rs_col4:
        st.markdown("""
        - 60.00 - 63.00: C-
        - 57.00 - 60.00: D+
        - 53.00 - 57.00: D
        - 50.00 - 53.00: D-
        """)

    with rs_col5:
        st.markdown("""
        - 45.00 - 50.00: E+
        - 35.00 - 45.00: E
        - 25.00 - 35.00: E-
        - Below 25.00: F
        """)
        

# --- DATAFRAME BEST TIME ---
df_records = df_records.query('Name == @athlete').sort_values(['Date'], ascending=False)
df_best_time = df_records

time = df_best_time['Record'].str.split(':', n=1, expand=True)
df_best_time['Record (s)'] = time[0].astype(float)*60 + time[1].astype(float)

idx = df_best_time.groupby('Event')['Record (s)'].idxmin()
df_best_time = df_best_time.loc[idx]
df_best_time.reset_index(drop=True, inplace=True)

df_best_time['Score'] = None
df_best_time['Rank'] = None

for idx, row in df_best_time.iterrows():
    _distance = row['Event'].split(' ')[0]
    _stroke = row['Event'].replace(f'{_distance} ', '').strip()

    stroke_mapping = {
        'FREE': 'Free',
        'BACK': 'Back',
        'FLY': 'Fly',
        'BREAST': 'Breast',
        'MEDLEY': 'IM'
    }

    # Iterate through the mapping dictionary
    for key, value in stroke_mapping.items():
        if key in _stroke:
            _stroke = value
            break
    
    _event = f'{_distance} {_stroke}'

    df_best_time.loc[idx, 'Score'] = df_stats[f'{_event} Score'][0]
    df_best_time.loc[idx, 'Rank'] = df_stats[f'{_event} Rank'][0]

df_best_time = df_best_time[['Event', 'Record', 'Competition', 'Date', 'Score', 'Rank']]

st.markdown("## Best Times")
st.dataframe(df_best_time, hide_index=True, use_container_width=True)

# --- Track Records ---
st.markdown("## Track Records")

event = st.selectbox(
    'Choose event:',
    options=sorted(df_records['Event'].unique())
)

time = df_records['Record'].str.split(':', n=1, expand=True)
df_records['Record (s)'] = time[0].astype(float)*60 + time[1].astype(float)

df_records = df_records.query('Event == @event')
df_progress = df_records.sort_values(['Date'])

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
                          categoryarray=y_labels)

fig_progress.update_xaxes(
    range=[
        max((datetime.datetime.strptime(df_records['Date'].max(), '%Y-%m-%d') - timedelta(days=367)), 
            (datetime.datetime.strptime(df_records['Date'].min(), '%Y-%m-%d') - timedelta(days=2))),
        datetime.datetime.strptime(df_records['Date'].max(), '%Y-%m-%d') + timedelta(days=2)
    ]
)

st.plotly_chart(fig_progress, use_container_width=True)

# --- Distance Statistic ---
st.markdown("## Distance Statistic")

distance1, distance2 = st.columns([1, 2])

with distance1:
    distance_data = {
        'Category': [f'50M Free ({df_stats["50M Free Rank"][0]})',
                    f'100M Free ({df_stats["100M Free Rank"][0]})',
                    f'200M Free ({df_stats["200M Free Rank"][0]})',
                    f'400M Free ({df_stats["400M Free Rank"][0]})',
                    f'800M Free ({df_stats["800M Free Rank"][0]})',
                    f'1500M Free ({df_stats["1500M Free Rank"][0]})'],
        'Values': [df_stats['50M Free Score'][0],
                df_stats['100M Free Score'][0],
                df_stats['200M Free Score'][0],
                df_stats['400M Free Score'][0],
                df_stats['800M Free Score'][0],
                df_stats['1500M Free Score'][0]]
    }

    df_distance = pd.DataFrame(distance_data)
    st.dataframe(df_distance.sort_values(['Values'], ascending=False), 
                 hide_index=True,
                 use_container_width=True)

with distance2:
    radar = px.line_polar(df_distance, r='Values', theta='Category', line_close=True)
    radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        polar_angularaxis=dict(
            tickfont=dict(size=24)
        ),
        showlegend=True
    )

    st.plotly_chart(radar)

# --- Stroke Statistic ---
st.markdown("## Stroke Statistic")

stroke1, stroke2 = st.columns([1, 2])

with stroke1:
    stroke_data1 = {
        'Category': ['Free', 'Back', 'Fly', 'Breast'],
        '50M': [df_stats['50M Free Score'][0],
                df_stats['50M Back Score'][0],
                df_stats['50M Fly Score'][0],
                df_stats['50M Breast Score'][0]]
    }

    stroke_data2 = {
        'Category': ['Free', 'Back', 'Fly', 'Breast'],
        '100M': [df_stats['100M Free Score'][0],
                 df_stats['100M Back Score'][0],
                 df_stats['100M Fly Score'][0],
                 df_stats['100M Breast Score'][0]]
    }

    df_stroke1 = pd.DataFrame(stroke_data1)
    df_stroke2 = pd.DataFrame(stroke_data2)
    df_stroke = df_stroke1.merge(df_stroke2, on='Category', how='left')
    df_stroke['Average'] = df_stroke[['50M', '100M']].mean(axis=1)
    df_stroke['Rank'] = df_stroke['Average'].apply(assign_rank)
    
    st.dataframe(df_stroke.sort_values(['Average'], ascending=False), 
                 hide_index=True,
                 use_container_width=True)

with stroke2:
    radar = px.line_polar(df_stroke, r='Average', theta='Category', line_close=True)
    radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        polar_angularaxis=dict(
            tickfont=dict(size=24)
        ),
        showlegend=True
    )

    st.plotly_chart(radar)

# --- Competitions ---
st.markdown("## Competitions")

df_records_comp = conn.read(worksheet='Records', usecols=list(range(0,7))).dropna(axis=0, how='all')
df_records_comp = df_records_comp.query('Name == @athlete').sort_values(['Date'], ascending=False)

competition = st.selectbox(
    'Choose competition:',
    options=df_records_comp['Competition'].unique()
)

df_records_comp = df_records_comp.query('Competition == @competition')
df_records_comp = df_records_comp.drop(columns=['Name', 'Sex', 'Year of Birth', 'Competition'])

df_records_comp['Performance'] = None 

for idx, row in df_records_comp.iterrows():
    _event = row['Event']
    _record = row['Record']

    best_time = df_best_time.query('Event == @_event')['Record'].values[0]

    if _record == best_time:
        df_records_comp.loc[idx, 'Performance'] = '🔥New Personal Best Time🔥'
    else:
        _record_s = _record.split(':')
        _record_s = float(_record_s[0])*60 + float(_record_s[1])

        best_time_s = best_time.split(':')
        best_time_s = float(best_time_s[0])*60 + float(best_time_s[1])

        diff = _record_s - best_time_s
        diff = round(diff, 2)
        diff_percent = (diff / best_time_s) * 100
        diff_percent = round(diff_percent, 2)
        if diff_percent <= 3.00:
            _emot = '🟡'
        elif diff_percent <= 5.00:
            _emot = '🟠'
        else:
            _emot = '🔴'

        df_records_comp.loc[idx, 'Performance'] = f'{diff} s ({diff_percent}%) Slower than PR {_emot}'

st.dataframe(df_records_comp, hide_index=True, use_container_width=True)

#  AI Analysis
st.markdown("## AI Analysis")
st.write('COMING SOON')

# if st.button('Analyze Athlete Stats'):
#     ai_analysis = analyze_athlete_stats(bio=athlete_data, stats=df_stats.to_dict(orient='records')[0])
#     st.write(json.loads(ai_analysis.text))