#configeuring the app
from flask import Flask
from models import db
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