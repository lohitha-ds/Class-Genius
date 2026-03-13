"""
UI Components for Attendance Integration in Streamlit
Provides admin functions to send notes to absentees
"""

import streamlit as st
import os
from datetime import datetime, timedelta
from attendance_integration import AttendanceManager
from absentee_notification import AbsenteeNotificationService
from database import conn, c



def render_attendance_integration_section():
    """Render the attendance integration section in admin panel"""
    
    st.markdown("""
    <div class="glass-effect p-8 rounded-3xl mb-8" style="border-left: 5px solid #000000;">
        <h2 class="text-3xl font-bold text-black mb-2">📋 Attendance Integration</h2>
        <p class="text-gray-600">Send class notes automatically to absentees based on face recognition</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Send Notes", "Attendance Report", "Notification History"])
    
    with tab1:
        render_send_notes_tab()
    
    with tab2:
        render_attendance_report_tab()
    
    with tab3:
        render_notification_history_tab()


def render_send_notes_tab():
    """Tab for sending notes to absentees"""
    
    st.subheader("📧 Send Notes to Absentees")
    
    # Date selection
    col1, col2 = st.columns(2)
    
    with col1:
        attendance_date = st.date_input(
            "Select attendance date",
            value=datetime.now().date(),
            help="Notes will be sent to students absent on this date"
        )
    
    with col2:
        note_file = st.selectbox(
            "Select PDF note to send",
            options=get_available_notes(),
            help="Choose which class notes to send to absentees"
        )
    
    # Reason for sending
    reason = st.text_area(
        "Reason for sending (optional)",
        placeholder="e.g., Missed class due to...",
        max_chars=500
    )
    
    # Get absentees preview
    if attendance_date:
        attendance_manager = AttendanceManager()
        date_str = attendance_date.strftime('%d-%m-%Y')
        absentees = attendance_manager.get_absentees_for_date(date_str)
        
        if absentees:
            st.info(f"📊 Found {len(absentees)} absentees for {date_str}")
            
            # Show absentee list
            with st.expander("👥 View Absentee List"):
                absentee_list = []
                for student_id, details in absentees.items():
                    absentee_list.append({
                        'ID': student_id,
                        'Name': details.get('name', 'N/A'),
                        'Email': details.get('email', 'N/A')
                    })
                
                st.dataframe(absentee_list, use_container_width=True)
        else:
            st.warning(f"✅ No absentees found for {date_str}")
    
    # Send button
    if st.button("📤 Send Notes to Absentees", type="primary", use_container_width=True):
        if not note_file:
            st.error("Please select a PDF file to send")
        elif not absentees:
            st.warning("No absentees to send notes to")
        else:
            with st.spinner("Sending emails..."):
                notification_service = AbsenteeNotificationService()
                result = notification_service.send_notes_to_absentees_for_date(
                    note_pdf_path=note_file,
                    attendance_date=date_str,
                    reason=reason
                )
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                    st.metric("Emails Sent", result['sent_count'])
                    if result['failed_count'] > 0:
                        st.warning(f"⚠️ {result['failed_count']} emails failed to send")
                else:
                    st.error(f"❌ {result['message']}")


def render_attendance_report_tab():
    """Tab for viewing attendance reports"""
    
    st.subheader("📊 Attendance Report")
    
    attendance_manager = AttendanceManager()
    
    # Date range selection
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start date",
            value=datetime.now().date() - timedelta(days=30)
        )
    
    with col2:
        end_date = st.date_input(
            "End date",
            value=datetime.now().date()
        )
    
    # Get all students
    all_students = attendance_manager.get_all_students()
    
    if all_students:
        st.info(f"📈 Total registered students: {len(all_students)}")
        
        # Show attendance statistics
        col1, col2, col3 = st.columns(3)
        
        # Today's absentees
        today_absentees = attendance_manager.get_absentees()
        with col1:
            st.metric("Today's Absentees", len(today_absentees))
        
        # Today's attendance rate
        today_present = len(all_students) - len(today_absentees)
        attendance_rate = (today_present / len(all_students) * 100) if all_students else 0
        with col2:
            st.metric("Today's Attendance Rate", f"{attendance_rate:.1f}%")
        
        with col3:
            st.metric("Today's Present", today_present)
        
        st.divider()
        
        # Student attendance details
        st.subheader("👥 Student Attendance Details")
        
        student_data = []
        for student_id, details in all_students.items():
            attendance_pct = attendance_manager.get_attendance_percentage(student_id)
            today_present = student_id not in today_absentees
            
            student_data.append({
                'ID': student_id,
                'Name': details.get('name', 'N/A'),
                'Email': details.get('email', 'N/A'),
                'Attendance %': f"{attendance_pct:.1f}%",
                'Present Today': '✅' if today_present else '❌'
            })
        
        st.dataframe(student_data, use_container_width=True)
    else:
        st.warning("No student data available. Ensure StudentDetails.csv is populated.")


def render_notification_history_tab():
    """Tab for viewing notification history"""
    
    st.subheader("📜 Notification History")
    
    from database import c
    from absentee_notification import AbsenteeNotificationService
    
    notification_service = AbsenteeNotificationService()
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        filter_type = st.selectbox(
            "Filter by",
            ["All", "Student", "Status"],
            help="Choose how to filter notification history"
        )
    
    # Get history
    try:
        if filter_type == "All":
            history = notification_service.get_notification_history()
        elif filter_type == "Student":
            student_id = st.text_input("Enter Student ID")
            history = notification_service.get_notification_history(student_id=student_id) if student_id else []
        else:
            status = st.selectbox("Select Status", ["sent", "failed"])
            history = notification_service.get_notification_history()
            history = [h for h in history if h[5] == status] if history else []
        
        if history:
            # Convert to dataframe for display
            history_data = []
            for record in history:
                history_data.append({
                    'ID': record[0],
                    'Note ID': record[1],
                    'Student ID': record[2],
                    'Attendance Date': record[3],
                    'Sent Date': record[4],
                    'Status': '✅ Sent' if record[5] == 'sent' else '❌ Failed'
                })
            
            st.dataframe(history_data, use_container_width=True)
            
            # Statistics
            col1, col2, col3 = st.columns(3)
            
            total = len(history)
            sent = len([h for h in history if h[5] == 'sent'])
            failed = len([h for h in history if h[5] == 'failed'])
            
            with col1:
                st.metric("Total Notifications", total)
            with col2:
                st.metric("Successfully Sent", sent)
            with col3:
                st.metric("Failed", failed)
        else:
            st.info("No notification history found")
    
    except Exception as e:
        st.error(f"Error loading notification history: {e}")


def get_available_notes():
    """Get list of available PDF notes"""
    notes_dir = "notes"
    available_notes = []
    
    if os.path.exists(notes_dir):
        for file in os.listdir(notes_dir):
            if file.endswith('.pdf'):
                available_notes.append(os.path.join(notes_dir, file))
    
    return available_notes


def sync_attendance_data():
    """Sync attendance data from face recognition system"""
    
    st.subheader("🔄 Sync Attendance Data")
    
    if st.button("Sync Student Cache", use_container_width=True):
        with st.spinner("Syncing student data..."):
            notification_service = AbsenteeNotificationService()
            result = notification_service.update_student_cache()
            
            if result['success']:
                st.success(result['message'])
            else:
                st.error(result['message'])
    
    st.info("""
    This syncs student details from the face recognition system's StudentDetails.csv file
    to ensure the database has the latest information.
    """)
