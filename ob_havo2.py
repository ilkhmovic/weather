from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QPainter, QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QDialog,QGraphicsScene, QGraphicsPixmapItem
from datetime import datetime , timedelta
from PyQt6.QtCore import QByteArray
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest
import pytz
import sys
import os

import requests

API_KEY = "d72e4b87a7294a71a4b205350253103"
CITY = "Tashkent"
URL = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={CITY}&days=10&aqi=no&alerts=no"

response = requests.get(URL)
data = response.json()

daily_forecast = {}

for entry in data["forecast"]["forecastday"]:
    date_txt = entry["date"]  # Faqat sana qismini olish

    # Har bir kun uchun o'rtacha bosimni hisoblash
    pressures = [hour["pressure_mb"] for hour in entry["hour"]]  # Kun bo'yi soatlik bosim qiymatlari
    avg_pressure = sum(pressures) / len(pressures)  # O'rtacha bosimni hisoblash

    # Agar sana allaqachon mavjud bo'lsa, mavjud ma'lumotlarni yangilaymiz
    if date_txt in daily_forecast:
        daily_forecast[date_txt]["temp_max"] = max(daily_forecast[date_txt]["temp_max"], entry["day"]["maxtemp_c"])
        daily_forecast[date_txt]["temp_min"] = min(daily_forecast[date_txt]["temp_min"], entry["day"]["mintemp_c"])
        daily_forecast[date_txt]["humidity"].append(entry["day"]["avghumidity"])
        daily_forecast[date_txt]["wind_speed"].append(entry["day"]["maxwind_kph"])
        daily_forecast[date_txt]["pressure"].append(avg_pressure)  # O'rtacha bosim qo'shildi
    else:
        # Yangi kun uchun ma'lumot yaratamiz
        daily_forecast[date_txt] = {
            "temp_max": entry["day"]["maxtemp_c"],  
            "temp_min": entry["day"]["mintemp_c"],  
            "humidity": [entry["day"]["avghumidity"]],  
            "wind_speed": [entry["day"]["maxwind_kph"]],
            "pressure": [avg_pressure],  # O'rtacha bosimni qo'shdik
            "description": entry["day"]["condition"]["text"],  # To'g'ri yo'l
            "icon": entry["day"]["condition"]["icon"]  # To'g'ri yo'l
        }

tashkent_tz = pytz.timezone("Asia/Tashkent")

# Hozirgi Toshkent vaqti
bugun = datetime.now(tashkent_tz).strftime("%Y-%m-%d")
ertaga = (datetime.now(tashkent_tz) + timedelta(days=1)).strftime("%Y-%m-%d")
indinga = (datetime.now(tashkent_tz) + timedelta(days=2)).strftime("%Y-%m-%d")
torinchi = (datetime.now(tashkent_tz) + timedelta(days=3)).strftime("%Y-%m-%d")
beshinchi = (datetime.now(tashkent_tz) + timedelta(days=4)).strftime("%Y-%m-%d")
oltinchi = (datetime.now(tashkent_tz) + timedelta(days=5)).strftime("%Y-%m-%d")
class MyWindow(QDialog):
    def __init__(self):
        super().__init__()

        # UI yuklash
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Oyna sozlamalari
        self.setWindowTitle("Ob-havo ma'lumotlari")
        self.setGeometry(100, 100, 964, 781)

        # Tugmachani bosganda vaqtni yangilashni bog‘laymiz
        self.ui.pushButton.clicked.connect(self.update_time)
        self.ui.pushButton.clicked.connect(self.update_weather)

        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_image_loaded)

        # 🔹 Qaysi kun uchun qaysi view ishlatilishini ko‘rsatamiz
        self.image_views = {
            bugun: self.ui.graphicsView_2,
            ertaga: self.ui.graphicsView_3,
            indinga: self.ui.graphicsView_4,
            torinchi: self.ui.graphicsView_5,
            beshinchi: self.ui.graphicsView_6,
            oltinchi: self.ui.graphicsView_7
        }

        self.update_weather()  # Dastur ishga tushganda yuklash

    def get_custom_icon_url(self, icon_url):
        base_url = "https:"  # WeatherAPI URL'lari https bilan boshlanadi
        return base_url + icon_url if icon_url else "https://cdn-icons-png.flaticon.com/512/1160/1160358.png"




    def load_weather_icon(self, icon_code, view):
        image_url = self.get_custom_icon_url(icon_code)
        request = QNetworkRequest(QtCore.QUrl(image_url))
        reply = self.network_manager.get(request)
        reply.view = view  # Qaysi view uchun yuklanganini eslab qolish
    
    def on_image_loaded(self, reply):
        image = QImage()
        image.loadFromData(reply.readAll())
        view = reply.view
        if not image.isNull():
            pixmap = QPixmap.fromImage(image)

        # Grafik sahifa o'lchamlarini olish
            view_width = view.width()
            view_height = view.height()

        # Original o'lchamlarni saqlash
            pixmap_width = pixmap.width()
            pixmap_height = pixmap.height()

        # Aspect ratio hisoblash
            aspect_ratio = pixmap_width / pixmap_height

        # Yangi o'lchamlarni hisoblash
            if view_width / view_height > aspect_ratio:
                new_width = int(view_height * aspect_ratio)  # floatni int ga o'zgartiramiz
                new_height = int(view_height)
            else:
                new_width = int(view_width)
                new_height = int(view_width / aspect_ratio)

        # Yangi o'lchamga moslashtirish
            pixmap = pixmap.scaled(new_width, new_height, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)

        # Sahifaga rasmni qo'shish
            scene = QGraphicsScene()
            item = QGraphicsPixmapItem(pixmap)
            scene.addItem(item)
            view.setScene(scene)

        reply.deleteLater()  # Xotirani tozalash


    def update_weather(self):
        self.ui.label.setText(f"📍 Shahar: {CITY} \n 🌡️ Harorat: {int(daily_forecast[bugun]['temp_max'])}°C")
        self.ui.label_2.setText(f"💧 Namlik: {int(daily_forecast[bugun]['humidity'][0])}% \n 🌬️ Shamol: {int(daily_forecast[bugun]['wind_speed'][0])} m/s \n 🌍 Bosim: {int(daily_forecast[bugun]['pressure'][0])} hPa")

    # 🔹 Tasvirlarni yuklash
        for date, view in self.image_views.items():
            if date in daily_forecast:
                icon_code = daily_forecast[date]["icon"]
                self.load_weather_icon(icon_code, view)



    def update_time(self):
        """Hozirgi vaqtni yangilaydi"""
        now = datetime.now().strftime("%H:%M:%S")
        self.ui.label_4.setText(now)  # label_4 da vaqtni yangilash

class Ui_Dialog:
     def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(964, 781)
        self.graphicsView = QtWidgets.QGraphicsView(parent=Dialog)
        self.graphicsView.setGeometry(QtCore.QRect(0, 0, 964, 781))
        self.graphicsView.setObjectName("graphicsView")
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        # 📌 ORQA FON RASMNI YUKLASH
        file_path = r"C:\Users\PRESTIGE\Documents\rasmlar\martin-masson-eGs_tNhEMvQ-unsplash.jpg"
        pixmap = QPixmap(file_path)

        if pixmap.isNull():
            print("❌ Rasm yuklanmadi! Yo‘l yoki faylni tekshiring.")
        else:
            scaled_pixmap = pixmap.scaled(self.graphicsView.width(), 
                                          self.graphicsView.height(), 
                                          QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                          QtCore.Qt.TransformationMode.SmoothTransformation)
            item = QGraphicsPixmapItem(scaled_pixmap)
            self.scene.addItem(item)
            self.scene.setSceneRect(0, 0, self.graphicsView.width(), self.graphicsView.height())
            item.setPos(0, 0)
        self.graphicsView_2 = QtWidgets.QGraphicsView(parent=Dialog)
        self.graphicsView_2.setGeometry(QtCore.QRect(20, 20, 550, 401))
        self.graphicsView_2.setStyleSheet("background-color: rgba(0, 0, 0, 50);border-radius:8px;border: 1px solid black;")
        self.graphicsView_2.setObjectName("graphicsView_2")
        self.label = QtWidgets.QLabel(parent=Dialog)
        self.label.setGeometry(QtCore.QRect(580, 90, 360, 161))
        self.label.setStyleSheet("background-color: rgba(0, 0, 0, 50);font-size:20px;border-radius:8px;border: 1px solid black;")
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(parent=Dialog)
        self.label_2.setGeometry(QtCore.QRect(580, 260, 360, 161))
        self.label_2.setStyleSheet("background-color: rgba(0, 0, 0, 50);font-size:20px;border-radius:8px;border: 1px solid black;")
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(parent=Dialog)
        self.label_3.setGeometry(QtCore.QRect(580, 20, 165, 61))
        self.label_3.setStyleSheet("background-color: rgba(0, 0, 0, 50);font-size:20px;border-radius:8px;border: 1px solid black;padding-left:20px;")
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(parent=Dialog)
        self.label_4.setGeometry(QtCore.QRect(750, 20, 190, 61))
        self.label_4.setStyleSheet("background-color: rgba(0, 0, 0, 50);font-size:20px;border-radius:8px;border: 1px solid black;padding-left:40px")
        self.label_4.setObjectName("label_4")
        self.textBrowser = QtWidgets.QTextBrowser(parent=Dialog)
        self.textBrowser.setGeometry(QtCore.QRect(20, 430, 181, 261))
        self.textBrowser.setStyleSheet("background-color: rgba(0, 0, 0, 150);color:lightgreen;border: 1px solid black;border-radius:8px;padding-top:150px;font-size:15px;padding-left:8px")
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser_2 = QtWidgets.QTextBrowser(parent=Dialog)
        self.textBrowser_2.setGeometry(QtCore.QRect(210, 430, 171, 261))
        self.textBrowser_2.setStyleSheet("background-color: rgba(0, 0, 0, 150);color:lightgreen;border: 1px solid black;border-radius:8px;padding-top:150px;font-size:15px;padding-left:8px")
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.textBrowser_3 = QtWidgets.QTextBrowser(parent=Dialog)
        self.textBrowser_3.setGeometry(QtCore.QRect(770, 430, 171, 261))
        self.textBrowser_3.setStyleSheet("background-color: rgba(0, 0, 0, 150);color:lightgreen;border: 1px solid black;border-radius:8px;padding-top:150px;font-size:15px;padding-left:8px")
        self.textBrowser_3.setObjectName("textBrowser_3")
        self.textBrowser_4 = QtWidgets.QTextBrowser(parent=Dialog)
        self.textBrowser_4.setGeometry(QtCore.QRect(390, 430, 181, 261))
        self.textBrowser_4.setStyleSheet("background-color: rgba(0, 0, 0, 150);color:lightgreen;border: 1px solid black;border-radius:8px;padding-top:150px;font-size:15px;padding-left:8px")
        self.textBrowser_4.setObjectName("textBrowser_4")
        self.textBrowser_5 = QtWidgets.QTextBrowser(parent=Dialog)
        self.textBrowser_5.setGeometry(QtCore.QRect(580, 430, 181, 261))
        self.textBrowser_5.setStyleSheet("background-color: rgba(0, 0, 0, 150);color:lightgreen;border: 1px solid black;border-radius:8px;padding-top:150px;font-size:15px;padding-left:8px")
        self.textBrowser_5.setObjectName("textBrowser_5")
        self.graphicsView_3 = QtWidgets.QGraphicsView(parent=Dialog)
        self.graphicsView_3.setGeometry(QtCore.QRect(30, 440, 161, 131))
        self.graphicsView_3.setStyleSheet("background-color: rgba(0, 0, 0, 50);border-radius:8px;border: 1px solid black;")
        self.graphicsView_3.setObjectName("graphicsView_3")
        self.graphicsView_4 = QtWidgets.QGraphicsView(parent=Dialog)
        self.graphicsView_4.setGeometry(QtCore.QRect(220, 440, 151, 131))
        self.graphicsView_4.setStyleSheet("background-color: rgba(0, 0, 0, 50);border-radius:8px;border: 1px solid black;")
        self.graphicsView_4.setObjectName("graphicsView_4")
        self.graphicsView_5 = QtWidgets.QGraphicsView(parent=Dialog)
        self.graphicsView_5.setGeometry(QtCore.QRect(780, 440, 151, 131))
        self.graphicsView_5.setStyleSheet("background-color: rgba(0, 0, 0, 50);border-radius:8px;border: 1px solid black;")
        self.graphicsView_5.setObjectName("graphicsView_5")
        self.graphicsView_6 = QtWidgets.QGraphicsView(parent=Dialog)
        self.graphicsView_6.setGeometry(QtCore.QRect(400, 440, 161, 131))
        self.graphicsView_6.setStyleSheet("background-color: rgba(0, 0, 0, 50);border-radius:8px;border: 1px solid black;")
        self.graphicsView_6.setObjectName("graphicsView_6")
        self.graphicsView_7 = QtWidgets.QGraphicsView(parent=Dialog)
        self.graphicsView_7.setGeometry(QtCore.QRect(590, 440, 161, 131))
        self.graphicsView_7.setStyleSheet("background-color: rgba(0, 0, 0, 50);border-radius:8px;border: 1px solid black;")
        self.graphicsView_7.setObjectName("graphicsView_7")
        self.graphicsView_8 = QtWidgets.QGraphicsView(parent=Dialog)
        self.graphicsView_8.setGeometry(QtCore.QRect(960, 440, 151, 131))
        self.graphicsView_8.setStyleSheet("background-color: rgba(0, 0, 0, 50);border-radius:8px;border: 1px solid black;")
        self.graphicsView_8.setObjectName("graphicsView_8")
        self.pushButton = QtWidgets.QPushButton(parent=Dialog)
        self.pushButton.setGeometry(QtCore.QRect(20, 710, 920, 51))
        self.pushButton.setStyleSheet("background-color: rgba(0, 0, 0, 150);border: 1px solid black;\n"
"border-radius:10px;\n"
"color:white;\n"
"font-size:20px;")
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
     

     def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", f"📍 Shahar: {CITY} \n 🌡️ Harorat: {int(daily_forecast[bugun]['temp_max'])}°C"))
        self.label_2.setText(_translate("Dialog", 
            f"💧 Namlik: {int(sum(daily_forecast[bugun]['humidity']) / len(daily_forecast[bugun]['humidity']))}% \n "
            f"🌬️ Shamol tezligi: {int(sum(daily_forecast[bugun]['wind_speed']) / len(daily_forecast[bugun]['wind_speed']))} m/s \n "
            f"🌍 Bosim: {int(daily_forecast[bugun]['pressure'][0])} hPa"))

        self.label_3.setText(_translate("Dialog", "Hozirgi vaqt"))
        self.label_4.setText(_translate("Dialog", datetime.now().strftime("%H:%M:%S")))

        self.textBrowser.setText(_translate("Dialog", 
            f"🌡️ Harorat: {int(daily_forecast[ertaga]['temp_max'])}°C \n"
            f"💧 Namlik: {int(sum(daily_forecast[ertaga]['humidity']) / len(daily_forecast[ertaga]['humidity']))}% \n"
            f"🌬️ Shamol: {int(sum(daily_forecast[ertaga]['wind_speed']) / len(daily_forecast[ertaga]['wind_speed']))} m/s \n"
            f"🌍 Bosim: {int(daily_forecast[ertaga]['pressure'][0])} hPa"))

        self.textBrowser_2.setText(_translate("Dialog", 
            f"🌡️ Harorat: {int(daily_forecast[indinga]['temp_max'])}°C \n"
            f"💧 Namlik: {int(sum(daily_forecast[indinga]['humidity']) / len(daily_forecast[indinga]['humidity']))}% \n"
            f"🌬️ Shamol: {int(sum(daily_forecast[indinga]['wind_speed']) / len(daily_forecast[indinga]['wind_speed']))} m/s \n"
            f"🌍 Bosim: {int(daily_forecast[indinga]['pressure'][0])} hPa"))

        self.textBrowser_3.setText(_translate("Dialog", 
            f"🌡️ Harorat: {int(daily_forecast[torinchi]['temp_max'])}°C \n"
            f"💧 Namlik: {int(sum(daily_forecast[torinchi]['humidity']) / len(daily_forecast[torinchi]['humidity']))}% \n"
            f"🌬️ Shamol: {int(sum(daily_forecast[torinchi]['wind_speed']) / len(daily_forecast[torinchi]['wind_speed']))} m/s \n"
            f"🌍 Bosim: {int(daily_forecast[torinchi]['pressure'][0])} hPa"))

        self.textBrowser_4.setText(_translate("Dialog", 
            f"🌡️ Harorat: {int(daily_forecast[beshinchi]['temp_max'])}°C \n"
            f"💧 Namlik: {int(sum(daily_forecast[beshinchi]['humidity']) / len(daily_forecast[beshinchi]['humidity']))}% \n"
            f"🌬️ Shamol: {int(sum(daily_forecast[beshinchi]['wind_speed']) / len(daily_forecast[beshinchi]['wind_speed']))} m/s \n"
            f"🌍 Bosim: {int(daily_forecast[beshinchi]['pressure'][0])} hPa"))

        self.textBrowser_5.setText(_translate("Dialog", 
            f"🌡️ Harorat: {int(daily_forecast[oltinchi]['temp_max'])}°C \n"
            f"💧 Namlik: {int(sum(daily_forecast[oltinchi]['humidity']) / len(daily_forecast[oltinchi]['humidity']))}% \n"
            f"🌬️ Shamol: {int(sum(daily_forecast[oltinchi]['wind_speed']) / len(daily_forecast[oltinchi]['wind_speed']))} m/s \n"
            f"🌍 Bosim: {int(daily_forecast[oltinchi]['pressure'][0])} hPa"))

        self.pushButton.setText(_translate("Dialog", "Ma'lumotlarni yangilash"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
