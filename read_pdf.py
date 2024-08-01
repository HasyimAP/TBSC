from datetime import datetime
from typing import Optional
import pandas as pd
import PyPDF2
import re
import streamlit as st

from streamlit_gsheets import GSheetsConnection


def refine_text_file(input_file, output_file):
    # Define patterns for valid line endings
    valid_endings = re.compile(r'(?:\d{2}\.\d{2}|DNS|DQ|FINAL|\(\w{3} \w{3}\))$')
    extra_newline_endings = re.compile(r'(?:LCM|SCM)$')
    
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Initialize list to hold processed lines
    processed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Check if the line ends with a valid pattern
        if valid_endings.search(line):
            processed_lines.append(line)
        else:
            # If the line does not end with a valid pattern, merge with next line
            while i + 1 < len(lines) and not valid_endings.search(lines[i].strip()):
                line += ' ' + lines[i + 1].strip()
                i += 1
            processed_lines.append(line)
        
        # Add extra newline after lines ending with 'LCM' or 'SCM'
        if extra_newline_endings.search(line):
            processed_lines.append('')  # Add an extra newline
        
        i += 1

    # Write the processed lines to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        for line in processed_lines:
            file.write(line + '\n')

def format_time(time_str: str):
    if len(time_str) == 5:
        return f'00:{time_str}'
    elif len(time_str) == 7:
        return f'0{time_str}'
    else:
        return time_str

def process_txt_file(input_file: str, competition: str, ind: bool = True):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    data = []

    if ind:
        event_regex = r'\b\d{2,4}\s?M\sGAYA\s[A-Z-]+\b'
    else:
        event_regex = r'\b\d{2,4}\s?M\s[A-Z-]+\b'
    event = ''
    
    event_ind_to_eng = {
        'GAYA KUPU-KUPU': 'BUTTERFLY',
        'GAYA BEBAS': 'FREESTYLE',
        'GAYA DADA': 'BREASTSTROKE',
        'GAYA GANTI': 'INDIVIDUAL MEDLEY',
        'GAYA KUPU KUPU': 'BUTTERFLY',
        'GAYA KUPU': 'BUTTERFLY',
        'GAYA PUNGGUNG': 'BACKSTROKE'
    }

    date_regex = r'(\d{1,2}\s\w+\s2024)'
    date = ''

    df_athletes = conn.read(worksheet='Athlete').dropna(axis=0, how='all')
    athlete_list = df_athletes['Name'].tolist()

    for line in lines:
        match = re.search(event_regex, line)
        if match:
            event = match.group().replace(' M', 'M')
            if ind:
                for ind_event, eng_event in event_ind_to_eng.items():
                    event = event.replace(ind_event, eng_event)
        
        match = re.findall(date_regex, line)
        if match:
            date = match[-1]

        for s in athlete_list:
            if s.upper() in line.upper():
                record = {
                    'Name': s.upper(),
                    'Event': event,
                    'Record': format_time(line.split(' ')[-1].strip()),
                    'Date': date,
                    'Competition': competition
                }
        
                data.append(record)

    df = pd.DataFrame(data)

    return df

def convert_to_date(date_str):
    month_mapping = {
        'JANUARI': '01',
        'FEBRUARI': '02',
        'MARET': '03',
        'APRIL': '04',
        'MEI': '05',
        'JUNI': '06',
        'JULI': '07',
        'AGUSTUS': '08',
        'SEPTEMBER': '09',
        'OKTOBER': '10',
        'NOVEMBER': '11',
        'DESEMBER': '12'
    }
    
    for indonesian_month, month_num in month_mapping.items():
        if indonesian_month in date_str:
            date_str = date_str.replace(indonesian_month, month_num)
            return datetime.strptime(date_str, '%d %m %Y')
    return date_str  # Return NaT if no match found


if __name__ == '__main__':
    
    pdf_path = 'full_result/AMREG FUN 2024.pdf'
    txt_path = 'output.txt'

    conn = st.connection("gsheets", type=GSheetsConnection)

    # Open the PDF document
    with open(pdf_path, 'rb') as pdf_file, open(txt_path, 'w', encoding='utf-8') as txt_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Iterate through each page
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()  # Extract text from the page
            lines = text.split('\n')
            for line in lines:
                txt_file.write(line + '\n')

    refine_text_file(txt_path, txt_path)

    clean_data = process_txt_file(txt_path, 'AMREG FUN 2024', ind=True)
    
    athletes = conn.read(worksheet='Athlete')
    clean_data = pd.merge(clean_data, athletes[['Name', 'Sex', 'Year of Birth']], how='left')[['Name', 'Sex', 'Year of Birth', 'Event', 'Record', 'Date', 'Competition']]
    clean_data['Year of Birth'] = clean_data['Year of Birth'].astype(int)

    # clean_data['Date'] = clean_data['Date'].replace('MARET', 'MEI')
    # clean_data['Date'] = clean_data['Date'].apply(convert_to_date).dt.date
    # clean_data['Date'] = pd.to_datetime(clean_data['Date'], format='%d %B %Y', utc=False).dt.date
    clean_data['Date'] = '2024-06-22'
    
    print(clean_data)

    # exit()
    df_records = conn.read(worksheet='Records', usecols=list(range(0,7))).dropna(axis=0, how='all')
    df_records = pd.concat([df_records, clean_data], ignore_index=True).drop_duplicates()
    
    conn.update(worksheet='Records', data=df_records)