# =============================================================================
# task6_visualizer.py — Task 6: Fetch data from Alpha Vantage and generate chart
# =============================================================================
# This module handles two responsibilities:
#   1. Querying the Alpha Vantage API for stock data
#   2. Filtering by date range and building the Plotly chart
#
# Two chart generators are provided:
#   - generate_chart()      → saves HTML file and opens in browser (Project 3 CLI)
#   - generate_chart_html() → returns an HTML string for embedding in Flask (Project 4)
# =============================================================================

import os
import sys
import webbrowser
from datetime import datetime

import requests
import plotly.graph_objects as go

from config import API_KEY, BASE_URL


# --------------------------------------------------------------------------- #
#  API Data Fetching
# --------------------------------------------------------------------------- #

def fetch_stock_data(symbol: str, function: str) -> dict:
    """
    Calls the Alpha Vantage API and returns the full JSON response.

    Args:
        symbol   (str): The stock ticker symbol (e.g. 'AAPL').
        function (str): The Alpha Vantage function name
                        (e.g. 'TIME_SERIES_DAILY').

    Returns:
        dict: The raw JSON response from the API.

    Raises:
        RuntimeError: If the API returns an error or the symbol is not found.
    """
    params = {
        "function":   function,
        "symbol":     symbol,
        "outputsize": "full",
        "apikey":     API_KEY,
        "datatype":   "json",
    }

    print(f"\n  Querying Alpha Vantage for '{symbol}' ({function})...")

    try:
        response = requests.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        raise RuntimeError(f"Network error: {err}") from err

    data = response.json()

    # Alpha Vantage returns error info inside the JSON body (not HTTP status)
    if "Error Message" in data:
        raise RuntimeError(f"API Error: {data['Error Message']}")

    if "Information" in data:
        # Usually means the free-tier rate limit was hit
        raise RuntimeError(f"API rate limit hit: {data['Information']}")

    return data


# --------------------------------------------------------------------------- #
#  Data Filtering
# --------------------------------------------------------------------------- #

def filter_by_date_range(
    raw_data:   dict,
    json_key:   str,
    begin_date: datetime,
    end_date:   datetime,
) -> tuple[list[str], list[float]]:
    """
    Extracts closing prices from the API response and filters them to the
    requested date range.

    Args:
        raw_data   (dict):     Full API JSON response.
        json_key   (str):      The key that holds the time series data.
        begin_date (datetime): Start of the date range.
        end_date   (datetime): End of the date range.

    Returns:
        tuple[list[str], list[float]]:
            - Sorted list of date strings (YYYY-MM-DD)
            - Corresponding list of closing prices (float)

    Raises:
        RuntimeError: If the key is missing or no data falls in the range.
    """
    if json_key not in raw_data:
        available = list(raw_data.keys())
        raise RuntimeError(
            f"Expected key '{json_key}' not found in API response. "
            f"Available keys: {available}"
        )

    time_series = raw_data[json_key]

    begin_str = begin_date.strftime("%Y-%m-%d")
    end_str   = end_date.strftime("%Y-%m-%d")

    filtered = {
        date: values
        for date, values in time_series.items()
        if begin_str <= date <= end_str
    }

    if not filtered:
        raise RuntimeError(
            f"No data found between {begin_str} and {end_str}. "
            "Try a wider date range, or check that the stock was active during that period."
        )

    dates  = sorted(filtered.keys())
    closes = [float(filtered[d]["4. close"]) for d in dates]

    return dates, closes


# --------------------------------------------------------------------------- #
#  Chart Generation — CLI Version (Project 3)
# --------------------------------------------------------------------------- #

def generate_chart(
    symbol:     str,
    chart_type: str,
    json_key:   str,
    raw_data:   dict,
    begin_date: datetime,
    end_date:   datetime,
) -> None:
    """
    Filters the stock data, builds a Plotly chart, saves it as an HTML file,
    and opens it in the user's default web browser.
    (Used by Main.py for the original console version.)
    """
    try:
        dates, closes = filter_by_date_range(raw_data, json_key, begin_date, end_date)
    except RuntimeError as err:
        print(f"  [!] {err}")
        sys.exit(1)

    begin_str = begin_date.strftime("%Y-%m-%d")
    end_str   = end_date.strftime("%Y-%m-%d")
    title     = f"{symbol} — Closing Price  ({begin_str} to {end_str})"

    if chart_type == "bar":
        trace = go.Bar(x=dates, y=closes, name=symbol, marker_color="steelblue")
    else:
        trace = go.Scatter(
            x=dates, y=closes, mode="lines+markers", name=symbol,
            line=dict(color="steelblue", width=2),
        )

    fig = go.Figure(data=[trace])
    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis_title="Date",
        yaxis_title="Closing Price (USD)",
        hovermode="x unified",
        template="plotly_white",
    )

    output_file = f"{symbol}_chart.html"
    fig.write_html(output_file)

    abs_path = os.path.abspath(output_file)
    print(f"\n  Chart saved to: {abs_path}")
    print("  Opening chart in your default browser...\n")
    webbrowser.open(f"file://{abs_path}")


# --------------------------------------------------------------------------- #
#  Chart Generation — Web / Flask Version (Project 4)
# --------------------------------------------------------------------------- #

def generate_chart_html(
    symbol:     str,
    chart_type: str,
    json_key:   str,
    raw_data:   dict,
    begin_date: datetime,
    end_date:   datetime,
) -> str:
    """
    Filters the stock data and builds a Plotly chart returned as an HTML
    string suitable for embedding directly inside a Flask template.

    Args:
        symbol     (str):      Stock ticker.
        chart_type (str):      'bar' or 'line'.
        json_key   (str):      Key to locate the time series in raw_data.
        raw_data   (dict):     Full API JSON response from fetch_stock_data().
        begin_date (datetime): Start of the date range.
        end_date   (datetime): End of the date range.

    Returns:
        str: Self-contained Plotly chart HTML snippet (no full <html> wrapper).

    Raises:
        RuntimeError: Propagated from filter_by_date_range on bad input.
    """
    dates, closes = filter_by_date_range(raw_data, json_key, begin_date, end_date)

    begin_str = begin_date.strftime("%Y-%m-%d")
    end_str   = end_date.strftime("%Y-%m-%d")
    title     = f"{symbol} — Closing Price ({begin_str} to {end_str})"

    if chart_type == "bar":
        trace = go.Bar(x=dates, y=closes, name=symbol, marker_color="steelblue")
    else:
        trace = go.Scatter(
            x=dates, y=closes, mode="lines+markers", name=symbol,
            line=dict(color="steelblue", width=2),
        )

    fig = go.Figure(data=[trace])
    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis_title="Date",
        yaxis_title="Closing Price (USD)",
        hovermode="x unified",
        template="plotly_white",
    )

    # full_html=False  → returns only the <div> + <script>, not a full HTML page
    # include_plotlyjs='cdn' → loads Plotly.js from CDN instead of bundling it inline
    return fig.to_html(full_html=False, include_plotlyjs="cdn")
