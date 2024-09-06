import os
import base64
import streamlit as st

from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
icon = Image.open(BASE_DIR + '/images/logo_TBSC.jpeg')

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
[data-testid="stAppViewContainer"] {{
background-image: url("data:image/png;base64,{homepage_img}");
background-size: cover;
}}

[data-testid="stHeader"] {{
background: rgb(0, 0, 0, 0);
}}

[data-testid="stAppViewBlockContainer"] {{
background-color: #F0F2F6;
opacity: 0.7;
}}

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

st.title('Welcome to TBSC Dashboard')

'''
### Dive into Excellence with Us

Nestled on the stunning shores of Bali, Telaga Biru Swimming Club is not just a place to swim; it's a place where dreams take shape, where champions are nurtured, and where the joy of swimming knows no boundaries. Our club boasts a rich legacy of training professional athletes who have represented Bali and Indonesia on the international stage. But we're not just about medals and records; we're about sharing the profound love for the water with everyone who seeks it, regardless of age or experience.

### For Aspiring Professionals:

Are you an aspiring professional swimmer looking to hone your skills, break records, and make a splash on the world stage? At Telaga Biru Swimming Club, we offer world-class training programs led by experienced coaches who have produced champions. Join us in the pursuit of excellence.

### For Beginners of All Ages:

It's never too late to learn the art of swimming. Our club welcomes beginners of all ages, from toddlers to seniors. Our patient and skilled instructors will guide you through the journey of discovering the joy and confidence that comes with swimming.

Whether you're aiming for gold or simply want to enjoy the serenity of Bali's crystal-clear waters, Telaga Biru Swimming Club is your home away from home.

### What Sets Us Apart:

- **Expert Coaches**: Our dedicated team of coaches brings years of experience and a passion for swimming to every lesson.

- **Inclusive Community**: We're more than a club; we're a community. Join a supportive network of fellow swimmers who share your passion.

### Discover the Magic of Swimming

At Telaga Biru Swimming Club, we believe that the water holds the power to transform lives. Dive in with us, and let the journey begin. Whether you're an aspiring professional or a beginner taking your first strokes, Telaga Biru Swimming Club is here to make your swimming dreams come true. Join us today, and together, we'll explore the endless possibilities of the deep blue.

### Contact Us

- Instagram: [@telagabiruscbali](https://www.instagram.com/telagabiruscbali?igsh=NWFtMmY5NjdjODg1)
- Facebook: [Telaga Biru Bali](https://www.facebook.com/telaga.birubali?mibextid=JRoKGi)

Or reach our coaches:
- **Coach Gede Meiga**: [+62 896-3838-2625](https://wa.me/6289638382625)
- **Coach Arya**: [+62 821-4507-3356](https://wa.me/6282145073356)
- **Coach Komang**: [+62 896-0164-6224](https://wa.me/6289601646224)
- **Coach Hasyim**: [+62 895-4109-04253](https://wa.me/62895410904253)

'''
