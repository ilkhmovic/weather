from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QPainter, QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QDialog, QGraphicsScene, QGraphicsPixmapItem
from datetime import datetime, timedelta
from PyQt6.QtCore import QByteArray
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest
import pytz
import sys
import os
import requests

API_KEY = "fab72e45aee8439e81615707251311"
CITY = "Tashkent"
URL = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={CITY}&days=10&aqi=no&alerts=no"

response = requests.get(URL)
data = response.json()

daily_forecast = {}

for entry in data["forecast"]["forecastday"]:
    date_txt = entry["date"]

    pressures = [hour["pressure_mb"] for hour in entry["hour"]]
    avg_pressure = sum(pressures) / len(pressures)

    if date_txt in daily_forecast:
        daily_forecast[date_txt]["temp_max"] = max(daily_forecast[date_txt]["temp_max"], entry["day"]["maxtemp_c"])
        daily_forecast[date_txt]["temp_min"] = min(daily_forecast[date_txt]["temp_min"], entry["day"]["mintemp_c"])
        daily_forecast[date_txt]["humidity"].append(entry["day"]["avghumidity"])
        daily_forecast[date_txt]["wind_speed"].append(entry["day"]["maxwind_kph"])
        daily_forecast[date_txt]["pressure"].append(avg_pressure)
    else:
        daily_forecast[date_txt] = {
            "temp_max": entry["day"]["maxtemp_c"],
            "temp_min": entry["day"]["mintemp_c"],
            "humidity": [entry["day"]["avghumidity"]],
            "wind_speed": [entry["day"]["maxwind_kph"]],
            "pressure": [avg_pressure],
            "description": entry["day"]["condition"]["text"],
            "icon": entry["day"]["condition"]["icon"]
        }

tashkent_tz = pytz.timezone("Asia/Tashkent")

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
        self.setGeometry(100, 100, 1200, 900)  # Kattaroq o'lcham
        self.setMinimumSize(800, 600)  # Minimal o'lcham

        # Tugmachani bosganda vaqtni yangilashni bog'laymiz
        self.ui.pushButton.clicked.connect(self.update_time)
        self.ui.pushButton.clicked.connect(self.update_weather)

        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_image_loaded)

        # Image views
        self.image_views = {
            bugun: self.ui.graphicsView_2,
            ertaga: self.ui.graphicsView_3,
            indinga: self.ui.graphicsView_4,
            torinchi: self.ui.graphicsView_5,
            beshinchi: self.ui.graphicsView_6,
            oltinchi: self.ui.graphicsView_7
        }

        # Layout sozlamalari
        self.setup_layout()

        self.update_weather()

    def setup_layout(self):
        """Layout va resize sozlamalari"""
        # Asosiy layout
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # Widgetlarni layoutga qo'shish
        main_layout.addWidget(self.ui.graphicsView)
        
        # Oynani resize qilish uchun signal
        self.ui.graphicsView.resizeEvent = self.on_resize

    def on_resize(self, event):
        """Oyna o'lchami o'zgarganda chaqiriladi"""
        # Orqa fon rasmni yangilash
        if hasattr(self.ui, 'background_pixmap'):
            scaled_pixmap = self.ui.background_pixmap.scaled(
                self.ui.graphicsView.width(),
                self.ui.graphicsView.height(),
                QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
            if self.ui.scene.items():
                self.ui.scene.items()[0].setPixmap(scaled_pixmap)

        # Widgetlarni yangilash
        self.update_widget_positions()
        super().resizeEvent(event)

    def update_widget_positions(self):
        """Widgetlarni yangi o'lchamga moslashtirish"""
        width = self.width()
        height = self.height()

        # Responsive o'lchamlar
        if width < 1000:  # Kichik ekranlar uchun
            self.setup_small_layout(width, height)
        else:  # Katta ekranlar uchun
            self.setup_large_layout(width, height)

    def setup_large_layout(self, width, height):
        """Katta ekranlar uchun layout"""
        # Asosiy weather info
        self.ui.graphicsView_2.setGeometry(20, 20, width//2 - 40, height//2 - 50)
        
        # Weather details
        label_width = width - (width//2 + 60)
        self.ui.label.setGeometry(width//2 + 20, 90, label_width, 161)
        self.ui.label_2.setGeometry(width//2 + 20, 260, label_width, 161)
        
        # Time labels
        self.ui.label_3.setGeometry(width//2 + 20, 20, label_width//2 - 10, 61)
        self.ui.label_4.setGeometry(width//2 + label_width//2 + 30, 20, label_width//2 - 10, 61)
        
        # Forecast boxes
        box_width = (width - 100) // 6
        box_height = height//3 - 50
        
        positions = [
            (20, height//2 + 20),
            (20 + box_width + 20, height//2 + 20),
            (20 + (box_width + 20)*2, height//2 + 20),
            (20 + (box_width + 20)*3, height//2 + 20),
            (20 + (box_width + 20)*4, height//2 + 20),
            (20 + (box_width + 20)*5, height//2 + 20)
        ]
        
        # Text browsers
        text_browsers = [
            self.ui.textBrowser, self.ui.textBrowser_2, self.ui.textBrowser_4,
            self.ui.textBrowser_5, self.ui.textBrowser_3
        ]
        
        for i, (x, y) in enumerate(positions[:5]):
            if i < len(text_browsers):
                text_browsers[i].setGeometry(x, y, box_width, box_height)
        
        # Graphics views for icons
        icon_views = [
            self.ui.graphicsView_3, self.ui.graphicsView_4, self.ui.graphicsView_6,
            self.ui.graphicsView_7, self.ui.graphicsView_5
        ]
        
        for i, view in enumerate(icon_views):
            if i < len(positions[:5]):
                x, y = positions[i]
                view.setGeometry(x + 10, y + 10, box_width - 20, box_height//2)
        
        # Update button
        self.ui.pushButton.setGeometry(20, height - 70, width - 40, 51)

    def setup_small_layout(self, width, height):
        """Kichik ekranlar uchun layout"""
        # Soddaroq layout kichik ekranlar uchun
        self.ui.graphicsView_2.setGeometry(10, 10, width - 20, height//3)
        self.ui.label.setGeometry(10, height//3 + 20, width - 20, 80)
        self.ui.label_2.setGeometry(10, height//3 + 110, width - 20, 80)
        
        # Forecast - vertical layout
        forecast_height = height//4
        forecast_width = width - 20
        
        forecasts = [
            (self.ui.textBrowser, self.ui.graphicsView_3),
            (self.ui.textBrowser_2, self.ui.graphicsView_4),
            (self.ui.textBrowser_4, self.ui.graphicsView_6),
            (self.ui.textBrowser_5, self.ui.graphicsView_7),
            (self.ui.textBrowser_3, self.ui.graphicsView_5)
        ]
        
        for i, (text_browser, graphics_view) in enumerate(forecasts):
            y_pos = height//2 + 20 + i * (forecast_height + 10)
            text_browser.setGeometry(10, y_pos, forecast_width, forecast_height)
            graphics_view.setGeometry(20, y_pos + 10, forecast_width//6, forecast_height - 20)
        
        self.ui.pushButton.setGeometry(10, height - 60, width - 20, 45)

    def get_custom_icon_url(self, icon_url):
        base_url = "https:"
        return base_url + icon_url if icon_url else "https://cdn-icons-png.flaticon.com/512/1160/1160358.png"

    def load_weather_icon(self, icon_code, view):
        image_url = self.get_custom_icon_url(icon_code)
        request = QNetworkRequest(QtCore.QUrl(image_url))
        reply = self.network_manager.get(request)
        reply.view = view

    def on_image_loaded(self, reply):
        image = QImage()
        image.loadFromData(reply.readAll())
        view = reply.view
        if not image.isNull():
            pixmap = QPixmap.fromImage(image)

            view_width = view.width()
            view_height = view.height()

            pixmap_width = pixmap.width()
            pixmap_height = pixmap.height()

            aspect_ratio = pixmap_width / pixmap_height

            if view_width / view_height > aspect_ratio:
                new_width = int(view_height * aspect_ratio)
                new_height = int(view_height)
            else:
                new_width = int(view_width)
                new_height = int(view_width / aspect_ratio)

            pixmap = pixmap.scaled(new_width, new_height, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)

            scene = QGraphicsScene()
            item = QGraphicsPixmapItem(pixmap)
            scene.addItem(item)
            view.setScene(scene)

        reply.deleteLater()

    def update_weather(self):
        self.ui.label.setText(f"📍 Shahar: {CITY} \n 🌡️ Harorat: {int(daily_forecast[bugun]['temp_max'])}°C")
        self.ui.label_2.setText(f"💧 Namlik: {int(daily_forecast[bugun]['humidity'][0])}% \n 🌬️ Shamol: {int(daily_forecast[bugun]['wind_speed'][0])} m/s \n 🌍 Bosim: {int(daily_forecast[bugun]['pressure'][0])} hPa")

        for date, view in self.image_views.items():
            if date in daily_forecast:
                icon_code = daily_forecast[date]["icon"]
                self.load_weather_icon(icon_code, view)

    def update_time(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.ui.label_4.setText(now)

class Ui_Dialog:
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1200, 900)  # Boshlang'ich o'lchamni kattalashtirdim
        
        # Asosiy background graphics view
        self.graphicsView = QtWidgets.QGraphicsView(parent=Dialog)
        self.graphicsView.setGeometry(QtCore.QRect(0, 0, 1200, 900))
        self.graphicsView.setObjectName("graphicsView")
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        # Orqa fon rasm
        file_path = r"/home/doston/Pictures/desktop image/"
        self.background_pixmap = QPixmap(file_path)
        
        if not self.background_pixmap.isNull():
            scaled_pixmap = self.background_pixmap.scaled(
                self.graphicsView.width(),
                self.graphicsView.height(),
                QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
            item = QGraphicsPixmapItem(scaled_pixmap)
            self.scene.addItem(item)
            self.scene.setSceneRect(0, 0, self.graphicsView.width(), self.graphicsView.height())
            item.setPos(0, 0)

        # Qolgan widgetlar (boshlang'ich pozitsiyalar)
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

        # Text browsers va graphics views
        self.create_forecast_widgets(Dialog)
        
        self.pushButton = QtWidgets.QPushButton(parent=Dialog)
        self.pushButton.setGeometry(QtCore.QRect(20, 820, 1160, 51))
        self.pushButton.setStyleSheet("background-color: rgba(0, 0, 0, 150);border: 1px solid black;border-radius:10px;color:white;font-size:20px;")
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def create_forecast_widgets(self, Dialog):
        """Forecast widgetlarini yaratish"""
        # Text browsers
        self.textBrowser = QtWidgets.QTextBrowser(parent=Dialog)
        self.textBrowser.setGeometry(QtCore.QRect(20, 430, 181, 261))
        self.textBrowser.setStyleSheet("background-color: rgba(0, 0, 0, 150);color:lightgreen;border: 1px solid black;border-radius:8px;padding-top:150px;font-size:15px;padding-left:8px")
        
        self.textBrowser_2 = QtWidgets.QTextBrowser(parent=Dialog)
        self.textBrowser_2.setGeometry(QtCore.QRect(210, 430, 171, 261))
        self.textBrowser_2.setStyleSheet("background-color: rgba(0, 0, 0, 150);color:lightgreen;border: 1px solid black;border-radius:8px;padding-top:150px;font-size:15px;padding-left:8px")
        
        self.textBrowser_3 = QtWidgets.QTextBrowser(parent=Dialog)
        self.textBrowser_3.setGeometry(QtCore.QRect(770, 430, 171, 261))
        self.textBrowser_3.setStyleSheet("background-color: rgba(0, 0, 0, 150);color:lightgreen;border: 1px solid black;border-radius:8px;padding-top:150px;font-size:15px;padding-left:8px")
        
        self.textBrowser_4 = QtWidgets.QTextBrowser(parent=Dialog)
        self.textBrowser_4.setGeometry(QtCore.QRect(390, 430, 181, 261))
        self.textBrowser_4.setStyleSheet("background-color: rgba(0, 0, 0, 150);color:lightgreen;border: 1px solid black;border-radius:8px;padding-top:150px;font-size:15px;padding-left:8px")
        
        self.textBrowser_5 = QtWidgets.QTextBrowser(parent=Dialog)
        self.textBrowser_5.setGeometry(QtCore.QRect(580, 430, 181, 261))
        self.textBrowser_5.setStyleSheet("background-color: rgba(0, 0, 0, 150);color:lightgreen;border: 1px solid black;border-radius:8px;padding-top:150px;font-size:15px;padding-left:8px")

        # Graphics views for icons
        self.graphicsView_3 = QtWidgets.QGraphicsView(parent=Dialog)
        self.graphicsView_3.setGeometry(QtCore.QRect(30, 440, 161, 131))
        self.graphicsView_3.setStyleSheet("background-color: rgba(0, 0, 0, 50);border-radius:8px;border: 1px solid black;")
        
        self.graphicsView_4 = QtWidgets.QGraphicsView(parent=Dialog)
        self.graphicsView_4.setGeometry(QtCore.QRect(220, 440, 151, 131))
        self.graphicsView_4.setStyleSheet("background-color: rgba(0, 0, 0, 50);border-radius:8px;border: 1px solid black;")
        
        self.graphicsView_5 = QtWidgets.QGraphicsView(parent=Dialog)
        self.graphicsView_5.setGeometry(QtCore.QRect(780, 440, 151, 131))
        self.graphicsView_5.setStyleSheet("background-color: rgba(0, 0, 0, 50);border-radius:8px;border: 1px solid black;")
        
        self.graphicsView_6 = QtWidgets.QGraphicsView(parent=Dialog)
        self.graphicsView_6.setGeometry(QtCore.QRect(400, 440, 161, 131))
        self.graphicsView_6.setStyleSheet("background-color: rgba(0, 0, 0, 50);border-radius:8px;border: 1px solid black;")
        
        self.graphicsView_7 = QtWidgets.QGraphicsView(parent=Dialog)
        self.graphicsView_7.setGeometry(QtCore.QRect(590, 440, 161, 131))
        self.graphicsView_7.setStyleSheet("background-color: rgba(0, 0, 0, 50);border-radius:8px;border: 1px solid black;")

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Ob-havo Dasturi"))

        def get_weather_text(date_key):
            if date_key in daily_forecast:
                data = daily_forecast[date_key]
                avg_humidity = int(sum(data['humidity']) / len(data['humidity']))
                avg_wind = int(sum(data['wind_speed']) / len(data['wind_speed']))
                pressure = int(data['pressure'][0])
                return (f"🌡️ Harorat: {int(data['temp_max'])}°C \n"
                        f"💧 Namlik: {avg_humidity}% \n"
                        f"🌬️ Shamol: {avg_wind} m/s \n"
                        f"🌍 Bosim: {pressure} hPa")
            else:
                return "Ma'lumot mavjud emas\n(Free API limiti)"

        if bugun in daily_forecast:
            self.label.setText(_translate("Dialog", f"📍 Shahar: {CITY} \n 🌡️ Harorat: {int(daily_forecast[bugun]['temp_max'])}°C"))
            d = daily_forecast[bugun]
            self.label_2.setText(_translate("Dialog", 
                f"💧 Namlik: {int(sum(d['humidity']) / len(d['humidity']))}% \n "
                f"🌬️ Shamol tezligi: {int(sum(d['wind_speed']) / len(d['wind_speed']))} m/s \n "
                f"🌍 Bosim: {int(d['pressure'][0])} hPa"))
        else:
            self.label.setText("Ma'lumot yo'q")

        self.label_3.setText(_translate("Dialog", "Hozirgi vaqt"))
        self.label_4.setText(_translate("Dialog", datetime.now().strftime("%H:%M:%S")))

        self.textBrowser.setText(_translate("Dialog", get_weather_text(ertaga)))
        self.textBrowser_2.setText(_translate("Dialog", get_weather_text(indinga)))
        self.textBrowser_3.setText(_translate("Dialog", get_weather_text(torinchi)))
        self.textBrowser_4.setText(_translate("Dialog", get_weather_text(beshinchi)))
        self.textBrowser_5.setText(_translate("Dialog", get_weather_text(oltinchi)))

        self.pushButton.setText(_translate("Dialog", "Ma'lumotlarni yangilash"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())