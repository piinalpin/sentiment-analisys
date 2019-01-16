from flask import Flask
app = Flask (__name__)

from app.modul.views import upload
from app.modul.views import upload_hasil
from app.modul.views import Index
from app.modul.views import hasil
from app.modul.views import Grafik
