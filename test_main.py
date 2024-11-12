import pytest
import pandas as pd
from datetime import datetime
from main import load_data, update_plot
from bokeh.plotting import figure

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

def test_update_plot():
    # Test plot creation with no indicators
    plot = update_plot(mock_data, [])
    assert isinstance(plot, figure)
    assert len(plot.renderers) > 0  # Should have at least candlestick renderers

    # Test plot creation with all indicators
    all_indicators = [
        "100 Day SMA", "30 Day SMA", "Linear Regression Line",
        "50 Day EMA", "RSI", "MACD", "Bollinger Bands"
    ]
    plot = update_plot(mock_data, all_indicators)
    assert isinstance(plot, figure)
    assert len(plot.renderers) > len(all_indicators)  # Should have candlesticks + all indicators

def test_indicator_calculations():
    # Test SMA calculation
    plot = update_plot(mock_data, ["30 Day SMA"])
    assert 'SMA30' in mock_data.columns

    # Test EMA calculation
    plot = update_plot(mock_data, ["50 Day EMA"])
    assert 'EMA50' in mock_data.columns

    # Test RSI calculation
    plot = update_plot(mock_data, ["RSI"])
    assert 'RSI' in mock_data.columns

    # Test MACD calculation
    plot = update_plot(mock_data, ["MACD"])
    assert 'MACD' in mock_data.columns
    assert 'Signal Line' in mock_data.columns

    # Test Bollinger Bands calculation
    plot = update_plot(mock_data, ["Bollinger Bands"])
    assert 'Upper Band' in mock_data.columns
    assert 'Lower Band' in mock_data.columns


if __name__ == "__main__":
    pytest.main([__file__])