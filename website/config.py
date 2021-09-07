from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = 'rajesh aka the king'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{"database.db"}'
    UPLOAD_PATH = 'static'
    IMAGE_UPLOADS = os.path.join(BASE_DIR, UPLOAD_PATH , "img") #"D:\\Project\\Bynder\\website\\static\\img"
    FILE_UPLOADS = os.path.join(BASE_DIR, UPLOAD_PATH , "uploads") #"D:\\Project\\Bynder\\website\\static\\uploads"
