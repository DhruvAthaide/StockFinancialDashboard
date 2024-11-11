# Importing necessary libraries
import math
import datetime as dt
import numpy as np
import yfinance as yf
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import TextInput, Button, DatePicker, MultiChoice, Div, Spacer

# Function to load stock data for two given tickers within a date range
def load_data(ticker1, ticker2, start, end):
    try:
        df1 = yf.download(ticker1, start=start, end=end)
        df2 = yf.download(ticker2, start=start, end=end)
        if df1.empty or df2.empty:
            raise ValueError(f"Data not found for tickers {ticker1} or {ticker2}")
        return df1, df2
    except Exception as e:
        raise ValueError("Error loading data") from e

# Function to update and generate a plot based on selected data and indicators
def update_plot(data, indicators, sync_axis=None):
    df = data 
    gain = df.Close > df.Open  # Boolean array for days with closing price higher than opening
    loss = df.Open > df.Close  # Boolean array for days with opening price higher than closing
    width = 12 * 60 * 60 * 1000  # Width of each candlestick bar (half day in milliseconds)

    # Create a Bokeh figure with datetime x-axis and optional synchronized x-axis
    if sync_axis is not None:
        p = figure(x_axis_type="datetime", tools="pan,wheel_zoom,box_zoom,reset,save", width=1000, x_range=sync_axis)
    else:
        p = figure(x_axis_type="datetime", tools="pan,wheel_zoom,box_zoom,reset,save", width=1000)

    p.xaxis.major_label_orientation = math.pi / 4  # Rotate x-axis labels for readability
    p.grid.grid_line_alpha = 0.3  # Set grid line transparency

    # Add high-low lines and candlestick bars for gain/loss days
    p.segment(df.index, df.High, df.index, df.Low, color="black")  # High-low line
    p.vbar(df.index[gain], width, df.Open[gain], df.Close[gain], fill_color="#00ff00", line_color="#00ff00")  # Gain bars
    p.vbar(df.index[loss], width, df.Open[loss], df.Close[loss], fill_color="#ff0000", line_color="#ff0000")  # Loss bars

    # Loop through selected indicators and plot each
    for indicator in indicators:
        if indicator == "30 Day SMA":
            # Calculate and plot 30-day Simple Moving Average (SMA)
            df['SMA30'] = df['Close'].rolling(30).mean()
            p.line(df.index, df.SMA30, color="purple", legend_label="30 Day SMA")

        elif indicator == "100 Day SMA":
            # Calculate and plot 100-day Simple Moving Average (SMA)
            df['SMA100'] = df['Close'].rolling(100).mean()
            p.line(df.index, df.SMA100, color="blue", legend_label="100 Day SMA")

        elif indicator == "Linear Regression Line":
            # Calculate and plot Linear Regression Line
            par = np.polyfit(range(len(df.index.values)), df.Close.values, 1, full=True)
            slope = par[0][0]
            intercept = par[0][1]
            y_predicted = [slope * i + intercept for i in range(len(df.index.values))]
            p.segment(df.index[0], y_predicted[0], df.index[-1], y_predicted[-1], legend_label="Linear Regression", color="red")
        
        elif indicator == "50 Day EMA":
            # Calculate and plot 50-day Exponential Moving Average (EMA)
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            p.line(df.index, df.EMA50, color="orange", legend_label="50 Day EMA")
        
        elif indicator == "RSI":
            # Calculate and plot Relative Strength Index (RSI)
            delta = df['Close'].diff(1)
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            p.line(df.index, df.RSI, color="brown", legend_label="RSI")

        elif indicator == "MACD":
            # Calculate and plot Moving Average Convergence Divergence (MACD)
            short_ema = df['Close'].ewm(span=12, adjust=False).mean()
            long_ema = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = short_ema - long_ema
            df['Signal Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            p.line(df.index, df.MACD, color="blue", legend_label="MACD")
            p.line(df.index, df['Signal Line'], color="green", legend_label="Signal Line")
        
        elif indicator == "Bollinger Bands":
            # Calculate and plot Bollinger Bands
            df['SMA20'] = df['Close'].rolling(window=20).mean()
            df['Upper Band'] = df['SMA20'] + 2 * df['Close'].rolling(window=20).std()
            df['Lower Band'] = df['SMA20'] - 2 * df['Close'].rolling(window=20).std()
            p.line(df.index, df['Upper Band'], color="gray", legend_label="Upper Bollinger Band")
            p.line(df.index, df['Lower Band'], color="gray", legend_label="Lower Bollinger Band")

        p.legend.location = "top_left"  # Set legend position
        p.legend.click_policy = "hide"  # Allow legends to be clicked for toggling visibility

    return p

# Callback function to handle button click event and update plots
def on_button_click():
    main_stock = stock1_text.value
    comparison_stock = stock2_text.value
    start = date_picker_from.value
    end = date_picker_to.value
    indicators = indicator_choice.value
    
    source1, source2 = load_data(main_stock, comparison_stock, start, end)
    p = update_plot(source1, indicators)
    p2 = update_plot(source2, indicators, sync_axis=p.x_range)

    # Clear previous elements in the document and add the layout and updated plots
    curdoc().clear()
    curdoc().add_root(layout)
    curdoc().add_root(row(p, p2))

# Creating input widgets for user inputs with improved titles and tooltips
stock1_text = TextInput(title="Main Stock Ticker", placeholder="Enter Main Stock Symbol")
stock2_text = TextInput(title="Comparison Stock Ticker", placeholder="Enter Comparison Stock Symbol")
date_picker_from = DatePicker(title='Start Date', value="2020-01-01", min_date="2000-01-01", max_date=dt.datetime.now().strftime("%Y-%m-%d"))
date_picker_to = DatePicker(title='End Date', value=dt.datetime.now().strftime("%Y-%m-%d"), min_date="2000-01-01", max_date=dt.datetime.now().strftime("%Y-%m-%d"))

# Indicators Choices
indicator_choice = MultiChoice(
    title="Select Indicators", 
    options=[
        "100 Day SMA", 
        "30 Day SMA", 
        "Linear Regression Line", 
        "50 Day EMA", 
        "RSI", 
        "MACD", 
        "Bollinger Bands"
    ], 
    placeholder="Choose one or more indicators"
)

# Load button to trigger data load and plot update with a modern look
load_button = Button(label="Load Data & Plot", button_type="primary", width=200)
load_button.on_click(on_button_click)

# Header's CSS Styling
header_style = """
<style>
    .header-text {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        color: #333;
        margin-bottom: 20px;
    }
</style>
"""

# Improved layout with descriptions and spacing
header = Div(
    text=header_style + "<div class='header-text'>Stock Financial Dashboard</div><p style='text-align:center;'>Analyze and Compare two Stocks with Indicators</p>",
    stylesheets=[header_style]
)
spacer = Spacer(height=20)

# Arrange widgets in a vertical layout with grouping
layout = column(
    header,
    spacer,
    row(stock1_text, stock2_text, width=600),
    row(date_picker_from, date_picker_to, width=400),
    indicator_choice,
    load_button,
)

# Add the layout to the Bokeh document
curdoc().clear()
curdoc().add_root(layout)
