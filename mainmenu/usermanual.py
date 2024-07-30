import streamlit as st
import datetime
import base64
import os
import pdfplumber

# Set page configuration
st.set_page_config(
    page_title="निर्मल : User Manual",
    page_icon="🔄",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Sidebar customization
st.markdown(
    """
    <style>
        [data-testid=stSidebar] [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True
)

with st.sidebar:
    st.image('./Images/logo-white.png', width=150)

def get_current_year():
    return datetime.datetime.now().year

with st.sidebar:
    st.markdown(f"""<h6 style='text-align: center;'>Powergrid &copy; {get_current_year()} All rights reserved.</h6>""", unsafe_allow_html=True) 

def app():
    # Check if the user is authenticated
    if not st.session_state.get('authenticated', False):
        st.error(" 🔒 Please log in before accessing the resource.")
        return
    
    # Title and Description
    st.markdown("<h1 style='text-align: center;'>< निर्मल : User Manual ></h1>", unsafe_allow_html=True)
    st.write("---")
    st.write("")

    def show_pdf(file_path):
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    st.image(page.to_image(resolution=600).original)
        except Exception as e:
            st.error(f"Error loading PDF with pdfplumber: {e}")

    show_pdf("User Manual - Nirmal.pdf")
    st.write("")

    left_co, cent_co,last_co = st.columns(3)
    with cent_co:
        with open("User Manual - Nirmal.pdf", "rb") as file:
            st.download_button(
                    label="Download User Manual <📖>",
                    data=file,
                    file_name="Nirmal - User Manual.pdf",
                    mime="application/pdf"
                ) 
    st.write("---")
    st.write("")

if __name__ == "__page__":
    app()
