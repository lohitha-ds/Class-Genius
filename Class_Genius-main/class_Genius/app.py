import streamlit as st
import os
from ocr_pdf import image_to_pdf
from email_service import send_email
from web_scrape import get_resources
from face_recognition_ui import render_face_recognition_section
from attendance_ui import render_attendance_integration_section
from database import conn, c



st.set_page_config("Class Genius", layout="wide", initial_sidebar_state="collapsed")


# Add Font Awesome CDN
st.markdown("""
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
""", unsafe_allow_html=True)


# ================= ENHANCED STYLES =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@import 'https://cdn.tailwindcss.com';
html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%) !important;
    min-height: 100vh;
    color: #1a1a1a !important;
}
.glass-effect {
    backdrop-filter: blur(10px);
    background: rgba(255, 255, 255, 0.98);
    border: 2px solid #e0e0e0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border-radius: 16px;
    padding: 24px;
}
.gradient-bg { background: linear-gradient(135deg, #000000 0%, #333333 100%) !important; }
.upload-area {
    transition: all 0.3s ease;
    border: 3px dashed #000000;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 12px;
    padding: 30px;
    text-align: center;
}
.upload-area:hover {
    border-color: #333333 !important;
    background: rgba(0, 0, 0, 0.1) !important;
    transform: scale(1.02);
}
.btn-primary {
    background: linear-gradient(135deg, #000000 0%, #333333 100%) !important;
    transition: all 0.3s ease !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    padding: 12px 32px !important;
    border-radius: 8px !important;
}
.btn-primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important;
}
.btn-secondary {
    background: #ffffff !important;
    border: 2px solid #000000 !important;
    color: #000000 !important;
    transition: all 0.3s ease !important;
    font-weight: 700 !important;
    padding: 12px 32px !important;
    border-radius: 8px !important;
}
.btn-secondary:hover {
    background: #000000 !important;
    border-color: #000000 !important;
    color: #ffffff !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important;
}
.fade-in { animation: fadeIn 0.6s ease-in; }
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}
.navbar {
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(20px);
    background: rgba(255, 255, 255, 0.99);
    border-bottom: 2px solid #e0e0e0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    padding: 16px 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
/* NAV BUTTONS (Emoji buttons) */
.nav-right a {
    background-color: #000000 !important;
    color: #ffffff !important;        /* WHITE TEXT */
    padding: 10px 22px;
    border-radius: 10px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    border: 2px solid #000000;
}

/* Emoji inside nav buttons */
.nav-right a span,
.nav-right a i {
    color: #ffffff !important;        /* WHITE EMOJIS */
}

/* Hover effect */
.nav-right a:hover {
    background-color: #ffffff !important;
    color: #000000 !important;
}

/* Hover emoji color */
.nav-right a:hover span,
.nav-right a:hover i {
    color: #000000 !important;
}

.pulse { animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.7; } }
.block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
.stButton > button { 
    border-radius: 8px !important; 
    font-weight: 700 !important;
    padding: 12px 24px !important;
    background-color: #000000 !important;
    color: #ffffff !important;
}
.stButton > button:hover {
    background-color: #333333 !important;
    color: #ffffff !important;
}
.stTextInput > div > div > input, .stTextArea > div > textarea {
    border-radius: 8px !important;
    border: 2px solid #d0d0d0 !important;
    padding: 12px 16px !important;
    background: #ffffff !important;
    color: #1a1a1a !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus, .stTextArea > div > textarea:focus {
    border-color: #000000 !important;
    box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1) !important;
    background: #ffffff !important;
    color: #1a1a1a !important;
}
.card {
    background: #ffffff;
    border-radius: 12px !important;
    padding: 24px !important;
    border: 2px solid #e0e0e0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    margin-bottom: 24px !important;
    color: #1a1a1a !important;
}
.hero-card {
    background: linear-gradient(135deg, #ffffff, #f9f9f9);
    border-radius: 16px !important;
    padding: 48px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    border: 2px solid #e0e0e0;
    color: #1a1a1a !important;
    text-align: center;
}
.feature-card {
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border-radius: 12px !important;
    background: #ffffff !important;
    border: 2px solid #e0e0e0 !important;
    padding: 24px !important;
}
.feature-card:hover {
    transform: translateY(-8px) !important;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.12) !important;
    border-color: #000000 !important;
}
.success-bg { background: linear-gradient(135deg, #10b981, #059669) !important; }
.error-bg { background: linear-gradient(135deg, #ef4444, #dc2626) !important; }
.center-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
.stDownloadButton > button {
    background-color: #000000 !important;
    color: #ffffff !important;
    border: 2px solid #000000 !important;
    font-weight: 600;
}

}
</style>
""", unsafe_allow_html=True)


# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None
if "page" not in st.session_state:
    st.session_state.page = "home"


# Handle page parameter from URL
params = st.query_params
if "page" in params:
    st.session_state.page = params.get("page", "home")


# ================= COMPONENTS =================
def render_navbar(role=None):
    """Modern navbar"""
    st.markdown("""
    <nav class="navbar">
        <div class="flex items-center">
            <h1 class="text-3xl font-bold text-black" style="margin: 0; display: flex; align-items: center;">
                <i class="fas fa-graduation-cap mr-3"></i>Class Genius
            </h1>
        </div>
    </nav>
    """, unsafe_allow_html=True)
   
    if role == "admin":
        col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1.2, 1.2, 1.2, 1.2, 1.2, 0.8])
        with col1: pass
        with col2:
            if st.button("🏠 Home", use_container_width=True, key="nav_home", help="Dashboard"):
                st.session_state.page = "home"
                st.query_params["page"] = "home"
                st.rerun()
        with col3:
            if st.button("📤 Upload", use_container_width=True, key="nav_upload", help="Upload Notes"):
                st.session_state.page = "upload"
                st.query_params["page"] = "upload"
                st.rerun()
        with col4:
            if st.button("😊 Face Rec", use_container_width=True, key="nav_face", help="Face Recognition"):
                st.session_state.page = "face_recognition"
                st.query_params["page"] = "face_recognition"
                st.rerun()
        with col5:
            if st.button("📋 Attendance", use_container_width=True, key="nav_attend", help="Attendance Integration"):
                st.session_state.page = "attendance"
                st.query_params["page"] = "attendance"
                st.rerun()
        with col6:
            if st.button("📧 Absentees", use_container_width=True, key="nav_absent", help="Send Notes"):
                st.session_state.page = "absentees"
                st.query_params["page"] = "absentees"
                st.rerun()
        with col7:
            if st.button("🚪 Exit", use_container_width=True, key="nav_logout"):
                st.session_state.user = None
                st.session_state.role = None
                st.query_params.clear()
                st.rerun()
    elif role == "student":
        col1, col2, col3, col4, col5 = st.columns([3, 1.5, 1.5, 1.5, 1])
        with col1: pass
        with col2:
            if st.button("🏠 Home", use_container_width=True, key="nav_shome"):
                st.session_state.page = "home"
                st.query_params["page"] = "home"
                st.rerun()
        with col3:
            if st.button("📖 Notes", use_container_width=True, key="nav_notes"):
                st.session_state.page = "notes"
                st.query_params["page"] = "notes"
                st.rerun()
        with col4:
            if st.button("🔍 Search", use_container_width=True, key="nav_web"):
                st.session_state.page = "web"
                st.query_params["page"] = "web"
                st.rerun()
        with col5:
            if st.button("🚪 Logout", use_container_width=True, key="nav_slogout"):
                st.session_state.user = None
                st.session_state.role = None
                st.query_params.clear()
                st.rerun()


def hero_section():
    """Modern hero with features"""
    st.markdown("""
    <div class="text-center py-16 fade-in">
        <h1 class="text-6xl md:text-7xl font-bold text-black mb-6 px-4">
            Class Genius
        </h1>
        <p class="text-2xl text-gray-700 mb-12 max-w-4xl mx-auto leading-relaxed px-4" style="margin-left: auto; margin-right: auto;">
            Transform classroom boards into perfect PDFs • Auto-deliver notes • Smart learning resources
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        st.markdown("""
        <div class="feature-card shadow-lg">
            <h3 class="text-2xl font-bold text-black mb-4" style="text-align: left;">Board to PDF</h3>
            <p class="text-base text-gray-600 leading-relaxed" style="text-align: left;">Convert handwritten boards to clean, shareable PDFs instantly</p>
        </div>
        """, unsafe_allow_html=True)
   
    with col2:
        st.markdown("""
        <div class="feature-card shadow-lg">
            <h3 class="text-2xl font-bold text-black mb-4" style="text-align: left;">Auto Email</h3>
            <p class="text-base text-gray-600 leading-relaxed" style="text-align: left;">Send notes to absentees automatically using roll numbers</p>
        </div>
        """, unsafe_allow_html=True)
   
    with col3:
        st.markdown("""
        <div class="feature-card shadow-lg">
            <h3 class="text-2xl font-bold text-black mb-4" style="text-align: left;">Smart Search</h3>
            <p class="text-base text-gray-600 leading-relaxed" style="text-align: left;">Find best learning resources from web & YouTube instantly</p>
        </div>
        """, unsafe_allow_html=True)


# ================= ROLE SELECTION =================
def role_selection():
    render_navbar()
    st.markdown("""
    <div class="glass-effect max-w-2xl mx-auto rounded-3xl shadow-lg fade-in my-20" style="text-align: center; margin-top: 80px;">
        <div class="center-content mb-12">
            <h2 class="text-4xl font-bold text-black mb-4" style="text-align: center;">Welcome to Class Genius</h2>
            <p class="text-xl text-gray-700 mb-12" style="text-align: center;">Choose your role to continue</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
   
    st.write("")
    st.write("")
    col1, col2, col3 = st.columns([1, 1.5, 1])
   
    with col2:
        st.markdown("""<div style="display: flex; flex-direction: column; gap: 16px;">""", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2, gap="small")
        with col_btn1:
            if st.button("👨‍🏫 Admin", use_container_width=True, key="admin_btn"):
                st.session_state.role = "admin"
                st.session_state.user = "admin"
                st.rerun()
   
        with col_btn2:
            if st.button("👨‍🎓 Student", use_container_width=True, key="student_btn"):
                st.session_state.role = "student"
                st.session_state.user = "student"
                st.rerun()
        st.markdown("""</div>""", unsafe_allow_html=True)
   
    


# ================= ADMIN PANEL =================
def admin_panel():
    render_navbar("admin")
   
    if st.session_state.page == "home":
        st.markdown("""
        <div class="hero-card max-w-4xl mx-auto fade-in" style="margin: 40px auto; text-align: center;">
            <h1 class="text-5xl font-bold text-black mb-6" style="text-align: center;">Welcome Admin!</h1>
            <p class="text-2xl text-gray-700 mb-12 leading-relaxed" style="text-align: center;">Powerful tools to manage classroom notes and reach every student</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 32px;">
                <a href="#" onclick="window.location.href='?page=upload'" class="btn-primary text-lg py-4 px-8 rounded-lg font-bold shadow-md block no-underline" style="background: linear-gradient(135deg, #000000 0%, #333333 100%); color: white; text-decoration: none; display: flex; align-items: center; justify-content: flex-start; gap: 12px; padding-left: 24px;">
                    Upload Notes
                </a>
                <a href="#" onclick="window.location.href='?page=absentees'" class="btn-secondary text-lg py-4 px-8 rounded-lg font-bold shadow-md block no-underline" style="background: white; border: 2px solid #000000; color: #000000; text-decoration: none; display: flex; align-items: center; justify-content: flex-start; gap: 12px; padding-left: 24px;">
                    Absentees
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
   
    elif st.session_state.page == "upload":
        st.markdown("""
        <div class="max-w-3xl mx-auto">
            <div class="glass-effect rounded-lg shadow-lg fade-in mb-12" style="padding: 32px; margin-top: 24px;">
                <div class="text-center mb-12">
                    <h1 class="text-4xl font-bold text-black mb-4" style="text-align: center;">Upload Classroom Board</h1>
                    <p class="text-2xl text-gray-700" style="text-align: center;">Capture or upload → OCR → Perfect PDF</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
       
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown("""
            <div class="upload-area" style="background: rgba(0, 0, 0, 0.05); border: 3px dashed #000000; padding: 48px 24px; border-radius: 12px; text-align: center;">
                <p class="text-2xl font-bold text-black mb-2" style="text-align: center;">Browse Files</p>
                <p class="text-base text-gray-600" style="text-align: center;">PNG, JPG, JPEG (up to 10MB)</p>
            </div>
            """, unsafe_allow_html=True)
            img = st.file_uploader("", type=["png", "jpg", "jpeg"], key="file_upload")
       
        with col2:
            st.markdown("""
            <div class="upload-area" style="background: rgba(0, 0, 0, 0.05); border: 3px dashed #000000; padding: 48px 24px; border-radius: 12px; text-align: center;">
                <p class="text-2xl font-bold text-black mb-2" style="text-align: center;">Take Photo</p>
                <p class="text-base text-gray-600" style="text-align: center;">Live camera capture</p>
            </div>
            """, unsafe_allow_html=True)
            camera_img = st.camera_input("", key="camera_upload")
       
        img_to_process = img if img else camera_img
       
        if img_to_process:
            st.markdown("""
            <hr class="my-12 border-2 border-gray-200">
            <div class="glass-effect p-8 rounded-3xl mb-8">
                <h3 class="text-3xl font-bold text-gray-800 mb-4 text-center">✏️ Name Your PDF</h3>
            </div>
            """, unsafe_allow_html=True)
           
            pdf_name = st.text_input(
                "Enter PDF name (no extension needed)",
                placeholder="Lecture_01, Chapter_2_Notes, Exam_Review",
                label_visibility="collapsed"
            )
           
            col1, col2 = st.columns([3,1])
            with col1:
                if st.button("✨ Generate PDF", use_container_width=True, type="primary"):
                    if pdf_name.strip():
                        os.makedirs("notes", exist_ok=True)
                       
                        temp_img_name = img.name if img else f"board_{len(os.listdir('notes'))}.png"
                        temp_img_path = os.path.join("notes", f"temp_{temp_img_name}")
                       
                        with open(temp_img_path, "wb") as f:
                            f.write(img_to_process.getbuffer())
                       
                        pdf_path = os.path.join("notes", f"{pdf_name.strip()}.pdf")
                        image_to_pdf(temp_img_path, pdf_path)
                       
                        try:
                            os.remove(temp_img_path)
                            c.execute("INSERT INTO notes(filename) VALUES (?)", (pdf_path,))
                            conn.commit()
                           
                            st.markdown("""
                            <div class="success-bg text-white p-12 rounded-3xl text-center shadow-2xl fade-in">
                                <i class="fas fa-check-circle text-7xl mb-6"></i>
                                <h2 class="text-4xl font-bold mb-4">PDF Created Successfully!</h2>
                                <p class="text-2xl">Your classroom notes are ready to share</p>
                            </div>
                            """, unsafe_allow_html=True)
                           
                            col_dl, col_send = st.columns(2)
                            with col_dl:
                                with open(pdf_path, "rb") as file:
                                    st.download_button(
                                        f"📥 Download PDF",
                                        file,
                                        file_name=os.path.basename(pdf_path),
                                        use_container_width=True
                                    )
                            with col_send:
                                if st.button("📧 Send to Absentees", use_container_width=True):
                                    st.session_state.page = "absentees"
                                    st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                    else:
                        st.error("⚠️ Please enter a PDF name")
   
    elif st.session_state.page == "absentees":
        st.markdown("""
        <div class="max-w-2xl mx-auto">
            <div class="glass-effect p-12 rounded-3xl shadow-2xl fade-in">
                <div class="text-center mb-12">
                    <i class="fas fa-users text-6xl text-indigo-600 mb-6"></i>
                    <h1 class="text-4xl font-bold text-gray-800 mb-4">Send Notes to Absentees</h1>
                    <p class="text-xl text-gray-600">Enter roll numbers (comma separated)</p>
                </div>
                <div class="bg-gradient-to-r from-blue-50 to-indigo-50 p-8 rounded-3xl mb-8 glass-effect">
                    <p class="text-lg font-semibold text-gray-800 mb-3">💡 Example:</p>
                    <p class="font-mono text-xl bg-white px-4 py-2 rounded-2xl">23b01a0598, 23b01a0601, 23b01a0623</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
       
        rolls = st.text_area(
            "Roll Numbers",
            placeholder="23b01a0598, 23b01a0601, 23b01a0615, 23b01a0702",
            label_visibility="collapsed",
            help="Emails sent to: rollnumber@svecw.edu.in"
        )
       
        if st.button("🚀 Send Notes Now", use_container_width=True, type="primary"):
            roll_list = [r.strip() for r in rolls.split(",") if r.strip()]
           
            if not roll_list:
                st.warning("⚠️ Please enter roll numbers")
            else:
                c.execute("SELECT filename FROM notes ORDER BY id DESC LIMIT 1")
                row = c.fetchone()
               
                if row:
                    send_email(roll_list, row[0])
                    st.markdown("""
                    <div class="success-bg text-white p-12 rounded-3xl text-center shadow-2xl">
                        <i class="fas fa-paper-plane text-7xl mb-6"></i>
                        <h2 class="text-4xl font-bold mb-4">Notes Sent Successfully!</h2>
                        <p class="text-2xl">📧 Delivered to all specified students</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="error-bg text-white p-12 rounded-3xl text-center shadow-2xl">
                        <i class="fas fa-exclamation-triangle text-7xl mb-6"></i>
                        <h2 class="text-4xl font-bold mb-4">No PDF Available</h2>
                        <p class="text-2xl">Upload notes first using Upload page</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    elif st.session_state.page == "face_recognition":
        render_face_recognition_section()
    
    elif st.session_state.page == "attendance":
        render_attendance_integration_section()


# ================= STUDENT PANEL =================
def student_panel():
    render_navbar("student")
   
    if st.session_state.page == "home":
        st.markdown("""
        <div class="hero-card max-w-4xl mx-auto text-center fade-in">
            <i class="fas fa-user-graduate text-7xl text-emerald-600 mb-8"></i>
            <h1 class="text-5xl font-bold text-gray-800 mb-6">Welcome Student!</h1>
            <p class="text-2xl text-gray-600 mb-12 leading-relaxed">Your complete learning hub - notes, resources, anytime access</p>
            <div class="grid md:grid-cols-2 gap-8 mt-16 text-left">
                <div class="glass-effect p-10 rounded-3xl cursor-pointer hover:shadow-2xl transition-all">
                    <i class="fas fa-file-pdf text-5xl text-orange-500 mb-6"></i>
                    <h3 class="text-3xl font-bold mb-4">📚 Class Notes</h3>
                    <p class="text-xl text-gray-600">Download all professor-uploaded PDFs</p>
                </div>
                <div class="glass-effect p-10 rounded-3xl cursor-pointer hover:shadow-2xl transition-all">
                    <i class="fas fa-search text-5xl text-purple-500 mb-6"></i>
                    <h3 class="text-3xl font-bold mb-4">🔍 Smart Search</h3>
                    <p class="text-xl text-gray-600">Instant learning resources from web & YouTube</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
   
    elif st.session_state.page == "notes":
        st.markdown("""
        <div class="max-w-6xl mx-auto">
            <div class="glass-effect p-12 rounded-3xl shadow-2xl mb-12 fade-in">
                <div class="text-center">
                    <i class="fas fa-file-pdf text-6xl text-orange-500 mb-6"></i>
                    <h1 class="text-5xl font-bold text-gray-800 mb-6">📚 Class Notes</h1>
                    <p class="text-2xl text-gray-600">All your lecture materials in one place</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
       
        c.execute("SELECT DISTINCT filename FROM notes")
        files = c.fetchall()
       
        if not files:
            st.markdown("""
            <div class="glass-effect p-20 rounded-3xl text-center fade-in max-w-2xl mx-auto">
                <i class="fas fa-clock text-8xl text-gray-400 mb-8"></i>
                <h2 class="text-4xl font-bold text-gray-500 mb-6">No Notes Yet</h2>
                <p class="text-2xl text-gray-400">Notes will appear here when professors upload them</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for i, (f,) in enumerate(files):
                if f.endswith(".pdf") and os.path.exists(f):
                    col1, col2 = st.columns([4,1])
                    with col1:
                        st.markdown(f"""
                        <div class="glass-effect p-8 rounded-2xl mb-6 feature-card">
                            <div class="flex items-center">
                                <i class="fas fa-file-pdf text-4xl text-orange-500 mr-6"></i>
                                <div>
                                    <h3 class="text-2xl font-bold text-gray-800 mb-1">{os.path.basename(f)}</h3>
                                    <p class="text-lg text-gray-500">Ready to download</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        with open(f, "rb") as file:
                            st.download_button(
                                "📥",
                                file,
                                file_name=os.path.basename(f),
                                key=f"student_pdf_{i}"
                            )
   
    elif st.session_state.page == "web":
        st.markdown("""
        <div class="max-w-4xl mx-auto">
            <div class="glass-effect p-12 rounded-3xl shadow-2xl fade-in mb-12">
                <div class="text-center mb-12">
                    <i class="fas fa-search text-6xl text-purple-500 mb-6"></i>
                    <h1 class="text-5xl font-bold text-gray-800 mb-6">🔍 Smart Learning Search</h1>
                    <p class="text-2xl text-gray-600 mb-8">Find the best resources for any topic instantly</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
       
        col_input, col_search = st.columns([4,1])
        with col_input:
            topic = st.text_input(
                "",
                placeholder="Binary Trees, Machine Learning, Operating Systems...",
                label_visibility="collapsed"
            )
        
        if topic and st.button("🔍 Search Resources", use_container_width=True, type="primary"):
            with st.spinner("🔮 Finding best resources..."):
                res = get_resources(topic)
               
                st.markdown("""
                <div class="glass-effect p-10 rounded-3xl mb-12">
                    <h3 class="text-3xl font-bold text-gray-800 mb-8 flex items-center">
                        <i class="fas fa-globe text-indigo-500 mr-4 text-3xl"></i>Top Websites
                    </h3>
                </div>
                """, unsafe_allow_html=True)
               
                for w in res["websites"]:
                    st.markdown(f"""
                    <div class="glass-effect p-6 rounded-2xl mb-4 hover:shadow-xl transition-all">
                        <a href="{w}" target="_blank" class="text-xl font-semibold text-indigo-600 hover:text-indigo-700">{w}</a>
                    </div>
                    """, unsafe_allow_html=True)
               
                st.markdown("""
                <div class="glass-effect p-10 rounded-3xl">
                    <h3 class="text-3xl font-bold text-gray-800 mb-8 flex items-center">
                        <i class="fab fa-youtube text-red-500 mr-4 text-3xl"></i>YouTube Videos
                    </h3>
                </div>
                """, unsafe_allow_html=True)
               
                youtube_url = res["youtube"]
                if youtube_url:
                    if "youtube.com/watch?v=" in youtube_url:
                        video_id = youtube_url.split("v=")[1].split("&")[0]
                    elif "youtu.be/" in youtube_url:
                        video_id = youtube_url.split("youtu.be/")[1].split("?")[0]
                    else:
                        video_id = None
                   
                    if video_id:
                        st.markdown(f"""
                        <div class="glass-effect p-4 rounded-3xl mb-8">
                            <iframe width="100%" height="450" src="https://www.youtube.com/embed/{video_id}"
                            frameborder="0" allowfullscreen class="rounded-3xl"></iframe>
                            <div class="text-center mt-6">
                                <a href="{youtube_url}" target="_blank" class="btn-primary inline-block text-xl py-4 px-8 rounded-3xl text-white font-semibold">
                                    <i class="fab fa-youtube mr-3"></i>Watch on YouTube
                                </a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="glass-effect p-12 rounded-3xl text-center">
                            <a href="{youtube_url}" target="_blank" class="btn-primary inline-block text-2xl py-6 px-12 rounded-3xl text-white font-bold">
                                <i class="fab fa-youtube mr-4 text-2xl"></i>{youtube_url.split('/')[-1]}
                            </a>
                        </div>
                        """, unsafe_allow_html=True)


# ================= ROUTER =================
if st.session_state.user is None:
    role_selection()
elif st.session_state.role == "admin":
    admin_panel()
else:
    student_panel()