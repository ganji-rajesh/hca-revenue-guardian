"""
Configuration file for Revenue Guardian application.
Centralizes all constants and configuration parameters.
"""

# Application Metadata
APP_NAME = "Revenue Guardian"
APP_VERSION = "1.1.0"
APP_DESCRIPTION = "Automated Bill-Only Surgical Reconciliation Engine"

# Matching Algorithm Parameters
DEFAULT_MATCH_THRESHOLD = 70
HIGH_CONFIDENCE_THRESHOLD = 90
REVIEW_THRESHOLD = 60

# Risk Classification
RISK_LEVELS = {
    "HIGH": "High",
    "MEDIUM": "Medium",
    "LOW": "Low"
}

# File Paths
SAMPLE_INVOICE_PATH = "vendor_invoice_data.csv"
SAMPLE_CLINICAL_PATH = "clinical_logs_data.csv"

# Column Mappings
INVOICE_COLUMNS = {
    "po_number": "PO_Number",
    "vendor_item": "Vendor_Item_Name",
    "unit_cost": "Unit_Cost",
    "invoice_date": "Invoice_Date",
    "quantity": "Quantity"
}

CLINICAL_COLUMNS = {
    "case_id": "Case_ID",
    "clinical_item": "Clinical_Item_Desc",
    "qty_used": "Qty_Used",
    "implant_date": "Implant_Date"
}

# Output Settings
EXPORT_DATETIME_FORMAT = "%Y%m%d_%H%M%S"

# UI Settings
PAGE_TITLE = "HCA Revenue Guardian"
PAGE_ICON = "🏥"
LAYOUT = "wide"
