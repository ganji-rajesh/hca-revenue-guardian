"""
Core reconciliation engine for fuzzy matching and risk classification.
This module contains the business logic for identifying revenue leakage.
"""

import pandas as pd
from thefuzz import process, fuzz
from typing import List, Dict, Tuple
import logging
from utils import normalize_text, validate_dataframe
from config import (
    HIGH_CONFIDENCE_THRESHOLD,
    RISK_LEVELS,
    INVOICE_COLUMNS,
    CLINICAL_COLUMNS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReconciliationEngine:
    """
    Main engine for performing fuzzy matching between vendor invoices
    and clinical documentation to identify revenue leakage.
    """

    def __init__(self, match_threshold: int = 70):
        """
        Initialize the reconciliation engine.

        Args:
            match_threshold (int): Minimum confidence score for a match (0-100)
        """
        self.match_threshold = match_threshold
        logger.info(f"ReconciliationEngine initialized with threshold: {match_threshold}")


    def classify_risk(self, match_score: int) -> Tuple[str, str]:
        """
        Classify the risk level based on match confidence score.

        Args:
            match_score (int): Confidence score (0-100)

        Returns:
            Tuple[str, str]: (status_message, risk_level)
        """
        if match_score >= HIGH_CONFIDENCE_THRESHOLD:
            return "✅ Match Found", RISK_LEVELS["LOW"]
        elif match_score >= self.match_threshold:
            return "⚠️ Review Required", RISK_LEVELS["MEDIUM"]
        else:
            return "❌ REVENUE LEAKAGE", RISK_LEVELS["HIGH"]


    def fuzzy_match_item(
        self, 
        vendor_item: str, 
        clinical_items: List[str],
        scorer=fuzz.token_sort_ratio
    ) -> Tuple[str, int]:
        """
        Find the best fuzzy match for a vendor item in clinical logs.

        Args:
            vendor_item (str): Item description from vendor invoice
            clinical_items (List[str]): List of clinical item descriptions
            scorer: Fuzzy matching scoring algorithm

        Returns:
            Tuple[str, int]: (best_match_string, confidence_score)
        """
        # Normalize the vendor item
        normalized_vendor = normalize_text(vendor_item)

        # Normalize all clinical items
        normalized_clinical = [normalize_text(item) for item in clinical_items]

        # Perform fuzzy matching
        best_match = process.extractOne(
            normalized_vendor,
            normalized_clinical,
            scorer=scorer
        )

        if best_match:
            # Return original clinical item and score
            match_index = normalized_clinical.index(best_match[0])
            return clinical_items[match_index], best_match[1]
        else:
            return "No Match Found", 0


    def reconcile(
        self, 
        df_invoice: pd.DataFrame, 
        df_clinical: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Perform full reconciliation between invoice and clinical data.

        Args:
            df_invoice (pd.DataFrame): Vendor invoice data
            df_clinical (pd.DataFrame): Clinical documentation data

        Returns:
            pd.DataFrame: Reconciliation results with match scores and risk levels
        """
        # Validate input data
        invoice_valid, invoice_error = validate_dataframe(
            df_invoice, 
            [INVOICE_COLUMNS["po_number"], 
             INVOICE_COLUMNS["vendor_item"], 
             INVOICE_COLUMNS["unit_cost"]]
        )

        if not invoice_valid:
            logger.error(f"Invoice data validation failed: {invoice_error}")
            raise ValueError(f"Invalid invoice data: {invoice_error}")

        clinical_valid, clinical_error = validate_dataframe(
            df_clinical,
            [CLINICAL_COLUMNS["clinical_item"]]
        )

        if not clinical_valid:
            logger.error(f"Clinical data validation failed: {clinical_error}")
            raise ValueError(f"Invalid clinical data: {clinical_error}")

        logger.info(f"Starting reconciliation: {len(df_invoice)} invoices vs {len(df_clinical)} clinical logs")

        # Extract clinical descriptions
        clinical_descriptions = df_clinical[CLINICAL_COLUMNS["clinical_item"]].tolist()

        # Process each invoice item
        results = []

        for index, row in df_invoice.iterrows():
            vendor_item = row[INVOICE_COLUMNS["vendor_item"]]

            # Find best match
            match_name, match_score = self.fuzzy_match_item(
                vendor_item,
                clinical_descriptions
            )

            # Classify risk
            status, risk_level = self.classify_risk(match_score)

            # Compile result
            results.append({
                "PO_Number": row[INVOICE_COLUMNS["po_number"]],
                "Vendor_Item": vendor_item,
                "Clinical_Match": match_name,
                "Confidence_Score": f"{match_score}%",
                "Confidence_Score_Numeric": match_score,
                "Unit_Cost": f"${row[INVOICE_COLUMNS['unit_cost']]:,.2f}",
                "Cost_At_Risk": row[INVOICE_COLUMNS["unit_cost"]],
                "Status": status,
                "Risk_Level": risk_level
            })

        df_results = pd.DataFrame(results)

        logger.info(f"Reconciliation complete: {len(df_results)} items processed")

        return df_results


    def generate_summary_stats(self, df_results: pd.DataFrame) -> Dict[str, Dict]:
        """
        Generate summary statistics from reconciliation results.

        Args:
            df_results (pd.DataFrame): Reconciliation results

        Returns:
            Dict[str, Dict]: Summary statistics by risk level
        """
        summary = {}

        for risk_level in [RISK_LEVELS["HIGH"], RISK_LEVELS["MEDIUM"], RISK_LEVELS["LOW"]]:
            filtered = df_results[df_results['Risk_Level'] == risk_level]

            summary[risk_level] = {
                "count": len(filtered),
                "total_amount": filtered['Cost_At_Risk'].sum(),
                "avg_amount": filtered['Cost_At_Risk'].mean() if len(filtered) > 0 else 0
            }

        return summary


# Standalone function for quick reconciliation
def quick_reconcile(
    invoice_path: str,
    clinical_path: str,
    threshold: int = 70
) -> pd.DataFrame:
    """
    Quick reconciliation from file paths.

    Args:
        invoice_path (str): Path to invoice CSV
        clinical_path (str): Path to clinical CSV
        threshold (int): Match threshold

    Returns:
        pd.DataFrame: Reconciliation results
    """
    df_inv = pd.read_csv(invoice_path)
    df_clin = pd.read_csv(clinical_path)

    engine = ReconciliationEngine(match_threshold=threshold)
    results = engine.reconcile(df_inv, df_clin)

    return results
