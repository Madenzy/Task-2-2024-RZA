#configeuring the app
from flask import Flask
from models import db
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = 'RZA_Task_2_Secret_Key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///rza_task_2.db' 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #
def configure_app(app: Flask):
    app.secret_key = 'RZA_Task_2_Secret_Key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rza_task_2.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)



# --- Stripe ---
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    # --- App URLs (force local testing) ---
BASE_URL = "http://127.0.0.1:5000"

    # --- Mail ---
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT", 465))
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "False") == "True"
MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "True") == "True"
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")