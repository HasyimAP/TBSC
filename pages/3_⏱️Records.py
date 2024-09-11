import base64
import datetime
import logging
import sys
import pandas as pd
import sentry_sdk
import streamlit as st
import plotly.express as px

from PIL import Image
from pathlib import Path
from datetime import timedelta
from utilities import assign_rank
from streamlit_gsheets import GSheetsConnection


sentry_sdk.init()

def exception_handler(e):
    import sentry_sdk  # Needed because this is executed outside the current scope
    st.image(
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNmVic2t4aWozOTFibjJ3eXNrbDZ4a2RjazRocGI1N3djbHVpOWQyeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/UQVVaXJtC3LBLwHmTU/giphy.gif'
        'Y2lkPTc5MGI3NjExNmVic2t4aWozOTFibjJ3eXNrbDZ4a2RjazRocGI1N3djbHVpOWQyeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/UQVVaXJtC3LBLwHmTU/giphy.gif',
        use_column_width=True
    )

    if sentry_sdk.is_initialized():
        st.error(
            f'Oops, something funny happened. We are looking into it. Please contact the admin.',
            icon='🙈',
        )
    else:
        st.write(e)
    
    raise e

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
drop = ['DNS', 'DQ', 'NS', 'NSS']
df_records = df_records[~df_records['Record'].isin(drop)]
df_stats = conn.read(worksheet='Statistic').dropna(axis=0, how='all')
df_stats = df_stats.dropna(axis=1, how='all')

athlete = st.selectbox(
    'Choose athlete:',
    options=sorted(df_athletes['Name'].unique())
)

# --- Athlete Statistic ---
col1, col2 = st.columns([1,2])

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

# --- Track Records ---
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

fig_progress.update_xaxes(
    range=[
        max((datetime.datetime.strptime(df_records['Date'].max(), '%Y-%m-%d') - timedelta(days=367)), (datetime.datetime.strptime(df_records['Date'].min(), '%Y-%m-%d') - timedelta(days=2))),
        datetime.datetime.strptime(df_records['Date'].max(), '%Y-%m-%d') + timedelta(days=2)
    ]
)

st.plotly_chart(fig_progress, use_container_width=True)

# --- Distance Statistic ---
'''
## Distance Statistic
'''

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
            tickfont=dict(size=24)  # Adjust the size and weight (bold) of the text
        ),
        showlegend=True
    )

    st.plotly_chart(radar)

# --- Stroke Statistic ---
'''
## Stroke Statistic
'''

stroke1, stroke2 = st.columns([1, 2])

with stroke1:
    stroke_data1 = {
        'Category': ['Free',
                     'Back',
                     'Fly',
                     'Breast'],
        '50M': [df_stats['50M Free Score'][0],
                   df_stats['50M Back Score'][0],
                   df_stats['50M Fly Score'][0],
                   df_stats['50M Breast Score'][0]]
    }

    stroke_data2 = {
        'Category': ['Free',
                     'Back',
                     'Fly',
                     'Breast'],
        '100M': [df_stats['100M Free Score'][0],
                   df_stats['100M Back Score'][0],
                   df_stats['100M Fly Score'][0],
                   df_stats['100M Breast Score'][0]]
    }

    df_stroke1 = pd.DataFrame(stroke_data1)
    df_stroke2 = pd.DataFrame(stroke_data2)
    df_stroke = df_stroke1
    df_stroke = df_stroke.merge(df_stroke2, on='Category', how='left')
    df_stroke['Average'] = df_stroke[['50M', '100M']].mean(axis=1)
    df_stroke['Rank'] = df_stroke['Average'].apply(assign_rank)
    
    st.dataframe(df_stroke.sort_values(['Average'], ascending=False), 
                 hide_index=True,
                 use_container_width=True)

with stroke2:
    radar = px.line_polar(df_stroke, r='Average', theta='Category', line_close=True)
    # radar = radar.add_trace(px.line_polar(df_stroke2, r='Values 100M', theta='Category', line_close=True).data[0])
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

'''
## Competitions
'''

df_records = conn.read(worksheet='Records', usecols=list(range(0,7))).dropna(axis=0, how='all')

df_records = df_records.query(
    'Name == @athlete'
).sort_values(['Date'], ascending=False)

competition = st.selectbox(
    'Choose competition:',
    options=sorted(df_records['Competition'].unique())
)

df_records = df_records.query(
    'Competition == @competition'
)

df_records = df_records.drop(columns=[
    'Name',
    'Sex',
    'Year of Birth',
    'Competition'
])

st.dataframe(
    df_records,
    hide_index=True, 
    use_container_width=True
)