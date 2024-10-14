import yfinance as yf
import sqlite3
from datetime import datetime
import logging
import os


# Define paths

LOG_DIR = 'logs/'
DB_PATH = 'data/stocks.db'

# Setup logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'stock_fetcher.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Stock symbols
SYMBOLS = {
'VWCE.DE': 'Vanguard All World ETF',
'OR.PA': "L'Oréal",
"RDDT": 'Reddit'
}

def create_database():
    """Create the SQLite database and table if they don't exist"""
    try: 
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                company_name TEXT NOT NULL,
                price REAL NOT NULL,
                timestamp DATETIME NOT NULL
            )
        ''')

        conn.commit()
        conn.close()
        logging.info(f"Database initialized at {DB_PATH}")
    except Exception as e:
        logging.error(f"Database creation error: {str(e)}")
        raise

def fetch_and_store_data():
    """Fetch current stock prices and store them in the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        current_time = datetime.now()

        for symbol, company_name in SYMBOLS.items():
            try:
                # Fetch stock data
                stock = yf.Ticker(symbol)
                # Only way to retrieve current price for ETFs
                if symbol == 'VWCE.DE':
                    current_price = stock.info['ask']
                # For other stocks we can retrieve it normally
                else:
                    current_price = stock.info['currentPrice']

                # Store in the database
                cursor.execute('''
                    INSERT INTO stock_prices (symbol, company_name, price, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (symbol, company_name, current_price, current_time))

                conn.commit()
            
                logging.info(f"Successfully fetched and stored data for {company_name}")

            except Exception as e:
                logging.error(f"Error fetching data for {company_name}: {str(e)}")
                continue

    except Exception as e:
        logging.error(f"Database operation error: {str(e)}")
        raise

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    try: 
        create_database()
        fetch_and_store_data()
    except Exception as e:
        logging.error(f"Main execution error: {str(e)}")
