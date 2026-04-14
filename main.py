import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
import webbrowser
import re


class WeatherMusicBot:
    def __init__(self):
        self.city = "Омск"
        self.weather_data = None

        # Грустный плейлист (для пасмурной погоды)
        self.sad_playlist = {
            'songs': [
                {'name': 'Radiohead - Creep', 'url': 'https://www.youtube.com/watch?v=XFkzRNyygfk',
                 'lyrics': 'I\'m a creep, I\'m a weirdo...'},
                {'name': 'Adele - Someone Like You', 'url': 'https://www.youtube.com/watch?v=hLQl3WQQoQ0',
                 'lyrics': 'Never mind, I\'ll find someone like you...'},
                {'name': 'Billie Eilish - when the party\'s over', 'url': 'https://www.youtube.com/watch?v=4sRhuFPsPUI',
                 'lyrics': 'Don\'t you know I\'m no good for you?'},
                {'name': 'Coldplay - The Scientist', 'url': 'https://www.youtube.com/watch?v=RB-RcX5DS5A',
                 'lyrics': 'Nobody said it was easy...'},
                {'name': 'Linkin Park - Numb', 'url': 'https://www.youtube.com/watch?v=kXYiU_JCYtU',
                 'lyrics': 'I\'m tired of being what you want me to be...'},
                {'name': 'Eminem - Stan', 'url': 'https://www.youtube.com/watch?v=gOMhN-hfMtY',
                 'lyrics': 'My tea\'s gone cold, I\'m wondering why...'},
                {'name': 'The Beatles - Yesterday', 'url': 'https://www.youtube.com/watch?v=NrgmdOz227I',
                 'lyrics': 'Yesterday, all my troubles seemed so far away...'},
                {'name': 'Nirvana - Something In The Way', 'url': 'https://www.youtube.com/watch?v=O9eIIl4MjO8',
                 'lyrics': 'Something in the way, mmm...'},
                {'name': 'Lana Del Rey - Summertime Sadness', 'url': 'https://www.youtube.com/watch?v=TdrL3QxjyVw',
                 'lyrics': 'I got my summertime sadness...'},
                {'name': 'Imagine Dragons - Demons', 'url': 'https://www.youtube.com/watch?v=mWRsgZuwf_8',
                 'lyrics': 'When you feel my heat, look into my eyes...'}
            ],
            'description': '🎵 ГРУСТНЫЙ ПЛЕЙЛИСТ для пасмурной погоды 🎵',
            'emoji': '☁️😢'
        }

        # Энергичный рок плейлист (для хорошей погоды)
        self.rock_playlist = {
            'songs': [
                {'name': 'Queen - We Will Rock You', 'url': 'https://www.youtube.com/watch?v=tsTH9TpxU_Y',
                 'lyrics': 'Buddy you\'re a boy make a big noise...'},
                {'name': 'AC/DC - Thunderstruck', 'url': 'https://www.youtube.com/watch?v=v2AC41dglnM',
                 'lyrics': 'Thunder, thunder, thunderstruck!'},
                {'name': 'Bon Jovi - Livin\' On A Prayer', 'url': 'https://www.youtube.com/watch?v=lDK9QqIzhwk',
                 'lyrics': 'Whoa, we\'re halfway there, whoa, livin\' on a prayer!'},
                {'name': 'Guns N\' Roses - Sweet Child O\' Mine', 'url': 'https://www.youtube.com/watch?v=1w7OgIMMRc4',
                 'lyrics': 'She\'s got a smile that it seems to me...'},
                {'name': 'Nirvana - Smells Like Teen Spirit', 'url': 'https://www.youtube.com/watch?v=hTWKbfoikeg',
                 'lyrics': 'Load up on guns, bring your friends...'},
                {'name': 'Metallica - Enter Sandman', 'url': 'https://www.youtube.com/watch?v=CD-E-LDc384',
                 'lyrics': 'Say your prayers, little one...'},
                {'name': 'The Rolling Stones - Satisfaction', 'url': 'https://www.youtube.com/watch?v=nrIPxlFzDi0',
                 'lyrics': 'I can\'t get no satisfaction...'},
                {'name': 'Foo Fighters - The Pretender', 'url': 'https://www.youtube.com/watch?v=SBjQ9tuuTJQ',
                 'lyrics': 'What if I say I\'m not like the others?'},
                {'name': 'Linkin Park - In The End', 'url': 'https://www.youtube.com/watch?v=eVTXPUF4Oz4',
                 'lyrics': 'I tried so hard and got so far...'},
                {'name': 'Green Day - American Idiot', 'url': 'https://www.youtube.com/watch?v=Ee_uujKuJMI',
                 'lyrics': 'Don\'t wanna be an American idiot...'}
            ],
            'description': '🎸 ЭНЕРГИЧНЫЙ РОК ПЛЕЙЛИСТ! 🎸',
            'emoji': '☀️🎸'
        }

    def get_weather_from_gismeteo(self):
        """
        Парсит погоду с сайта Gismeteo для Омска
        """
        url = 'https://www.gismeteo.ru/weather-omsk-4578/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # Ищем описание погоды (облачность)
            weather_tab = soup.find('div', class_='weathertab is-active')
            weather_desc = 'Не определено'

            if weather_tab:
                # Ищем tooltip с описанием погоды
                tooltip = weather_tab.get('data-tooltip', '')
                if tooltip:
                    weather_desc = tooltip
                else:
                    # Альтернативный поиск описания
                    icon_group = weather_tab.find('div', class_='weather-icon-group')
                    if icon_group:
                        parent = weather_tab.find_parent()
                        if parent:
                            desc_elem = parent.find('div', class_='tooltip-text')
                            if desc_elem:
                                weather_desc = desc_elem.text.strip()
            else:
                # Поиск в блоке current weather
                cw_block = soup.find('div', class_='cw')
                if cw_block:
                    desc_elem = cw_block.find('div', class_='description')
                    if desc_elem:
                        weather_desc = desc_elem.text.strip()

            # Поиск температуры
            temp_elem = soup.find('temperature-value', {'value': True})
            if not temp_elem:
                temp_elem = soup.find('span', class_='unit unit_temperature_c')

            temperature = None
            if temp_elem:
                if temp_elem.name == 'temperature-value':
                    temp_value = temp_elem.get('value')
                else:
                    temp_value = temp_elem.text
                try:
                    temperature = int(float(temp_value))
                except:
                    temperature = None

            # Определяем, пасмурно ли
            cloudy_keywords = ['пасмурно', 'облачно', 'тучи', 'дождь', 'снег', 'морось', 'гроза', 'пасмурная']
            is_cloudy = any(keyword in weather_desc.lower() for keyword in cloudy_keywords)

            # Если не удалось определить по ключевым словам, пробуем по иконке
            if weather_tab and not is_cloudy:
                icon_use = weather_tab.find('use')
                if icon_use:
                    href = icon_use.get('href', '')
                    # Иконки с облаками: d_c2, d_c3, n_c2, n_c3 и т.д.
                    if '_c2' in href or '_c3' in href or '_c4' in href:
                        is_cloudy = True
                    elif '_c0' in href or '_c1' in href:
                        is_cloudy = False

            return {
                'condition': 'пасмурно' if is_cloudy else 'ясно/солнечно',
                'description': weather_desc,
                'temperature': temperature if temperature else 'Н/Д',
                'city': self.city,
                'is_cloudy': is_cloudy
            }

        except Exception as e:
            print(f"❌ Ошибка при получении погоды: {e}")
            return self.get_demo_weather()

    def get_demo_weather(self):
        """
        Демо-режим для тестирования
        """
        print("\n🔧 ДЕМО-РЕЖИМ: Использую тестовые данные")

        # Случайный выбор погоды
        weather_types = [
            {'desc': 'Пасмурно, небольшой дождь', 'cloudy': True, 'temp': 5},
            {'desc': 'Ясно, солнечно', 'cloudy': False, 'temp': 18},
            {'desc': 'Облачно с прояснениями', 'cloudy': True, 'temp': 8},
            {'desc': 'Солнечно, без осадков', 'cloudy': False, 'temp': 22}
        ]

        selected = random.choice(weather_types)

        return {
            'condition': 'пасмурно' if selected['cloudy'] else 'ясно/солнечно',
            'description': selected['desc'],
            'temperature': selected['temp'],
            'city': self.city,
            'is_cloudy': selected['cloudy']
        }

    def get_music_recommendation(self, is_cloudy):
        """
        Возвращает плейлист в зависимости от погоды
        """
        if is_cloudy:
            return self.sad_playlist
        else:
            return self.rock_playlist

    def display_song(self, song, index, total):
        """
        Отображает информацию о песне
        """
        print(f"\n{'=' * 60}")
        print(f"🎵 Песня {index + 1} из {total}")
        print(f"{'=' * 60}")
        print(f"📀 Название: {song['name']}")
        print(f"🔗 Ссылка: {song['url']}")
        print(f"📝 Отрывок текста: {song['lyrics']}")
        print(f"{'=' * 60}")

        choice = input("\n❓ Открыть ссылку в браузере? (да/нет): ").lower()
        if choice in ['да', 'yes', 'y', 'д']:
            webbrowser.open(song['url'])
            print("✅ Ссылка открыта в браузере!")

    def display_playlist(self, playlist, weather_info):
        """
        Отображает весь плейлист
        """
        print("\n" + "=" * 60)
        print(f"🌤️ ПОГОДА В ГОРОДЕ {weather_info['city'].upper()}")
        print("=" * 60)
        print(f"📊 Условия: {weather_info['description']}")
        if weather_info['temperature'] != 'Н/Д':
            print(f"🌡️ Температура: {weather_info['temperature']}°C")
        print(f"🎵 Настроение: {playlist['emoji']}")
        print("=" * 60)

        print(f"\n{playlist['description']}")
        print("-" * 60)

        for i, song in enumerate(playlist['songs']):
            print(f"{i + 1}. {song['name']}")

        print("-" * 60)

        while True:
            try:
                choice = input(f"\n🎯 Выберите номер песни (1-{len(playlist['songs'])})\n"
                               f"Или введите '0' чтобы показать все песни с текстом: ")

                if choice == '0':
                    for i, song in enumerate(playlist['songs']):
                        self.display_song(song, i, len(playlist['songs']))
                        if i < len(playlist['songs']) - 1:
                            input("\nНажмите Enter для продолжения...")
                    break
                else:
                    idx = int(choice) - 1
                    if 0 <= idx < len(playlist['songs']):
                        self.display_song(playlist['songs'][idx], idx, len(playlist['songs']))
                        break
                    else:
                        print(f"❌ Пожалуйста, введите число от 1 до {len(playlist['songs'])}")
            except ValueError:
                print("❌ Пожалуйста, введите корректное число")

    def run(self):
        """
        Запуск бота
        """
        print("\n" + "=" * 60)
        print("🤖 MUSIC WEATHER BOT 🤖")
        print("=" * 60)
        print(f"\n📍 Город: {self.city}")
        print("🌍 Получаю данные о погоде с Gismeteo...")

        # Получаем погоду
        self.weather_data = self.get_weather_from_gismeteo()

        if not self.weather_data:
            print("❌ Не удалось получить данные о погоде")
            return

        # Определяем плейлист
        playlist = self.get_music_recommendation(self.weather_data['is_cloudy'])

        # Показываем плейлист
        self.display_playlist(playlist, self.weather_data)

        print("\n👋 Спасибо за использование Music Weather Bot!")


def main():
    bot = WeatherMusicBot()
    bot.run()


if __name__ == "__main__":
    main()
