# =============================================================================
# app.py — Flask Application Entry Point
# =============================================================================
# Provides two routes:
#   GET  /  → renders the form (loads stock symbols from stocks.csv)
#   POST /  → reads form data, queries Alpha Vantage, returns the chart
# =============================================================================

import csv
import os
from datetime import datetime

from flask import Flask, render_template, request

from config import TIME_SERIES_OPTIONS, CHART_TYPE_OPTIONS
from task6_visualizer import fetch_stock_data, generate_chart_html

app = Flask(__name__)


# --------------------------------------------------------------------------- #
#  Helper — Load Stock Symbols from CSV
# --------------------------------------------------------------------------- #

def load_stock_symbols() -> list[str]:
    """
    Reads stock symbols from stocks.csv located in the same directory.
    Tries common column names ('Symbol', 'Ticker', 'symbol', 'ticker').

    Returns:
        list[str]: Sorted list of stock ticker symbols.
    """
    csv_path = os.path.join(os.path.dirname(__file__), "stocks.csv")
    symbols = []

    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Normalize header names to handle variations
            headers = reader.fieldnames or []
            symbol_col = next(
                (h for h in headers if h.strip().lower() in ("symbol", "ticker")),
                None,
            )

            if symbol_col is None:
                # Fallback: use the first column
                symbol_col = headers[0] if headers else None

            if symbol_col:
                for row in reader:
                    val = row.get(symbol_col, "").strip().upper()
                    if val:
                        symbols.append(val)

    except FileNotFoundError:
        # If CSV is missing, return a small default list so the app still runs
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META"]

    return sorted(set(symbols))


# --------------------------------------------------------------------------- #
#  Routes
# --------------------------------------------------------------------------- #

@app.route("/", methods=["GET", "POST"])
def index():
    """
    GET  — render the empty form.
    POST — validate inputs, fetch data, render the form + chart.
    """
    symbols    = load_stock_symbols()
    chart_html = None
    error      = None

    # Preserve what the user selected so the form re-populates after submit
    form_data = {
        "symbol":      "",
        "chart_type":  "1",
        "time_series": "1",
        "begin_date":  "",
        "end_date":    "",
    }

    if request.method == "POST":
        # Pull values from the submitted form
        form_data["symbol"]      = request.form.get("symbol", "").strip().upper()
        form_data["chart_type"]  = request.form.get("chart_type", "1")
        form_data["time_series"] = request.form.get("time_series", "1")
        form_data["begin_date"]  = request.form.get("begin_date", "")
        form_data["end_date"]    = request.form.get("end_date", "")

        symbol      = form_data["symbol"]
        chart_type  = CHART_TYPE_OPTIONS.get(form_data["chart_type"], {}).get("type", "line")
        ts_option   = TIME_SERIES_OPTIONS.get(form_data["time_series"])

        try:
            # Validate dates
            begin_date = datetime.strptime(form_data["begin_date"], "%Y-%m-%d")
            end_date   = datetime.strptime(form_data["end_date"],   "%Y-%m-%d")

            if end_date < begin_date:
                raise ValueError("End date cannot be before begin date.")

            if ts_option is None:
                raise ValueError("Invalid time series selection.")

            # Fetch data from Alpha Vantage and build the chart
            raw_data   = fetch_stock_data(symbol, ts_option["function"])
            chart_html = generate_chart_html(
                symbol, chart_type, ts_option["json_key"],
                raw_data, begin_date, end_date
            )

        except ValueError as exc:
            error = str(exc)
        except Exception as exc:
            error = f"Unexpected error: {exc}"

    return render_template(
        "index.html",
        symbols=symbols,
        chart_types=CHART_TYPE_OPTIONS,
        time_series_options=TIME_SERIES_OPTIONS,
        chart_html=chart_html,
        error=error,
        form_data=form_data,
    )


# --------------------------------------------------------------------------- #
#  Run
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # host='0.0.0.0' makes the app reachable inside Docker
    app.run(host="0.0.0.0", port=5000, debug=True)
