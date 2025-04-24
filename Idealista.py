import requests
from bs4 import BeautifulSoup
import time
import telegram

# Configuración del bot de Telegram
TELEGRAM_TOKEN = '7923351682:AAFdTbSAazSpzz45e-Gakx5NVDY4v0g801s'
CHAT_ID = '7688811483'
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Búsqueda en Idealista (ajustar si querés otra zona o filtros)
IDEALISTA_URL = 'https://www.idealista.com/alquiler-viviendas/madrid/con-precio-hasta_1200,con-foto/'
HEADERS = {'User-Agent': 'Mozilla/5.0'}
KEYWORDS = ['dueño directo', 'particular', 'sin agencia']

# Para guardar los anuncios ya vistos y no repetir
vistos = set()


def buscar_anuncios():
    try:
        res = requests.get(IDEALISTA_URL, headers=HEADERS)
        soup = BeautifulSoup(res.text, 'html.parser')
        anuncios = soup.find_all('article')

        for anuncio in anuncios:
            enlace = anuncio.find('a', class_='item-link')
            if not enlace:
                continue

            titulo = enlace.get_text().lower()
            href = enlace.get('href')
            url_completa = f"https://www.idealista.com{href}"

            precio_elem = anuncio.find('span', class_='item-price')
            m2_elem = anuncio.find('span', class_='item-detail')
            hab_elem = anuncio.find_all('span', class_='item-detail')

            if not precio_elem or not m2_elem:
                continue

            precio = int(precio_elem.get_text().replace('€', '').replace('.', '').strip())
            m2_texto = [elem.get_text() for elem in hab_elem if 'm²' in elem.get_text()]
            m2 = int(m2_texto[0].replace('m²', '').strip()) if m2_texto else 0

            hab_texto = [elem.get_text() for elem in hab_elem if 'hab.' in elem.get_text()]
            habitaciones = int(hab_texto[0].replace('hab.', '').strip()) if hab_texto else 0

            # Condiciones: hasta 1200€, desde junio (en el título), dueño directo, 2 hab o 1 hab con más de 60 m²
            if precio <= 1200 and 'junio' in titulo and any(p in titulo for p in KEYWORDS):
                if habitaciones == 2 or (habitaciones == 1 and m2 >= 60):
                    if url_completa not in vistos:
                        mensaje = f"📢 Nuevo anuncio:
{titulo}\n💶 Precio: {precio}€\n📐 Superficie: {m2} m²\n🛏 Habitaciones: {habitaciones}\n🔗 {url_completa}"
                        bot.send_message(chat_id=CHAT_ID, text=mensaje)
                        vistos.add(url_completa)

    except Exception as e:
        bot.send_message(chat_id=CHAT_ID, text=f"❌ Error en la búsqueda: {e}")


if _name_ == '_main_':
    buscar_anuncios()
    