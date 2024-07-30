import json
import os
import shutil
import streamlit as st
import tempfile


def assign_rank(score):
    if score > 98.0:
        return 'EX'
    elif score > 95:
        return 'S+'
    elif score > 92.5:
        return 'S'
    elif score > 90:
        return 'S-'
    elif score > 87:
        return 'A+'
    elif score > 83:
        return 'A'
    elif score > 80:
        return 'A-'
    elif score > 77:
        return 'B+'
    elif score > 73:
        return 'B'
    elif score > 70:
        return 'B-'
    elif score > 67:
        return 'C+'
    elif score > 63:
        return 'C'
    elif score > 60:
        return 'C-'
    elif score > 57:
        return 'D+'
    elif score > 53:
        return 'D'
    elif score > 50:
        return 'D-'
    elif score > 45:
        return 'E+'
    elif score > 35:
        return 'E'
    elif score > 25:
        return 'E-'
    else:
        return 'F'
    
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

def sanitize_creds(creds: dict):
    sanitized_creds = {}
    for key, value in creds.items():
        if isinstance(value, dict):
            sanitized_creds[key] = sanitize_creds(value)
        elif isinstance(value, (str, int, float, bool, list)):
            sanitized_creds[key] = value
        else:
            sanitized_creds[key] = dict(value)  # Convert non-serializable values to strings
    return sanitized_creds

def create_temp_credentials():
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, 'temp_creds.json')
    
    creds = dict(st.secrets["credentials"])
    creds['usernames'] = creds['usernames'].to_dict()
    print(creds)
    print('====')
    # sanitized_creds = sanitize_creds(creds)

    with open(temp_file, 'w') as file:
        json.dump(creds, file)
        
    return temp_file, temp_dir

def delete_temp_credentials(temp_dir):
    shutil.rmtree(temp_dir)
