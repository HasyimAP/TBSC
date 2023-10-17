import base64
import streamlit as st
import plotly.express as px

from PIL import Image
from pathlib import Path
from st_aggrid import AgGrid, GridOptionsBuilder
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

athlete = st.selectbox(
    'Choose athlete:',
    options=sorted(df_athletes['Name'].unique())
)

df_records = df_records.query(
    'Name == @athlete'
).sort_values(['Date'], ascending=False)

# Show the table
st.dataframe(
    df_records.style.format({'Year of Birth': lambda x : '{:.0f}'.format(x)}),
    hide_index=True, 
    use_container_width=True
)

# gd = GridOptionsBuilder.from_dataframe(df_records)
# gd.configure_default_column(groupable=True)

# grid_options = gd.build()

# AgGrid(df_records, 
#        gridOptions=grid_options,
#        height=250)

# Track Records
st.header('Track Records')

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
                    #    color='Name', 
                    #    width=1280, 
                    #    height=480,
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