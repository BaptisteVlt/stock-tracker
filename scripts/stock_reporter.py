import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
import yfinance as yf

# Define paths

LOG_DIR = 'logs/'
DB_PATH = 'data/stocks.db'

# Setup logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'stock_reporter.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "stocksnotification64@gmail.com" # Replace
SENDER_PASSWORD = "zidquytjmvkxyepg" # Replace
RECIPIENT_EMAIL = "baptistev91@gmail.com" # Replace

def get_stock_evolution():
    """Calculate stock price evolution since the start of the day"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get start of the day timestamp
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        evolution_data = []

        # Query distinct symbols
        cursor.execute("SELECT DISTINCT symbol, company_name FROM stock_prices")
        stocks = cursor.fetchall()

        for symbol, company_name, in stocks: 
            # Get last price of yesterday
            start_price = yf.Ticker(symbol).info['regularMarketPreviousClose']

            # Get latest price
            cursor.execute("""
                SELECT price
                FROM stock_prices
                WHERE symbol = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (symbol,))

            current_price = cursor.fetchone()

            if start_price and current_price:
                current_price = current_price[0]
                change_percent = ((current_price - start_price) / start_price) * 100

                evolution_data.append({
                    'company': company_name,
                    'symbol': symbol,
                    'start_price': start_price,
                    'current_price': current_price,
                    'change_percent': change_percent
                })
            
        conn.close()
        return evolution_data
        
    except Exception as e:
        logging.error(f"Error calculating stock evolution: {str(e)}")
        raise

def send_email_report(evolution_data):
    """Send email with stock evolution report"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"Stock Evolution Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        # Create HTML email content
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                h1 {{
                    color: #2c3e50;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin-top: 20px;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                th {{
                    backgroung-color: #f2f2f2;
                    color: #2c3e50;
                }}
                .positive {{
                    color: #27ae60;
                }}
                .negative {{
                    color: #c0392b;
                }}
            </style>
        </head>
        <body>
            <h1>Stock Evolution Report</h1>
            <p>Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <table>
                <tr>
                    <th>Company</th>
                    <th>Symbol</th>
                    <th>Start Price</th>
                    <th>Current Price</th>
                    <th>Change (%)</th>
                </tr>
        """

        for stock in evolution_data:
            change_class = 'positive' if stock['change_percent'] >= 0 else 'negative'
            change_sign = '+' if stock['change_percent'] >= 0 else ''
            html += f""" 
                <tr>
                    <td>{stock['company']}</td>
                    <td>{stock['symbol']}</td>
                    <td>${stock['start_price']}</td>
                    <td>${stock['current_price']}</td>
                    <td class="{change_class}">{change_sign}{stock['change_percent']:.2f}%</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, 'html'))

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        logging.info("Email report sent successfully")
    
    except Exception as e:
        logging.error(f"Error send email: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        evolution_data = get_stock_evolution()
        send_email_report(evolution_data)
    except Exception as e:
        logging.error(f"Main execution error: {str(e)}")