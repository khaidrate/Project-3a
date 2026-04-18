# Stock Data Visualization
**IT4320 Software Engineering — Project 3**

## khai's instructions:

**1. Get a free API key**
Go to https://www.alphavantage.co/support/#api-key and sign up for a free key, but you should already have one, and the project files include one.

**2. Add your API key**
Open `config.py` and replace `YOUR_API_KEY_HERE` with your actual key:
```python
API_KEY = "your_key_goes_here"
```

**3. Install dependencies** (one time only)
Open a terminal inside the project folder and run:
```
pip install -r requirements.txt
```

**4. Run the application**
```
python main.py
```

---

## How to Use It

Once running, the app will walk you through five prompts in order:

| Prompt | Example Input |
|---|---|
| Stock symbol | `AAPL`, `TSLA`, `GOOGL` |
| Chart type | `1` for Bar, `2` for Line |
| Time series | `1` Daily, `2` Weekly, `3` Monthly |
| Beginning date | `2022-01-01` |
| End date | `2023-01-01` |

After the last prompt, the app fetches the data and opens your chart in the browser. The chart is also saved as `SYMBOL_chart.html` in the project folder so you can reopen it anytime.

---

## File Structure
Just in case
```
Stock Visualizer/
├── main.py                  ← Entry point — run this to start the app
├── config.py                ← API key and shared settings
├── task1_stock_symbol.py    ← Handles stock symbol input
├── task2_chart_type.py      ← Handles chart type selection
├── task3_time_series.py     ← Handles time series function selection
├── task4_begin_date.py      ← Handles beginning date input
├── task5_end_date.py        ← Handles end date input and validation
├── task6_visualizer.py      ← Fetches API data and generates the chart
└── requirements.txt         ← Python package dependencies
```
enjoy
