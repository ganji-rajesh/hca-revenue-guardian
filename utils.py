"""
Utility functions for data preprocessing and validation.
"""

import pandas as pd
import re
from typing import Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """
    Normalize text for fuzzy matching by removing special characters,
    extra whitespace, and converting to lowercase.

    Args:
        text (str): Raw text string

    Returns:
        str: Normalized text string
    """
    if not isinstance(text, str):
        return str(text)

    # Convert to lowercase
    text = text.lower()

    # Remove special characters (keep alphanumeric and spaces)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)

    # Remove extra whitespace
    text = ' '.join(text.split())

    return text


def validate_dataframe(df: pd.DataFrame, required_columns: list) -> Tuple[bool, Optional[str]]:
    """
    Validate that a DataFrame contains all required columns.

    Args:
        df (pd.DataFrame): DataFrame to validate
        required_columns (list): List of required column names

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if df is None or df.empty:
        return False, "DataFrame is empty"

    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"

    return True, None


def calculate_financial_metrics(df: pd.DataFrame, cost_column: str) -> dict:
    """
    Calculate aggregated financial metrics from a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with financial data
        cost_column (str): Name of the cost column

    Returns:
        dict: Dictionary with financial metrics
    """
    try:
        total_amount = df[cost_column].sum()
        count = len(df)
        avg_amount = df[cost_column].mean()

        return {
            "total_amount": total_amount,
            "count": count,
            "average_amount": avg_amount
        }
    except Exception as e:
        logger.error(f"Error calculating financial metrics: {str(e)}")
        return {
            "total_amount": 0.0,
            "count": 0,
            "average_amount": 0.0
        }


def format_currency(amount: float) -> str:
    """
    Format a number as USD currency.

    Args:
        amount (float): Amount to format

    Returns:
        str: Formatted currency string
    """
    return f"${amount:,.2f}"
