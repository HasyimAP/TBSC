import json
import markdown2
import os
import shutil
import streamlit as st
import tempfile

from fpdf import FPDF
from PIL import Image


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
    # print(creds)
    for user in creds['usernames']:
        # print(creds['usernames'][user])
        creds['usernames'][user]['email'] = None
    # sanitized_creds = sanitize_creds(creds)

    with open(temp_file, 'w') as file:
        json.dump(creds, file)
        
    return temp_file, temp_dir

def delete_temp_credentials(temp_dir):
    shutil.rmtree(temp_dir)

def exception_handler(e):
    import sentry_sdk  # Needed because this is executed outside the current scope
    st.image(
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNmVic2t4aWozOTFibjJ3eXNrbDZ4a2RjazRocGI1N3djbHVpOWQyeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/UQVVaXJtC3LBLwHmTU/giphy.gif'
        'Y2lkPTc5MGI3NjExNmVic2t4aWozOTFibjJ3eXNrbDZ4a2RjazRocGI1N3djbHVpOWQyeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/UQVVaXJtC3LBLwHmTU/giphy.gif'
    )
    if sentry_sdk.is_initialized():
        st.error(
            f'Oops, something funny happened. We are looking into it. Please contact the admin.',
            icon='🙈',
        )
    else:
        st.write(e)
    
    raise e

def create_watermark(pdf: FPDF):
        watermark_image = 'images/logo_TBSC.jpeg'
        image = Image.open(watermark_image).convert("RGBA")
    
        alpha = image.split()[3]
        alpha = alpha.point(lambda p: p * 0.1) 
        image.putalpha(alpha)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            image.save(temp_file.name, format='PNG')
            watermark_image = temp_file.name

        with Image.open(watermark_image) as img:
            watermark_width, watermark_height = img.size
        
        if watermark_width > watermark_height:
            scale = pdf.w / watermark_width
            new_width = pdf.w/2
            new_height = (watermark_height * scale)/2
        else:
            scale = pdf.h / watermark_height
            new_width = (watermark_width * scale)/2
            new_height = pdf.h/2
        
        x_position = (pdf.w - new_width) / 2
        y_position = (pdf.h - new_height) / 2
        
        wm = {
            'wm': watermark_image,
            'x': x_position,
            'y': y_position,
            'w': new_width,
            'h': new_height
        }
        return wm

class PDF(FPDF):
    def __init__(self, watermark=None):
        super().__init__()
        self.watermark = watermark

    def header(self):
        # Add a watermark to each page
        if self.watermark:
            self.image(self.watermark['wm'], self.watermark['x'], self.watermark['y'], self.watermark['w'], self.watermark['h'])

def markdown_to_pdf(markdown_content: str):
    html_content = markdown2.markdown(markdown_content.strip(), extras=["tables"])

    pdf = PDF()
    wm_img = create_watermark(pdf)
    pdf.watermark = wm_img

    pdf.add_page()
    
    # Add HTML content to PDF
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("helvetica", size=12)
    pdf.write_html(html_content)
    # pdf.multi_cell(0, 10, html_content)
    
    return bytes(pdf.output())
    