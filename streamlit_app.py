import streamlit as st

# Define pages with titles and icons
login_page = st.Page("account/login.py", title="Log out", icon=":material/login:", default=True)

home_page = st.Page("mainmenu/home.py", title="Home", icon=":material/home:")
mis_page = st.Page("mainmenu/mis.py", title="MIS", icon=":material/settings:")
dashboard_page = st.Page("mainmenu/dashboard.py", title="Dashboard", icon=":material/dashboard:")
usermanual_page = st.Page("mainmenu/usermanual.py", title="User Manual", icon=":material/menu_book:")

word_to_pdf_page = st.Page("convertfiles/word_to_pdf.py", title="Word to PDF", icon=":material/description:")
png_to_pdf_page = st.Page("convertfiles/png_to_pdf.py", title="PNG to PDF", icon=":material/description:")
jpg_to_pdf_page = st.Page("convertfiles/jpg_to_pdf.py", title="JPG to PDF", icon=":material/description:")
excel_to_pdf_page = st.Page("convertfiles/excel_to_pdf.py", title="Excel to PDF", icon=":material/picture_as_pdf:")
pdf_to_jpg_page = st.Page("convertfiles/pdf_to_jpg.py", title="PDF to JPG", icon=":material/picture_as_pdf:")

merge_pdf_page = st.Page("pdfop/merge_pdf.py", title="Merge PDFs", icon=":material/merge_type:")
protect_pdf_page = st.Page("pdfop/protect_pdf.py", title="Protect PDF", icon=":material/lock:")
unlock_pdf_page = st.Page("pdfop/unlock_pdf.py", title="Unlock PDF", icon=":material/lock_open:")
organise_pdf_page = st.Page("pdfop/organise_pdf.py", title="Organise PDF", icon=":material/folder:")
split_pdf_page = st.Page("pdfop/split_pdf.py", title="Split PDF", icon=":material/vertical_split:")
extract_pdf_page = st.Page("pdfop/extract_pdf.py", title="Extract PDF", icon=":material/filter_frames:")
compress_pdf_page = st.Page("pdfop/compress_pdf.py", title="Compress PDF", icon=":material/compress:")
watermark_pdf_page = st.Page("pdfop/watermark_pdf.py", title="Watermark PDF", icon=":material/water_drop:")
sign_pdf_page = st.Page("pdfop/sign_pdf.py", title="Sign PDF", icon=":material/draw:")



# Initialize session state for authentication status
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Set up navigation with sections and pages
if st.session_state.authenticated:
    st.session_state.runpage = dashboard_page
    pg = st.navigation(
        {
            "Account": [login_page],
            "Menu Options": [home_page, mis_page , dashboard_page , usermanual_page],
            "PDF Operations": [merge_pdf_page, compress_pdf_page , sign_pdf_page, watermark_pdf_page, organise_pdf_page, split_pdf_page, extract_pdf_page, protect_pdf_page, unlock_pdf_page],
            "Convert Files": [word_to_pdf_page, jpg_to_pdf_page, png_to_pdf_page, pdf_to_jpg_page, excel_to_pdf_page]
        }
    )
else:
    pg = st.navigation([login_page])

# Set the Powergrid logo
st.logo("Images/powergrid.webp")

# Run the navigation
pg.run()
