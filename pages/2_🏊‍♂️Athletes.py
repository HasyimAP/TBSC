import base64
import datetime
import streamlit as st

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

st.title('Athletes List')

conn = st.experimental_connection("gsheets", type=GSheetsConnection)

df_athletes = conn.read(worksheet='Athlete', usecols=list(range(0,5))).dropna(axis=0, how='all')
# df_records = conn.read(worksheet='Records', usecols=list(range(0,8)), ttl=5).dropna(axis=0, how='all')

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

df_athletes = df_athletes.sort_values(by=['Year of Birth', 'Sex'])
df_athletes = df_athletes[['Name', 'Sex', 'Year of Birth', 'Current Age', 'Age Group', 'Club', 'Province']]
st.dataframe(df_athletes.style.format({'Year of Birth': lambda x : '{:.0f}'.format(x)}), hide_index=True, use_container_width=True)

# gd = GridOptionsBuilder.from_dataframe(df_athletes)
# gd.configure_pagination(enabled=True)
# gd.configure_default_column(groupable=True)

# grid_options = gd.build()

# AgGrid(
#     df_athletes,
#     gridOptions=grid_options,
#     height=400
# )