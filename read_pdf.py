from datetime import datetime
import difflib
from typing import Optional
import pandas as pd
import PyPDF2
import re
import streamlit as st
import pdfplumber

from streamlit_gsheets import GSheetsConnection


pd.set_option('display.max_columns', None)

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
        event_regex = r'\d{2,4}\s?M\sGAYA\s?[A-Z -]+\b'
    else:
        event_regex = r'\d{2,4}\s?M\s?[A-Z -]+\b'
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

    date = ''

    df_athletes = conn.read(worksheet='Athlete').dropna(axis=0, how='all')
    df_athletes = df_athletes[~df_athletes['Status'].isin(['INACTIVE', 'TRANSFER'])]
    athlete_list = df_athletes['Name'].tolist()

    for line in lines:
        if any(word.upper() in line.upper() for word in ['ACARA', 'DICETAK', 'Sponsor', '27 - 29']):
            continue

        replacements = {
            # 'PT': 'PUTU',
            # 'MD': 'MADE',
            # 'KD': 'KADEK',
            'ABHIGAMEKA': 'ABHIGAMIKA'
        }

        for old, new in replacements.items():
            line = line.replace(old, new)
        
        event_match = re.search(event_regex, line)
        if event_match:
            event = event_match.group().replace(' M', 'M').replace('PUTRA', '').replace('PUTRI', '')
            if ind:
                for ind_event, eng_event in event_ind_to_eng.items():
                    event = event.replace(ind_event, eng_event)
        
        date_match = re.search(r'(\d{2}/08/2024)', line)
        if date_match:
            date = date_match.group()
        
        for s in athlete_list:
            record = {
                'Name': s.upper(),
                'Event': event,
                'Record': format_time(line.split(' ')[-1].strip()),
                'Date': date,
                'Competition': competition
            }

            name = s.strip().upper()
            # name_list = name.split(' ')
            # if len(name_list) > 3:
            #     name = ' '.join(name_list[:int(len(name_list) * 0.8)])
            # else:
            #     name = s.upper()
            
            if name in line.upper():
                data.append(record)
                continue
                
            elif 'TELAGA BIRU' in line:
                split_parts = re.split(r'\d+', line)
    
                text_parts = [part.strip() for part in split_parts if part.strip()]
                if text_parts[0] in s:
                    data.append(record)
                    continue

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
    
    if date_str:
        for indonesian_month, month_num in month_mapping.items():
            if indonesian_month in date_str:
                date_str = date_str.replace(indonesian_month, month_num)
                return datetime.strptime(date_str, '%d %m %Y')
    return date_str  # Return NaT if no match found

def check_total_athletes(input_file: str):
    athlete = []
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        if 'TELAGA BIRU' in line:

            split_parts = re.split(r'\d+', line)
    
            text_parts = [part.strip() for part in split_parts if part.strip()]
            name = text_parts[0].replace('PT', 'PUTU').replace('MD', 'MADE').replace('KD', 'KADEK')
            if any(keyword in name for keyword in ['TBSC', 'TELAGA BIRU', 'TEAM']):
                continue
            athlete.append(name)
        else:
            continue

    return set(athlete)

if __name__ == '__main__':
    event = 'Amarta Regis Cup 2024'
    pdf_path = f'full_result/{event}.pdf'
    txt_path = 'output.txt'

    conn = st.connection("gsheets", type=GSheetsConnection)

    # Open the PDF document

    with pdfplumber.open(pdf_path) as pdf, open(txt_path, 'w') as txt_file:
        for page in pdf.pages:
            text = page.extract_text()  # Extract text from the page
            if text:  # Check if there is any text
                lines = text.splitlines()  # Split the text into lines
                for line in lines:
                    txt_file.write(line + "\n")

    # refine_text_file(txt_path, txt_path)

    clean_data = process_txt_file(txt_path, event, ind=True)
    
    athletes = conn.read(worksheet='Athlete').dropna(axis=0, how='all').dropna(axis=1, how='all').astype(str)
    athletes = athletes[~athletes['Status'].isin(['INACTIVE', 'TRANSFER'])]
    print(athletes)
    print(athletes['Name'].unique().tolist())
    athletes['Year of Birth'] = athletes['Year of Birth'].astype(float).astype(int)
    clean_data = pd.merge(clean_data, athletes[['Name', 'Sex', 'Year of Birth']], how='left', on='Name')[['Name', 'Sex', 'Year of Birth', 'Event', 'Record', 'Date', 'Competition']]
    clean_data = clean_data.drop(index=0)
    # clean_data['Year of Birth'] = clean_data['Year of Birth'].astype(float).astype(int)

    # clean_data['Date'] = clean_data['Date'].replace('MARET', 'MEI')
    # clean_data['Date'] = clean_data['Date'].apply(convert_to_date).dt.date
    # clean_data['Date'] = pd.to_datetime(clean_data['Date'], format='%d/%m/%Y', utc=False).dt.date
    clean_data['Date'] = '2024-08-24'

    def format_record(time: str):
        try:
            time_list = time.split(':')
            second = '.'.join([time_list[1], time_list[2]])

            return ':'.join([time_list[0], second])
        except:
            return time
    clean_data['Record'] = clean_data['Record'].apply(format_record)
    
    print(clean_data)
    print('Total athlete: ', len(clean_data['Name'].unique()))
    print(sorted(clean_data['Name'].unique().tolist()))
    listed_athlete = check_total_athletes(txt_path)
    print('\nListed athlete: ', len(listed_athlete))
    print(sorted(listed_athlete))

    not_listed = []
    for name2 in listed_athlete:
        listed = False
        # matches = difflib.get_close_matches(name2, clean_data['Name'].unique().tolist(), n=1, cutoff=0.6)
        
        # if matches:
        #     listed = True
        
        if name2 in clean_data['Name'].unique().tolist():
            listed = True

        if not listed:
            for name in clean_data['Name'].unique().tolist():
                if name2 in name:
                    listed = True
        
        if not listed:
            not_listed.append(name2)

    not_listed = list(set(not_listed))

    print('\nNot listed athlete: ', len(not_listed))
    print(sorted(not_listed))

    clean_data.to_excel('check_sheets.xlsx', index=False)
    exit()
    df_records = conn.read(worksheet='Records', usecols=list(range(0,7))).dropna(axis=0, how='all')
    df_records = pd.concat([df_records, clean_data], ignore_index=True).drop_duplicates()
    
    conn.update(worksheet='Records', data=df_records)