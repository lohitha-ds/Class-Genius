"""
Face Recognition UI Components for Streamlit
Adds face recognition features to the ClassGenius app
"""

import streamlit as st
import os
from datetime import datetime
from face_recognition_bridge import FaceRecognitionBridge


def render_face_recognition_section():
    """Render complete face recognition section"""
    
    st.markdown("""
    <div class="glass-effect p-8 rounded-3xl mb-8" style="border-left: 5px solid #FF6B6B;">
        <h2 class="text-3xl font-bold text-black mb-2">😊 Face Recognition System</h2>
        <p class="text-gray-600">Register students, train model, and take attendance</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Register Student", "Capture Photos", "Train Model", "Take Attendance"])
    
    with tab1:
        render_register_student_tab()
    
    with tab2:
        render_capture_photos_tab()
    
    with tab3:
        render_train_model_tab()
    
    with tab4:
        render_take_attendance_tab()


def render_register_student_tab():
    """Register a new student and capture photos"""
    
    st.subheader("👤 Register New Student & Capture Photos")
    
    # Use container for better state management
    with st.form("student_registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            student_id = st.text_input(
                "Student ID",
                placeholder="STU001 or 23b01a0573",
                help="Unique identifier for the student"
            )
        
        with col2:
            student_name = st.text_input(
                "Student Name",
                placeholder="John Doe",
                help="Full name of the student"
            )
        
        student_email = st.text_input(
            "Email Address",
            placeholder="student@example.com",
            help="Email for notifications"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_samples = st.slider(
                "Number of Photo Samples",
                min_value=10,
                max_value=100,
                value=30,
                step=5,
                help="More samples = better accuracy (10-100)"
            )
        
        with col2:
            sample_interval = st.slider(
                "Sample Interval",
                min_value=50,
                max_value=300,
                value=100,
                step=10,
                help="Lower value = more frequent captures (50-300)"
            )
        
        submitted = st.form_submit_button("✅ Register & Capture Photos", use_container_width=True)
        
        if submitted:
            # Trim and validate inputs
            student_id = student_id.strip() if student_id else ""
            student_name = student_name.strip() if student_name else ""
            student_email = student_email.strip() if student_email else ""
            
            # Debug: Show what was received
            st.write(f"Debug - ID: '{student_id}' | Name: '{student_name}' | Email: '{student_email}'")
            
            if not student_id:
                st.error("❌ Please enter Student ID")
            elif not student_name:
                st.error("❌ Please enter Student Name")
            elif not student_email:
                st.error("❌ Please enter Email Address")
            elif "@" not in student_email:
                st.error("❌ Please enter a valid email address")
            else:
                # Register student first
                with st.spinner("🔄 Registering student..."):
                    bridge = FaceRecognitionBridge()
                    result = bridge.add_student(student_id, student_name, student_email)
                    
                    if result['success']:
                        st.success(f"✅ Student registered! Serial: {result['serial']}")
                        st.info(f"📷 Now capturing {num_samples} photos for {student_name}...")
                        
                        # Capture photos immediately
                        with st.spinner(f"📷 Opening camera... Look at the webcam and keep your face centered. Capturing {num_samples} photos..."):
                            capture_result = bridge.capture_student_photos(
                                student_id,
                                num_samples=num_samples,
                                sample_interval=sample_interval
                            )
                            
                            if capture_result['success']:
                                st.success(capture_result['message'])
                                st.balloons()
                                st.metric("Photos Captured", capture_result['samples_captured'])
                            else:
                                st.error(capture_result['message'])
                    else:
                        st.error(f"❌ {result['message']}")
    
    # Show existing students
    st.divider()
    st.subheader("📋 Registered Students")
    
    bridge = FaceRecognitionBridge()
    students = bridge.get_existing_students()
    
    if students:
        student_df = []
        for s in students:
            student_df.append({
                'Serial': s['serial'],
                'ID': s['id'],
                'Name': s['name'],
                'Email': s['email']
            })
        st.dataframe(student_df, use_container_width=True)
        st.info(f"📊 Total students registered: {len(students)}")
    else:
        st.warning("No students registered yet. Fill the form above to register!")


def render_capture_photos_tab():
    """Capture training photos for a student"""
    
    st.subheader("📷 Capture Training Photos")
    
    st.info("""
    Capture multiple photos of the student's face for training.
    Make sure the lighting is good and the student's face is clearly visible.
    """)
    
    bridge = FaceRecognitionBridge()
    students = bridge.get_existing_students()
    
    if not students:
        st.warning("No students registered. Please register a student first.")
        return
    
    # Create student ID mapping
    student_options = {f"{s['name']} ({s['id']})": s['id'] for s in students}
    
    selected = st.selectbox(
        "Select Student",
        options=list(student_options.keys()),
        help="Choose student to capture photos for"
    )
    
    selected_student_id = student_options[selected]
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_samples = st.slider(
            "Number of Samples",
            min_value=10,
            max_value=100,
            value=30,
            step=5,
            help="More samples = better accuracy"
        )
    
    with col2:
        sample_interval = st.slider(
            "Sample Interval",
            min_value=50,
            max_value=300,
            value=100,
            step=10,
            help="Lower value = more frequent captures"
        )
    
    if st.button("📷 Start Capturing Photos", type="primary", use_container_width=True):
        with st.spinner(f"Capturing {num_samples} photos... Click 'q' in the camera window to stop"):
            result = bridge.capture_student_photos(
                selected_student_id,
                num_samples=num_samples,
                sample_interval=sample_interval
            )
            
            if result['success']:
                st.success(result['message'])
                st.metric("Samples Captured", result['samples_captured'])
            else:
                st.error(result['message'])


def render_train_model_tab():
    """Train the face recognition model"""
    
    st.subheader("🤖 Train Face Recognition Model")
    
    st.info("""
    Train the model using captured photos.
    This creates a machine learning model that can recognize student faces.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Training Steps:")
        st.markdown("""
        1. Register all students
        2. Capture photos for each student (10-100 samples)
        3. Click 'Train Model' button
        4. Wait for training to complete
        5. Use 'Take Attendance' to verify
        """)
    
    with col2:
        st.markdown("### Requirements:")
        st.markdown("""
        - ✅ At least 2 students registered
        - ✅ Each student must have photos
        - ✅ Clear face images
        - ✅ Good lighting
        - ⏱️ Training takes 30-60 seconds
        """)
    
    if st.button("🤖 Train Model", type="primary", use_container_width=True):
        with st.spinner("Training model... This may take a minute"):
            bridge = FaceRecognitionBridge()
            result = bridge.train_model()
            
            if result['success']:
                st.success(result['message'])
                st.balloons()
            else:
                st.error(result['message'])


def render_take_attendance_tab():
    """Take attendance using face recognition"""
    
    st.subheader("✅ Take Attendance")
    
    st.info("""
    Use the webcam to recognize students and mark attendance.
    Make sure the model is trained first.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        confidence = st.slider(
            "Confidence Threshold",
            min_value=50,
            max_value=200,
            value=150,
            step=10,
            help="Lower = stricter. Higher = more lenient"
        )
    
    with col2:
        st.metric("Today's Date", datetime.now().strftime('%d-%m-%Y'))
    
    if st.button("📹 Start Taking Attendance", type="primary", use_container_width=True):
        with st.spinner("Starting attendance... Click 'q' in the camera window to stop"):
            bridge = FaceRecognitionBridge()
            result = bridge.take_attendance(confidence_threshold=confidence)
            
            if result['success']:
                st.success(result['message'])
                
                if result['students']:
                    st.subheader("📊 Attendance Record")
                    attendance_df = []
                    for student in result['students']:
                        attendance_df.append({
                            'Student ID': student['id'],
                            'Name': student['name'],
                            'Time': student['time']
                        })
                    
                    st.dataframe(attendance_df, use_container_width=True)
                    
                    st.success(f"Attendance saved to: {result['attendance_file']}")
            else:
                st.error(result['message'])
    
    # Show today's attendance summary
    st.divider()
    st.subheader("📈 Today's Attendance Summary")
    
    bridge = FaceRecognitionBridge()
    attendance = bridge.get_today_attendance_list()
    
    if attendance['success']:
        if attendance['present']:
            st.metric("Students Present Today", attendance['count'])
            
            with st.expander("View Details"):
                st.write("**Students marked present:**")
                for student_id in attendance['present']:
                    st.write(f"• {student_id}")
        else:
            st.info("No attendance recorded yet today")
    else:
        st.error(attendance['message'])
