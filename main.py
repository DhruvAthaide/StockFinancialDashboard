# Import necessary libraries
import math
import datetime as dt
import numpy as np
import yfinance as yf
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import TextInput, Button, DatePicker, MultiChoice, Div, Spacer, ColorBar
from bokeh.transform import linear_cmap
from bokeh.palettes import Viridis256
from bokeh.models.tickers import BasicTicker
from bokeh.transform import jitter

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

# Function to generate candlestick plot based on selected data and indicators
def candlestick_plot(data, indicators, sync_axis=None):
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
            df['SMA30'] = df['Close'].rolling(30).mean()
            p.line(df.index, df.SMA30, color="purple", legend_label="30 Day SMA")

        elif indicator == "100 Day SMA":
            df['SMA100'] = df['Close'].rolling(100).mean()
            p.line(df.index, df.SMA100, color="blue", legend_label="100 Day SMA")

        elif indicator == "Linear Regression Line":
            par = np.polyfit(range(len(df.index.values)), df.Close.values, 1, full=True)
            slope = par[0][0]
            intercept = par[0][1]
            y_predicted = [slope * i + intercept for i in range(len(df.index.values))]
            p.segment(df.index[0], y_predicted[0], df.index[-1], y_predicted[-1], legend_label="Linear Regression", color="red")
        
        elif indicator == "50 Day EMA":
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            p.line(df.index, df.EMA50, color="orange", legend_label="50 Day EMA")
        
        elif indicator == "RSI":
            delta = df['Close'].diff(1)
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            p.line(df.index, df.RSI, color="brown", legend_label="RSI")

        elif indicator == "MACD":
            short_ema = df['Close'].ewm(span=12, adjust=False).mean()
            long_ema = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = short_ema - long_ema
            df['Signal Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            p.line(df.index, df.MACD, color="blue", legend_label="MACD")
            p.line(df.index, df['Signal Line'], color="green", legend_label="Signal Line")
        
        elif indicator == "Bollinger Bands":
            df['SMA20'] = df['Close'].rolling(window=20).mean()
            df['Upper Band'] = df['SMA20'] + 2 * df['Close'].rolling(window=20).std()
            df['Lower Band'] = df['SMA20'] - 2 * df['Close'].rolling(window=20).std()
            p.line(df.index, df['Upper Band'], color="gray", legend_label="Upper Bollinger Band")
            p.line(df.index, df['Lower Band'], color="gray", legend_label="Lower Bollinger Band")

        p.legend.location = "top_left"  # Set legend position
        p.legend.click_policy = "hide"  # Allow legends to be clicked for toggling visibility

    return p

# Additional visualization tools
def heatmap_plot(data):
    p = figure(title="Heatmap of Daily Returns", tools="pan,box_zoom,reset,save", width=500, height=500)
    data['Returns'] = data['Close'].pct_change() * 100
    mapper = linear_cmap(field_name='Returns', palette=Viridis256, low=-10, high=10)
    p.rect(x='Date', y='Returns', width=1, height=1, source=data, fill_color=mapper, line_color=None)
    color_bar = ColorBar(color_mapper=mapper['transform'], width=8, location=(0,0), ticker=BasicTicker())
    p.add_layout(color_bar, 'right')
    return p

def scatter_plot(data):
    p = figure(title="Price vs Volume Scatter Plot", x_axis_label="Volume", y_axis_label="Close Price", tools="pan,box_zoom,reset,save", width=500, height=500)
    p.scatter(data['Volume'], data['Close'], color="navy", alpha=0.5)
    return p

def bar_chart(data):
    p = figure(title="Daily Volume Bar Chart", x_axis_type="datetime", width=1000, height=400)
    p.vbar(x=data.index, top=data['Volume'], width=0.5, color="blue", legend_label="Volume")
    return p

# Callback function to handle button click event and update plots
def on_button_click():
    main_stock = stock1_text.value
    comparison_stock = stock2_text.value
    start = date_picker_from.value
    end = date_picker_to.value
    indicators = indicator_choice.value
    
    source1, source2 = load_data(main_stock, comparison_stock, start, end)
    p = candlestick_plot(source1, indicators)
    p2 = candlestick_plot(source2, indicators, sync_axis=p.x_range)

    # Additional visualization plots
    heatmap = heatmap_plot(source1)
    scatter = scatter_plot(source1)
    bar = bar_chart(source1)

    # Clear previous elements in the document and add the layout and updated plots
    curdoc().clear()
    curdoc().add_root(layout)
    curdoc().add_root(column(row(p, p2), row(heatmap, scatter, bar)))

# Creating input widgets for user inputs
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

# Load button
load_button = Button(label="Load and Plot Data", button_type="success")
load_button.on_click(on_button_click)

# Layout setup for input controls and plot display
layout = column(
    row(stock1_text, stock2_text),
    row(date_picker_from, date_picker_to),
    indicator_choice,
    load_button
)

curdoc().add_root(layout)
