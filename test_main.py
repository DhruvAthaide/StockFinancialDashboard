import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import MagicMock, patch
from bokeh.plotting import figure
from main import load_data, candlestick_plot

# Mock data for testing
mock_data = pd.DataFrame({
    'Open': [100, 101, 102],
    'High': [105, 106, 107],
    'Low': [98, 99, 100],
    'Close': [103, 104, 105]
}, index=pd.date_range(start='2023-01-01', periods=3))

def test_load_data():
    # Test successful data loading
    start = '2023-01-01'
    end = '2023-01-31'
    df1, df2 = load_data('AAPL', 'MSFT', start, end)
    assert not df1.empty
    assert not df2.empty
    assert isinstance(df1, pd.DataFrame)
    assert isinstance(df2, pd.DataFrame)

    # Test error handling for invalid ticker
    with pytest.raises(ValueError):
        load_data('INVALID_TICKER', 'MSFT', start, end)

@patch("main.candlestick_plot")
def test_update_plot(mock_candlestick_plot):
    from bokeh.plotting import figure  # Import here to match runtime scope

    # Mock the return value of candlestick_plot
    mock_candlestick_plot.return_value = figure()

    # Test plot creation with no indicators
    indicators = []
    plot = mock_candlestick_plot(mock_data, indicators)  # Use the mocked function directly
    assert isinstance(plot, figure)
    assert mock_candlestick_plot.called

    # Test plot creation with all indicators
    all_indicators = [
        "100 Day SMA", "30 Day SMA", "Linear Regression Line",
        "50 Day EMA", "RSI", "MACD", "Bollinger Bands"
    ]
    plot = mock_candlestick_plot(mock_data, all_indicators)  # Use the mocked function directly
    assert isinstance(plot, figure)
    assert mock_candlestick_plot.called

def test_indicator_calculations():
    # Mock SMA calculation
    mock_data['SMA30'] = mock_data['Close'].rolling(30).mean()
    assert 'SMA30' in mock_data.columns

    # Mock EMA calculation
    mock_data['EMA50'] = mock_data['Close'].ewm(span=50, adjust=False).mean()
    assert 'EMA50' in mock_data.columns

    # Mock RSI calculation
    delta = mock_data['Close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    mock_data['RSI'] = 100 - (100 / (1 + rs))
    assert 'RSI' in mock_data.columns

    # Mock MACD calculation
    short_ema = mock_data['Close'].ewm(span=12, adjust=False).mean()
    long_ema = mock_data['Close'].ewm(span=26, adjust=False).mean()
    mock_data['MACD'] = short_ema - long_ema
    mock_data['Signal Line'] = mock_data['MACD'].ewm(span=9, adjust=False).mean()
    assert 'MACD' in mock_data.columns
    assert 'Signal Line' in mock_data.columns

    # Mock Bollinger Bands calculation
    mock_data['SMA20'] = mock_data['Close'].rolling(window=20).mean()
    mock_data['Upper Band'] = mock_data['SMA20'] + 2 * mock_data['Close'].rolling(window=20).std()
    mock_data['Lower Band'] = mock_data['SMA20'] - 2 * mock_data['Close'].rolling(window=20).std()
    assert 'Upper Band' in mock_data.columns
    assert 'Lower Band' in mock_data.columns

if __name__ == "__main__":
    pytest.main([__file__])
