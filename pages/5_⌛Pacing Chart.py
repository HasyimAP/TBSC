import os
import base64
import re
import pandas as pd
import streamlit as st
import tempfile

from PIL import Image
from fpdf import FPDF
from pathlib import Path
from streamlit_gsheets import GSheetsConnection

BASE_DIR = Path(__file__).parent.parent
icon = Image.open(BASE_DIR / 'images/logo_TBSC.jpeg')

st.set_page_config(
    page_title='TBSC Dashboard',
    page_icon=icon,
    layout='centered'
)

@st.cache_data
def get_img_as_base64(file):
    with open(file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

homepage_img = get_img_as_base64('images/main_page.jpg')
sidebar_img = get_img_as_base64('images/sidebar.jpg')

page_bg_img = f'''
<style>
# [data-testid="stAppViewContainer"] {{
# background-image: url("data:image/png;base64,{homepage_img}");
# background-size: cover;
# }}

# [data-testid="stHeader"] {{
# background: rgb(0, 0, 0, 0);
# }}

# [data-testid="stAppViewBlockContainer"] {{
# background-color: #F0F2F6;
# opacity: 0.7;
# }}

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

# st.title('Coming Soon...')

st.title('Pacing Charts')

conn = st.connection("gsheets", type=GSheetsConnection)

df_athletes = conn.read(worksheet='Athlete', usecols=list(range(0,6))).dropna(axis=0, how='all')
df_records = conn.read(worksheet='Records', usecols=list(range(0,7))).dropna(axis=0, how='all')
drop = ['DNS', 'DQ', 'NS', 'NSS']
df_records = df_records[~df_records['Record'].isin(drop)]

athlete = st.selectbox(
    'Choose athlete:',
    options=sorted(df_athletes['Name'].unique())
)

df_records = df_records.query(
    'Name == @athlete'
).sort_values(['Date'], ascending=False)

df_best_time = df_records

time = df_best_time['Record'].str.split(':', n=1, expand=True)
df_best_time['Record (s)'] = time[0].astype(float)*60 + time[1].astype(float)

idx = df_best_time.groupby('Event')['Record (s)'].idxmin()
df_best_time = df_best_time.loc[idx]
df_best_time.reset_index(drop=True, inplace=True)

event = st.selectbox(
    'Choose event:',
    options=sorted(df_best_time['Event'].unique())
)

best_time = df_best_time.query(
    'Event == @event'
)['Record (s)'].values[0]

match = re.search(r'(\d+)m?', event)

col1, col2 = st.columns(2)

distance = int(match.group(1))
best_speed = distance/best_time
target_speed = 1.02 * best_speed
target_time = round(distance/target_speed, 2)
diff = best_time-target_time

with col1:
    f'''
    Best Time:

        {int(best_time//60):02}:{(best_time%60):05.2f}

    Best Speed:

        {round(best_speed, 2)} m/s

    Improvement:

        2%
    '''

with col2:
    f'''
    Target Time:

        {int(target_time//60):02}:{(target_time%60):05.2f}

    Target Speed:

        {round(target_speed, 2)} m/s

    Diff:

        {round(diff, 2)} s
    '''

pace_chart = pd.DataFrame(columns=[event])
pace_chart[event] = [f'{x}%' for x in range(100, 59, -5)]
pace_chart['Personal best (s)'] = pace_chart[event].apply(lambda x: round(best_time + best_time*(1-((float(x.strip('%'))/100))), 2))
pace_chart['Target time (s)'] = pace_chart[event].apply(lambda x: round(target_time + target_time*(1-((float(x.strip('%'))/100))), 2))
pace_chart['Diff from PB'] = pace_chart['Personal best (s)'].apply(lambda x: f'+ {round(x - pace_chart[pace_chart[event] == "100%"]['Personal best (s)'].values[0], 2)}')
pace_chart['Diff from TT'] = pace_chart['Target time (s)'].apply(lambda x: f'+ {round(x - pace_chart[pace_chart[event] == "100%"]['Target time (s)'].values[0], 2)}')

pace_chart['PB min'] = pace_chart['Personal best (s)'] // 60
pace_chart['PB sec'] = pace_chart['Personal best (s)'] % 60
pace_chart['Personal best'] = pace_chart['PB min'].apply(lambda x: f'{int(x):02}') + ':' + pace_chart['PB sec'].apply(lambda x: f'{x:05.2f}')

pace_chart['TT min'] = pace_chart['Target time (s)'] // 60
pace_chart['TT sec'] = pace_chart['Target time (s)'] % 60
pace_chart['Target time'] = pace_chart['TT min'].apply(lambda x: f'{int(x):02}') + ':' + pace_chart['TT sec'].apply(lambda x: f'{x:05.2f}')

pace_chart = pace_chart[[
    event,
    'Personal best',
    'Diff from PB',
    'Target time',
    'Diff from TT'
]]

st.dataframe(
    pace_chart,
    hide_index=True
)

col3, col4 = st.columns(2)

with col3:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
        excel_chart = pace_chart.to_excel(temp_file.name, index=False, engine='openpyxl')
        excel_file_path = temp_file.name
    with open(excel_file_path, 'rb') as file:
        st.download_button(
            label='Download chart as Excel',
            data=file,
            file_name=f'{athlete} {event}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

with col4:
    def df_to_pdf(dataframe: pd.DataFrame):
        pdf = FPDF()
        pdf.add_page()
        
        # Font and size
        pdf.set_font('Arial', size=12)
        
        # Title
        pdf.cell(200, 10, txt=athlete, ln=True, align='C')
        pdf.ln(5)

        col_widths = [max(pdf.get_string_width(str(dataframe[col].max()))+6, pdf.get_string_width(col)+6) for col in dataframe.columns]
        total_width = sum(col_widths) + len(col_widths)
        page_width = pdf.w - pdf.l_margin - pdf.r_margin
        start_x = (page_width - total_width)

        pdf.set_x(start_x)

        # Column names 
        pdf.set_font('Arial', 'B', size=12)  # Bold font for headers
        for i, col in enumerate(dataframe.columns):
            pdf.cell(col_widths[i], 10, col, 1, align='C')
        pdf.ln()
        
        # Row data
        pdf.set_font('Arial', size=12)  # Regular font for data
        for index, row in dataframe.iterrows():
            pdf.set_x(start_x)
            for i, col in enumerate(dataframe.columns):
                pdf.cell(col_widths[i], 10, str(row[col]), 1, align='C')
            pdf.ln()
        
        return pdf.output(dest='S').encode('latin1')
    
    pdf_bytes = df_to_pdf(pace_chart)

    st.download_button(
        label="Download chart as PDF",
        data=pdf_bytes,
        file_name=f'{athlete} {event}.pdf',
        mime='application/pdf'
    )