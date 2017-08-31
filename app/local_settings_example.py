import os
import datetime

# *****************************
# Environment specific settings
# *****************************

# DO NOT use "DEBUG = True" in production environments
DEBUG = True

# DO NOT use Unsecure Secrets in production environments
# Generate a safe one with:
#     python -c "import os; print repr(os.urandom(24));"
SECRET_KEY = "This is an UNSECURE Secret. CHANGE THIS for production environments."

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = "sqlite:///../app.sqlite"
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Flask-Mail settings
# For smtp.gmail.com to work, you MUST set "Allow less secure apps" to ON in Google Accounts.
# Change it in https://myaccount.google.com/security#connectedapps (near the bottom).
MAIL_SERVER = "localhost"
MAIL_PORT = 25
MAIL_USE_SSL = False
MAIL_USE_TLS = False
MAIL_USERNAME = ""
MAIL_PASSWORD = ""
MAIL_DEFAULT_SENDER = "'Your Name' <test@localhost>"
MAIL_DEFAULT_SENDER_EMAIL = "test@localhost"

ADMINS = [
    "'Admin' <admin@localhost>",
    ]

# ETH_WALLET_ADDRESS = "0x0"
# BTC_WALLET_ADDRESS = "1"

# ETC/ETH Wallet addresses must be lowercase
ETC_WALLET_ADDRESS = "Put the wallet to monitor here".lower()

# Block to start monitoring at, no point in tracking old blocks
ETC_MIN_BLOCK = 4376000
# Parity RPC address for ETC
ETC_RPC_ADDRESS = "http://localhost:8545" 

# Delay in seconds between checking for changes on the blockchains
BLOCK_CHECK_DELAY = 5 

# Delay between email alerts
EMAIL_TIME_LIMIT = datetime.timedelta(minutes=15) 

# Use RabbitMQ
CELERY_BROKER_URL="Celery broker URL" 