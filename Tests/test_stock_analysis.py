import unittest
from datetime import datetime
from ..main import load_data, update_plot
import pandas as pd

class TestStockAnalysis(unittest.TestCase):

    def test_load_data_valid_tickers(self):
        # Testing if load_data correctly fetches data for valid tickers
        ticker1 = "AAPL"
        ticker2 = "MSFT"
        start = "2020-01-01"
        end = "2021-01-01"
        
        df1, df2 = load_data(ticker1, ticker2, start, end)
        
        # Assert data is not empty
        self.assertGreater(len(df1), 0)
        self.assertGreater(len(df2), 0)
    
    def test_load_data_invalid_ticker(self):
        # Testing load_data with an invalid ticker
        ticker1 = "INVALID"
        ticker2 = "MSFT"
        start = "2020-01-01"
        end = "2021-01-01"
        
        with self.assertRaises(ValueError):
            load_data(ticker1, ticker2, start, end)

    def test_update_plot_with_sma_indicator(self):
        # Test update_plot function with 30-day SMA indicator
        ticker = "AAPL"
        start = "2020-01-01"
        end = "2021-01-01"
        df, _ = load_data(ticker, ticker, start, end)
        indicators = ["30 Day SMA"]
        
        plot = update_plot(df, indicators)
        
        # Test if the plot has the expected number of lines for the 30 Day SMA
        self.assertTrue(any(legend.label == "30 Day SMA" for legend in plot.legend.items))
    
    def test_update_plot_without_indicators(self):
        # Test update_plot function with no indicators
        indicators = []
        some_data = {
                        "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                        "Open": [100, 101, 102],
                        "Close": [101, 102, 103],
                        "Volume": [5000, 5200, 5300]
                    }

        # Convert to DataFrame
        df = pd.DataFrame(some_data)

        # Call the update_plot with the DataFrame
        plot = update_plot(df, indicators)
        plot.clear_renderers()
        ticker = "AAPL"
        start = "2020-01-01"
        end = "2021-01-01"
        df, _ = load_data(ticker, ticker, start, end)
        indicators = []
        
        plot = update_plot(df, indicators)
        
        # Ensure no lines are added for indicators
        self.assertEqual(len(plot.renderers), 1)  # Only candlestick chart should be present

if __name__ == "__main__":
    unittest.main()
