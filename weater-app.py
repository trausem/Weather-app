import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

API_KEY = "TWÓJ_API_KEY_TUTAJ" 

def get_weather(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric", "lang": "pl"}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Błąd", f"Nie można pobrać danych pogodowych: {e}")
        return None


def get_forecast(city):
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": API_KEY, "units": "metric", "lang": "pl"}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Błąd", f"Nie można pobrać prognozy pogody: {e}")
        return None


def update_weather():
    city = city_entry.get()
    if not city:
        messagebox.showwarning("Uwaga", "Proszę wpisać nazwę miasta!")
        return

    weather_data = get_weather(city)
    if weather_data and weather_data["cod"] == 200:
        temp = weather_data["main"]["temp"]
        desc = weather_data["weather"][0]["description"]
        icon = weather_data["weather"][0]["icon"]

        temperature_label.config(text=f"Temperatura: {temp}°C")
        description_label.config(text=f"Opis: {desc.capitalize()}")

        icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
        icon_response = requests.get(icon_url, stream=True)
        if icon_response.status_code == 200:
            img_data = icon_response.content
            img = Image.open(io.BytesIO(img_data)).resize((100, 100))
            weather_icon = ImageTk.PhotoImage(img)
            icon_label.config(image=weather_icon, borderwidth=2, relief="solid")
            icon_label.image = weather_icon

        forecast_data = get_forecast(city)
        if forecast_data and forecast_data["cod"] == "200":
            forecast_text = ""
            times, temps = [], []
            for forecast in forecast_data["list"][:5]:
                dt_txt = forecast["dt_txt"]
                temp = forecast["main"]["temp"]
                desc = forecast["weather"][0]["description"]
                forecast_text += f"{dt_txt}: {temp}°C, {desc}\n"
                times.append(dt_txt)
                temps.append(temp)
            forecast_label.config(text=forecast_text)

            fig, ax = plt.subplots()
            ax.plot(times, temps, marker='o')
            ax.set_title("Prognoza temperatury", color="white")
            ax.set_xlabel("Czas", color="white")
            ax.set_ylabel("Temperatura (°C)", color="white")
            ax.tick_params(colors="white")
            fig.patch.set_facecolor("#333")
            ax.set_facecolor("#444")
            fig.autofmt_xdate()

            for widget in plot_frame.winfo_children():
                widget.destroy()

            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10)

            plt.close(fig)

    else:
        messagebox.showerror("Błąd", "Nie znaleziono miasta lub wystąpił problem z API!")


root = tk.Tk()
root.title("Aplikacja pogodowa")
root.geometry("800x800")
root.resizable(False, False)
root.config(bg="#333")

city_entry = tk.Entry(root, font=("Arial", 14), bg="#555", fg="white", insertbackground="white")
city_entry.pack(pady=10)

search_button = tk.Button(root, text="Sprawdź pogodę", font=("Arial", 14), command=update_weather, bg="#555", fg="white")
search_button.pack(pady=10)

icon_label = tk.Label(root, bg="#333")
icon_label.pack(pady=10)

temperature_label = tk.Label(root, text="Temperatura: --°C", font=("Arial", 16), bg="#333", fg="white")
temperature_label.pack(pady=5)

description_label = tk.Label(root, text="Opis: --", font=("Arial", 16), bg="#333", fg="white")
description_label.pack(pady=5)

forecast_label = tk.Label(root, text="Prognoza na kilka dni:\n--", font=("Arial", 14), justify="left", bg="#333", fg="white")
forecast_label.pack(pady=10)

plot_frame = tk.Frame(root, bg="#333")
plot_frame.pack(pady=10)

root.mainloop()
