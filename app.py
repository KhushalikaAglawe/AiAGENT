import warnings

# WARNING SUPPRESSION: Yeh line sabhi modules se DeprecationWarning ko ignore kar degi.
warnings.filterwarnings("ignore", category=DeprecationWarning) 

import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3 
import streamlit as st
from agent_logic import run_prioritization_agent 

# --- 1. LOGIN CONSTANTS & PRIORITY ORDER ---
USER_CREDENTIALS = {
    "admin": "admin123",
    "analyst": "data456",
    "viewer": "view789",
}

PRIORITY_ORDER = {
    'P1: Critical Issue 🚨': 1,
    'P2: High Priority': 2,
    'P3: Top Positive 👍': 3,
    'P4: Review Later': 4
}

# --- FILE PATH CONSTANTS ---
DB_FILE_NAME = 'feedback_data.db' 
TABLE_NAME = 'feedback_table'     


# --- DATA DELETION FUNCTION (Clears SQLite Table) ---
def clear_database():
    """Deletes the entire feedback table from the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE_NAME)
        cursor = conn.cursor()
        
        cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
        conn.commit()
        
        st.success(f"✅ Database reset successful! Table '{TABLE_NAME}' deleted from {DB_FILE_NAME}.")
    except Exception as e:
        st.error(f"❌ An error occurred during database reset: {e}")
    finally:
        if conn:
            conn.close()


# --- 2. STREAMLIT CONFIGURATION & INITIALIZATION ---
st.set_page_config(
    layout="wide", 
    page_title="🌟 Feedback Prioritizer Dashboard", 
    initial_sidebar_state="expanded",
    menu_items={'About': "# Yeh app AI-powered feedback prioritization ke liye hai."}
)

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None

# --- Custom CSS for Mobile Responsiveness ---
st.markdown("""
<style>
/* 1. Common Styling */
.stApp > header {
    background-color: transparent;
}
[data-testid="stMetricValue"] {
    font-size: 32px;
    font-weight: bold;
    color: #007bff;
}
[data-testid="stMetricLabel"] {
    font-size: 14px;
    color: #6c757d;
}
h2 {
    border-bottom: 2px solid #e0e0e0;
    padding-bottom: 10px;
    margin-top: 20px;
}
.stForm {
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    background-color: #f8f9fa;
}

/* 2. MOBILE RESPONSIVENESS FIXES */
@media (max-width: 768px) {
    /* Metrics columns ko stack karna */
    .stApp [data-testid="stHorizontalBlock"] > div {
        flex-direction: column !important;
    }
    .stApp [data-testid="stHorizontalBlock"] > div > div {
        width: 100% !important;
        margin-bottom: 10px;
    }
    /* Chart columns ko stack karna */
    .stApp [data-testid="column"] {
        width: 100% !important;
        max-width: 100% !important;
        flex: 1 1 100% !important;
    }
    /* Title aur headers ki font size choti karna */
    h1 {
        font-size: 2em; 
    }
    h2 {
        font-size: 1.5em; 
    }
}
</style>
""", unsafe_allow_html=True)


# --- 3. LOGIN & LOGOUT FUNCTIONS ---

def handle_login(username, password):
    """Credentials check karta hai aur session state update karta hai."""
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        st.session_state['authenticated'] = True
        st.session_state['username'] = username
        st.toast(f"✅ Login successful! Welcome, {username}.", icon='🎉')
        st.rerun() 
    else:
        st.error("❌ Invalid Username or Password. Please try again.")

def logout():
    """User ko log out karta hai."""
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    st.toast("👋 You have been logged out.", icon='🚪')
    st.rerun()

def show_login_page():
    """Login form ko center mein display karta hai."""
    
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        st.image("https://images.unsplash.com/photo-1517430816045-df4b7de1101d?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", width=600, caption="AI-Powered Feedback Analysis")
        st.title("🔐 Feedback Prioritizer: Login Required")
        st.markdown("---")
        
        with st.form("login_form"):
            st.subheader("Enter Credentials (Access for 3 Authorized Users)")
            username = st.text_input("👤 Username", key="login_username")
            password = st.text_input("🔒 Password", type="password", key="login_password")
            submitted = st.form_submit_button("🚀 Login")

            if submitted:
                handle_login(username, password)
    
    # Allowed users ki jaankari sidebar mein
    with st.sidebar:
        st.header("🔑 Test Credentials")
        st.info(
            """
            **Admin:** admin / admin123  
            **Analyst:** analyst / data456  
            **Viewer:** viewer / view789
            """
        )

# --- 4. MAIN APPLICATION CONTENT (Design Enhanced) ---

def show_main_app(df_prioritized):
    """Main dashboard content with enhanced design."""
    
    # --- HEADER & LOGOUT ---
    st.sidebar.header(f"Welcome, {st.session_state['username']}! 👋")
    st.sidebar.button("🚪 Logout", on_click=logout, use_container_width=True) 
    st.sidebar.markdown("---")
    
    st.title("✨ AI Feedback Prioritization Dashboard")
    st.caption("🔍 Analyzing and ranking customer feedback in real-time.")

    # Admin Tab Logic
    is_admin = st.session_state['username'] == "admin"
    
    if is_admin:
        tab_dashboard, tab_admin = st.tabs(["📊 Dashboard View", "⚙️ Admin Tools (Data Reset)"])
    else:
        tab_dashboard = st.container() 
        tab_admin = None

    # Error handling for data load failure
    if df_prioritized.empty:
        st.error("❌ Error loading data or the database is empty. Please run 'python feedback_collector.py'.")
        return

    # --- DASHBOARD CONTENT ---
    with tab_dashboard:
        # --- SIDEBAR FILTERS ---
        st.sidebar.header("⚙️ Filter Options")
        
        # Priority Multiselect with Emojis
        priority_filter = st.sidebar.multiselect(
            "🚨 Priority Level",
            options=df_prioritized['Priority'].unique(),
            default=['P1: Critical Issue 🚨', 'P2: High Priority'] 
        )

        # Category Multiselect
        category_filter = st.sidebar.multiselect(
            "🏷️ Feedback Category",
            options=df_prioritized['Category'].unique(),
            default=df_prioritized['Category'].unique()
        )
        
        # Confidence Score Slider
        min_confidence = st.sidebar.slider(
            "🎯 Minimum Confidence Score",
            min_value=0.0,
            max_value=1.0,
            value=0.5, 
            step=0.05,
            format="%.2f"
        )
        st.sidebar.markdown("---")


        # --- APPLY FILTERS ---
        df_filtered = df_prioritized[
            (df_prioritized['Priority'].isin(priority_filter)) &
            (df_prioritized['Category'].isin(category_filter)) &
            (df_prioritized['Confidence_Score'] >= min_confidence)
        ]
        
       # --- ROW 1: METRICS (Using st.container for grouping) ---
        st.header("📊 Key Performance Indicators (KPIs)")
        
        metric_container = st.container(border=True)
        with metric_container:
            total_feedback = len(df_prioritized)
            
            p1_count = df_filtered[df_filtered['Priority'] == 'P1: Critical Issue 🚨'].shape[0]
            p2_count = df_filtered[df_filtered['Priority'] == 'P2: High Priority'].shape[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric(label="Total Feedback (Last 7 Days)", value=total_feedback)
            col2.metric(label=f"Filtered Items", value=len(df_filtered), delta=f"{len(df_filtered)} items visible", delta_color="off")
            col3.metric(label=f"🚨 Critical Issues (P1)", value=p1_count, delta="High Risk", delta_color="inverse")
            col4.metric(label=f"🔥 High Priority (P2)", value=p2_count, delta="Needs Review")

        st.markdown("---")

        # --- ROW 2: CHARTS ---
        st.header("📈 Data Visualization")
        
        # 1. Pie Chart
        priority_counts = df_filtered['Priority'].value_counts().reset_index()
        priority_counts.columns = ['Priority', 'Count']
        
        fig_priority = px.pie(
            priority_counts, 
            values='Count', 
            names='Priority', 
            title='**Priority Distribution (Filtered)**',
            color='Priority',
            color_discrete_map={
                'P1: Critical Issue 🚨': 'red', 'P2: High Priority': 'orange', 'P3: Top Positive 👍': 'green', 'P4: Review Later': 'blue'
            }
        )

        # 2. Bar Chart 
        category_priority_counts = df_filtered.groupby(['Category', 'Priority']).size().reset_index(name='Count')
        
        fig_category = px.bar(
            category_priority_counts, x='Category', y='Count', color='Priority', 
            title='**Category Breakdown by Priority (Filtered)**',
            color_discrete_map={
                'P1: Critical Issue 🚨': 'red', 'P2: High Priority': 'orange', 'P3: Top Positive 👍': 'green', 'P4: Review Later': 'blue'
            }
        )

        fig_category.update_layout(barmode='stack', xaxis_title="Feedback Category")
        
        # Plotly deprecation warning fix
        PLOTLY_CONFIG = {
            'displayModeBar': False, 
            'responsive': True       
        }

        # Use width='stretch' (Streamlit fix) aur config=PLOTLY_CONFIG (Plotly fix)
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.plotly_chart(fig_priority, width='stretch', config=PLOTLY_CONFIG)
        with chart_col2:
            st.plotly_chart(fig_category, width='stretch', config=PLOTLY_CONFIG)

        st.markdown("---")

        # --- ROW 3: FILTERED DATA TABLE & DOWNLOAD BUTTON ---
        st.header(f"📋 Prioritized Feedback Table ({len(df_filtered)} Items)")
        st.caption("This table reflects your current filter selections in the sidebar.")
        
        if not df_filtered.empty:
            
            # Priority Rank for correct sorting
            if 'Priority_Rank' not in df_filtered.columns:
                df_filtered['Priority_Rank'] = df_filtered['Priority'].map(PRIORITY_ORDER)
                
            df_display = df_filtered.sort_values(by='Priority_Rank', ascending=True)

            csv = df_display.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Download Filtered Data as CSV",
                data=csv,
                file_name='Prioritized_Feedback_Agent_Output.csv',
                mime='text/csv',
                help='Click to download the currently filtered table data.'
            )
            
            # Table display. Note: 'Original_Text' contains regional language entries.
            st.dataframe(
                df_display[['Date/Time', 'Priority', 'Category', 'Confidence_Score', 'Text', 'Original_Text', 'User_ID']], 
                width='stretch'
            )

        else:
            st.info("No data available based on current filters.")

    # --- ADMIN Tools Tab ---
    if tab_admin:
        with tab_admin:
            st.header("⚠️ Permanent Data Reset Tool")
            st.warning("🚨 **WARNING:** Clicking this button will PERMANENTLY delete the entire **Feedback Table** from the SQLite database. Use this for weekly resets.")
            
            if st.button("🗑️ Reset Feedback Data (Clear Database)", type="primary"):
                clear_database() 
                st.info("🔄 Please **RERUN** the app (Ctrl+R/Cmd+R) to load the empty dataset.")


# --- 5. MAIN APP FLOW ---
def main():
    """Authentication state ke aadhar par app flow ko control karta hai."""
    if not st.session_state['authenticated']:
        show_login_page()
    else:
        df_prioritized = run_prioritization_agent()
        show_main_app(df_prioritized)

if __name__ == '__main__':
    main()