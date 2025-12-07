from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Hola! Estoy vivo."

def run():
  # Render espera que escuchemos en el puerto 0.0.0.0
  app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()