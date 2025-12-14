import os

class Config:
    SECRET_KEY = 'BD_Kursach'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///time_tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
