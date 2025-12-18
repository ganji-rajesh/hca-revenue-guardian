# 🏥 Healthcare Supply Chain Informatics Portfolio

**Targeted Technical Solutions for HCA Healthcare**

This repository contains three high-impact proof-of-concept projects designed specifically to address the major responsibilities of a Supply Chain Informatics Specialist: **Financial Integrity, Operational Efficiency, and Patient Safety.**

---

## 📂 Project Index

| Project Name | Focus Area | Tech Stack | Estimated Build Time |
| :--- | :--- | :--- | :--- |
| **1. Surgical Implant Reconciliation Bot** | 💰 Revenue Integrity | Python, Pandas, Fuzzy Matching | 3-5 Hours |
| **2. "Save-the-Supply" Optimization Tool** | 📉 Waste Reduction | Time-Series Analysis, Streamlit | 2-4 Hours |
| **3. OpenFDA Recall Cross-Reference** | 🚨 Compliance/Safety | REST APIs, JSON, SQL | 2-3 Hours |

---

## 1. The "Bill-Only" Reconciliation Engine
### *Project: Surgical Implant Reconciliation Bot*

**Context:** In high-volume surgery, vendors often provide "Bill-Only" implants (e.g., screws, knees). A common source of revenue leakage occurs when the hospital pays the vendor invoice but fails to document the item in the EHR for insurance reimbursement.

**Objective:** Automate the identification of "uncaptured charges" by reconciling inconsistent datasets using fuzzy logic.

#### 🏗️ Architecture
1.  **Input Layer:**
    *   `Vendor_Invoice.csv` (PO#, Item Description, Cost, Date)
    *   `EHR_Logs.csv` (PatientID, Item Used, Date)
2.  **Processing Layer (Python):**
    *   **Normalization:** Lowercase conversion and special character removal.
    *   **Fuzzy Matcher:** Uses Levenshtein distance to match messy vendor strings (e.g., "Stryker Screw 4mm") to clinical names (e.g., "Screw, 4mm, Titanium").
    *   **Logic Gate:** Matches within a +/- 2-day window with a Match Score > 80%.
3.  **Output Layer:**
    *   Generates an audit report highlighting specific POs with no corresponding clinical documentation.

#### 🛠️ Skills Showcased
*   **Fuzzy Logic / String Matching:** (`thefuzz` library) Handling inconsistent naming conventions.
*   **Data Cleaning:** (`pandas`) Merging and cleaning datasets.
*   **Revenue Analysis:** Calculating the dollar impact of leakage.

---

## 2. Predictive Expiration "Redistribution" Dashboard
### *Project: "Save-the-Supply" Optimization Tool*

**Context:** The Job Description emphasizes optimizing PAR levels and transferring items. Hospitals often discard expiring items while a nearby facility is ordering the same product. This solves the logistics of waste reduction.

**Objective:** Identify inventory expiring in the next 90 days and calculate a "Burn Rate" to determine if it should be transferred to another facility.

#### 🏗️ Architecture
1.  **Data Model:**
    *   `Inventory_Snapshot` (Item, Qty, ExpiryDate, Location)
    *   `Usage_History` (Item, Qty Used, Date)
2.  **Analytics Engine:**
    *   **Metric Calculation:** Calculates Average Daily Usage (ADU).
    *   **Logic Script:** `IF (Stock_On_Hand / ADU) > Days_To_Expiration THEN Flag_For_Transfer`.
    *   **Classification:** 🟢 **Safe** (Will use in time) vs 🔴 **Risk** (Will expire).
3.  **Presentation:**
    *   A heatmap or table sorted by "Cost at Risk" ($), suggesting transfer quantities.

#### 🛠️ Skills Showcased
*   **Time-Series Analysis:** Forecasting consumption based on historical data.
*   **Logic Scripting:** Conditional algorithms for inventory management.
*   **Data Visualization:** (`Matplotlib` or `Streamlit`) Visualizing financial risk.

---

## 3. Automated FDA Recall Monitor
### *Project: OpenFDA Recall Cross-Reference Tool*

**Context:** Recall management is critical for patient safety and compliance. Relying on manual emails for FDA alerts is slow and risky. This tool automates the monitoring process via API.

**Objective:** Connect to the OpenFDA API to fetch real-time device recalls and instantly query internal inventory to alert staff of affected items on the shelf.

#### 🏗️ Architecture
1.  **External Source:**
    *   `GET` request to [OpenFDA API](https://open.fda.gov/apis/device/recall/) (filtered by last 7 days).
2.  **Internal Simulation:**
    *   Mock SQLite database representing `Current_Hospital_Inventory`.
3.  **Matching Logic:**
    *   Parses JSON to extract `k_number` (510k) or `lot_number`.
    *   Query: `SELECT * FROM Inventory WHERE Lot_Num IN (API_List)`.
4.  **Alerting:**
    *   Triggers a formatted "CRITICAL ALERT" displaying the specific bin location of the recalled item.

#### 🛠️ Skills Showcased
*   **API Integration:** (`requests`) Handling external data feeds.
*   **JSON Parsing:** Navigating nested dictionary structures.
*   **SQL/Database:** Querying internal inventory systems.
*   **Process Automation:** Reducing manual monitoring time.

---

## 🚀 Getting Started

To run these proofs-of-concept locally:

1.  Clone this repository.
2.  Install dependencies:
    ```
    pip install pandas thefuzz faker streamlit matplotlib requests
    ```
3.  Navigate to the specific project folder and run the script (e.g., `python revenue_guardian.py`).

---

*This portfolio was created to demonstrate technical competency for the HCA Supply Chain Informatics Specialist role.*
