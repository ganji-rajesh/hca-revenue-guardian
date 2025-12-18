"""
Revenue Guardian - Streamlit Application
Main UI interface for the Bill-Only Reconciliation Engine.
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Import custom modules
from reconciliation_engine import ReconciliationEngine
from utils import format_currency
from config import (
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
    DEFAULT_MATCH_THRESHOLD,
    SAMPLE_INVOICE_PATH,
    SAMPLE_CLINICAL_PATH,
    RISK_LEVELS,
    EXPORT_DATETIME_FORMAT
)

# --- Page Configuration ---
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00529B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #00529B;
    }
</style>
""", unsafe_allow_html=True)

# --- Title Section ---
st.markdown(f'<div class="main-header">{PAGE_ICON} {APP_NAME}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">{APP_DESCRIPTION}</div>', unsafe_allow_html=True)

# --- Project Context Banner ---
with st.expander("📋 Project Context & Objective", expanded=False):
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        ### Objective
        Automate the detection of **revenue leakage** by reconciling Vendor Invoices 
        against Clinical Documentation using advanced fuzzy logic matching.

        ### The Problem
        In high-volume surgical environments, "Bill-Only" implants are provided by vendors:
        - ✅ **Supply Chain PAYS** the vendor for the implant
        - ❌ **Clinical staff FAILS** to document it in the patient's EHR
        - 💸 **Result:** Hospital cannot bill insurance → Revenue Lost

        ### The Solution
        This tool uses **Fuzzy String Matching** with configurable thresholds to identify:
        - Discrepancies between AP (Accounts Payable) and Clinical Documentation
        - High-risk items requiring immediate attention
        - Financial impact of uncaptured charges
        """)

    with col2:
        st.markdown("### Key Features")
        st.markdown("""
        - 🔍 **Fuzzy Matching**: Handles spelling variations
        - 📊 **Risk Classification**: High/Medium/Low
        - 💰 **Financial Impact**: Real-time calculation
        - 📥 **Audit Reports**: Exportable CSV
        - ⚙️ **Configurable**: Adjustable thresholds
        """)

# --- Sidebar Configuration ---
st.sidebar.header("⚙️ Configuration")
st.sidebar.markdown("---")

# Matching Threshold Slider
match_threshold = st.sidebar.slider(
    "Match Confidence Threshold (%)",
    min_value=60,
    max_value=95,
    value=DEFAULT_MATCH_THRESHOLD,
    step=5,
    help="Items below this score will be flagged as potential revenue leakage"
)

st.sidebar.markdown("---")
st.sidebar.info(f"""
**Matching Threshold: {match_threshold}%**

- **90-100%**: High Confidence Match ✅
- **{match_threshold}-89%**: Review Required ⚠️
- **< {match_threshold}%**: High Risk Leakage ❌
""")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Version:** {APP_VERSION}")

# --- Data Loading Section ---
st.header("1️⃣ Data Source")

# Check if sample data files exist
sample_data_exists = os.path.exists(SAMPLE_INVOICE_PATH) and os.path.exists(SAMPLE_CLINICAL_PATH)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📂 Load Sample Data")
    if sample_data_exists:
        if st.button("🚀 Load Demo Dataset", type="primary", use_container_width=True):
            try:
                st.session_state.df_inv = pd.read_csv(SAMPLE_INVOICE_PATH)
                st.session_state.df_clin = pd.read_csv(SAMPLE_CLINICAL_PATH)
                st.session_state.data_loaded = True
                st.success("✅ Sample data loaded successfully!")
            except Exception as e:
                st.error(f"Error loading sample data: {str(e)}")
    else:
        st.warning("⚠️ Sample CSV files not found in repository.")

with col2:
    st.subheader("⬆️ Upload Custom Data")
    uploaded_inv = st.file_uploader("Upload Vendor Invoice CSV", type=['csv'], key="invoice")
    uploaded_clin = st.file_uploader("Upload Clinical Logs CSV", type=['csv'], key="clinical")

    if uploaded_inv and uploaded_clin:
        try:
            st.session_state.df_inv = pd.read_csv(uploaded_inv)
            st.session_state.df_clin = pd.read_csv(uploaded_clin)
            st.session_state.data_loaded = True
            st.success("✅ Custom data uploaded successfully!")
        except Exception as e:
            st.error(f"Error uploading files: {str(e)}")

# --- Analysis Section ---
if 'data_loaded' in st.session_state and st.session_state.data_loaded:

    df_inv = st.session_state.df_inv
    df_clin = st.session_state.df_clin

    st.markdown("---")
    st.header("2️⃣ Reconciliation Analysis")

    # --- KPI Metrics ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_invoiced = len(df_inv)
        st.metric("📄 Invoices Processed", total_invoiced)

    with col2:
        total_spend = df_inv['Unit_Cost'].sum()
        st.metric("💰 Total Spend", format_currency(total_spend))

    with col3:
        total_logged = len(df_clin)
        st.metric("📋 Clinical Logs", total_logged)

    with col4:
        potential_issues = total_invoiced - total_logged
        st.metric("⚠️ Potential Gaps", potential_issues)

    st.markdown("---")

    # --- Run Reconciliation Engine ---
    with st.spinner("🔍 Running Reconciliation Engine..."):
        try:
            # Initialize engine with user-selected threshold
            engine = ReconciliationEngine(match_threshold=match_threshold)

            # Perform reconciliation
            df_results = engine.reconcile(df_inv, df_clin)

            # Generate summary statistics
            summary_stats = engine.generate_summary_stats(df_results)

            st.success("✅ Reconciliation complete!")

        except Exception as e:
            st.error(f"Error during reconciliation: {str(e)}")
            st.stop()

    # --- Results Visualization ---
    st.subheader("📊 Detailed Reconciliation Report")

    # Filter Options
    filter_option = st.radio(
        "Filter Results:",
        ["All Items", "High Risk Only", "Review Required", "Matched Items"],
        horizontal=True
    )

    # Apply Filter
    if filter_option == "High Risk Only":
        display_df = df_results[df_results['Risk_Level'] == RISK_LEVELS["HIGH"]]
    elif filter_option == "Review Required":
        display_df = df_results[df_results['Risk_Level'] == RISK_LEVELS["MEDIUM"]]
    elif filter_option == "Matched Items":
        display_df = df_results[df_results['Risk_Level'] == RISK_LEVELS["LOW"]]
    else:
        display_df = df_results

    # Display count
    st.caption(f"Showing {len(display_df)} of {len(df_results)} items")

    # Display Dataframe
    st.dataframe(
        display_df[['PO_Number', 'Vendor_Item', 'Clinical_Match', 'Confidence_Score', 'Unit_Cost', 'Status']],
        use_container_width=True,
        height=400
    )

    # --- Financial Impact Summary ---
    st.markdown("---")
    st.header("3️⃣ Financial Impact Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        high_stats = summary_stats[RISK_LEVELS["HIGH"]]

        st.error("### ❌ Critical Revenue Leakage")
        st.metric("Uncaptured Revenue", format_currency(high_stats['total_amount']))
        st.metric("Undocumented Items", high_stats['count'])
        if high_stats['count'] > 0:
            st.caption(f"Avg: {format_currency(high_stats['avg_amount'])}")

    with col2:
        medium_stats = summary_stats[RISK_LEVELS["MEDIUM"]]

        st.warning("### ⚠️ Items Requiring Review")
        st.metric("Amount Under Review", format_currency(medium_stats['total_amount']))
        st.metric("Items Flagged", medium_stats['count'])
        if medium_stats['count'] > 0:
            st.caption(f"Avg: {format_currency(medium_stats['avg_amount'])}")

    with col3:
        low_stats = summary_stats[RISK_LEVELS["LOW"]]

        st.success("### ✅ Successfully Matched")
        st.metric("Verified Revenue", format_currency(low_stats['total_amount']))
        st.metric("Matched Items", low_stats['count'])
        if low_stats['count'] > 0:
            st.caption(f"Avg: {format_currency(low_stats['avg_amount'])}")

    # --- Download Section ---
    st.markdown("---")
    st.header("4️⃣ Export Audit Report")

    col1, col2, col3 = st.columns(3)

    with col1:
        csv_data = df_results.to_csv(index=False).encode('utf-8')
        timestamp = datetime.now().strftime(EXPORT_DATETIME_FORMAT)
        st.download_button(
            label="📥 Download Full Report (CSV)",
            data=csv_data,
            file_name=f'revenue_leakage_audit_{timestamp}.csv',
            mime='text/csv',
            type="primary",
            use_container_width=True
        )

    with col2:
        high_risk_df = df_results[df_results['Risk_Level'] == RISK_LEVELS["HIGH"]]
        high_risk_csv = high_risk_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⚠️ Download High-Risk Only",
            data=high_risk_csv,
            file_name=f'high_risk_items_{timestamp}.csv',
            mime='text/csv',
            use_container_width=True
        )

    with col3:
        # Export summary statistics
        summary_df = pd.DataFrame(summary_stats).T
        summary_csv = summary_df.to_csv().encode('utf-8')
        st.download_button(
            label="📊 Download Summary Stats",
            data=summary_csv,
            file_name=f'summary_statistics_{timestamp}.csv',
            mime='text/csv',
            use_container_width=True
        )

else:
    st.info("👆 Please load sample data or upload custom CSV files to begin analysis.")

    # Show sample data format
    with st.expander("📝 Required Data Format"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Vendor Invoice CSV:**")
            st.code("""
Invoice_ID, PO_Number, Vendor_Item_Name, Quantity, Unit_Cost, Invoice_Date
INV-001, PO-1001, Stryker Knee System, 1, 4500.00, 2025-10-15
            """)

        with col2:
            st.markdown("**Clinical Logs CSV:**")
            st.code("""
Case_ID, Clinical_Item_Desc, Qty_Used, Implant_Date, PO_Ref_Optional
CASE-501, stryker knee total, 1, 2025-10-15, PO-1001
            """)

# --- Footer ---
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #888; font-size: 0.9rem;'>
    <b>{APP_NAME} v{APP_VERSION}</b> | Built for HCA Healthcare Supply Chain Informatics Specialist Role<br>
    Developed following Data Science Best Practices
</div>
""", unsafe_allow_html=True)
