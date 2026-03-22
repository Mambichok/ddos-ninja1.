import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import sqlite3
import json
import time
import requests
import urllib3
import ssl
import os
import subprocess
import threading
import webbrowser
import socket
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
from datetime import datetime



import os
import re

def load_env(filepath='.env'):
    """Загружает переменные из .env файла"""
    if not os.path.exists(filepath):
        print(f"❌ Файл {filepath} не найден!")
        print(f"   Создаю {filepath}...")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("VK_TOKEN=vk1.a.замени_на_свой_токен\n")
            f.write("ADMIN_ID=579954757\n")
        return False
    
    print(f"✅ Найден файл {filepath}")
    loaded_vars = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            
            if key and value:
                os.environ[key] = value
                loaded_vars.append(key)
                print(f"   Загружена переменная: {key}={value[:10]}...")
    
    print(f"✅ Загружено переменных: {len(loaded_vars)}")
    return len(loaded_vars) > 0

# Загружаем
if not load_env():
    print("\n⚠️ Заполни файл .env и перезапусти бота!")
    input("Нажми Enter для выхода...")
    exit(1)

load_env()




# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ssl_version=ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

# ============ КОНФИГУРАЦИЯ ============
# ============ КОНФИГУРАЦИЯ ============
VK_TOKEN = os.getenv('VK_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

# Валидация и конвертация типов!
if not VK_TOKEN:
    print("❌ Ошибка: Не найден VK_TOKEN в .env!")
    exit(1)

if not ADMIN_ID:
    print("❌ Ошибка: Не найден ADMIN_ID в .env!")
    exit(1)

try:
    ADMIN_ID = int(ADMIN_ID)  # ← ВАЖНО! Конвертируем строку в число
except ValueError:
    print(f"❌ Ошибка: ADMIN_ID должен быть числом, а не '{ADMIN_ID}'")
    exit(1)

print(f"👑 Admin ID загружен: {ADMIN_ID} (тип: {type(ADMIN_ID).__name__})")

# ============ ПУТИ К ИГРАМ ============
GAMES_PATHS = {
    'ddos_jump': r"C:\Users\igor_\OneDrive\Рабочий стол\project\Hackaton_DDG\ddos-jump",
    'ddos_bird': r"C:\Users\igor_\OneDrive\Рабочий стол\project\Hackaton_DDG\ddos-bird",
    'ddos_ninja': r"C:\Users\igor_\OneDrive\Рабочий стол\project\Hackaton_DDG\ddos-ninja",
    'ddos_fishing': r"C:\Users\igor_\OneDrive\Рабочий стол\project\Hackaton_DDG\ddos-fishing",
    'ddos_blust': r"C:\Users\igor_\OneDrive\Рабочий стол\project\Hackaton_DDG\ddos-blust"
}

GAMES_PORTS = {
    'ddos_jump': 8080,
    'ddos_bird': 8081,
    'ddos_ninja': 8082,
    'ddos_fishing': 8083,
    'ddos_blust': 8084
}

# ============ ПЕРЕВОДЫ ============
TRANSLATIONS = {
    'ru': {
        'welcome': "👋 Добро пожаловать!\n\nВыберите язык:",
        'choose_language': "🌍 Выберите язык:",
        'register_btn': "📝 Зарегистрироваться",
        'enter_first_name': "Введите ваше имя:",
        'enter_last_name': "Введите вашу фамилию:",
        'enter_phone': "Введите номер телефона:",
        'registration_complete': "🎉 Регистрация завершена!\n\nДобро пожаловать, {name}!",
        'my_points': "🎯 Мои очки",
        'games_list': "🎮 Список игр",
        'your_points': "🎯 Ваши очки: {points}",
        'choose_game': "🎮 Выберите игру:",
        'back': "🔙 Назад",
        'game_selected': "🎮 Вы выбрали: {game}\n\n👉 {link}\n\n🚀 Игра запускается автоматически...",
        'invalid_name': "⚠️ Имя слишком короткое. Введите корректное имя:",
        'invalid_phone': "⚠️ Номер телефона слишком короткий. Попробуйте ещё раз:",
        'use_buttons': "Используйте кнопки:",
        'start_command': "👋 Напишите /start для начала",
        'language_set': "✅ Язык выбран: Русский",
        'game_not_found': "❌ Игра не найдена на сервере",
        'game_loading': "⏳ Запускаю игру..."
    },
    'en': {
        'welcome': "👋 Welcome!\n\nChoose your language:",
        'choose_language': "🌍 Choose language:",
        'register_btn': "📝 Register",
        'enter_first_name': "Enter your first name:",
        'enter_last_name': "Enter your last name:",
        'enter_phone': "Enter your phone number:",
        'registration_complete': "🎉 Registration complete!\n\nWelcome, {name}!",
        'my_points': "🎯 My Points",
        'games_list': "🎮 Games List",
        'your_points': "🎯 Your points: {points}",
        'choose_game': "🎮 Choose a game:",
        'back': "🔙 Back",
        'game_selected': "🎮 You selected: {game}\n\n👉 {link}\n\n🚀 Launching game...",
        'invalid_name': "⚠️ Name is too short. Please enter a valid name:",
        'invalid_phone': "⚠️ Phone number is too short. Please try again:",
        'use_buttons': "Please use the buttons:",
        'start_command': "👋 Type /start to begin",
        'language_set': "✅ Language selected: English",
        'game_not_found': "❌ Game not found on server",
        'game_loading': "⏳ Launching game..."
    }
}

# ============ МЕНЕДЖЕР ИГР ============
class GameManager:
    def __init__(self):
        self.running_servers = {}
        self.local_ip = self.get_local_ip()
    
    def get_local_ip(self):
        """Получить локальный IP адрес"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "localhost"
    
    def start_game_server(self, game_id):
        """Запустить сервер для игры"""
        if game_id in self.running_servers:
            return f"http://{self.local_ip}:{GAMES_PORTS[game_id]}"
        
        game_path = GAMES_PATHS.get(game_id)
        if not game_path or not os.path.exists(game_path):
            print(f"❌ Папка игры не найдена: {game_path}")
            return None
        
        port = GAMES_PORTS[game_id]
        
        def run_server():
            try:
                os.chdir(game_path)
                # Используем pythonw.exe для скрытого окна (без консоли)
                python_exe = r"C:\Users\igor_\AppData\Local\Programs\Python\Python313\pythonw.exe"
                if not os.path.exists(python_exe):
                    python_exe = r"C:\Users\igor_\AppData\Local\Programs\Python\Python313\python.exe"
                
                subprocess.Popen(
                    [python_exe, "-m", "http.server", str(port)],
                    cwd=game_path,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"✅ Сервер игры {game_id} запущен на порту {port}")
            except Exception as e:
                print(f"❌ Ошибка запуска сервера {game_id}: {e}")
        
        thread = threading.Thread(target=run_server)
        thread.daemon = True
        thread.start()
        
        time.sleep(2)
        
        server_url = f"http://{self.local_ip}:{port}"
        self.running_servers[game_id] = server_url
        return server_url
    
    def open_game_in_browser(self, game_id):
        """Открыть игру в браузере"""
        url = self.start_game_server(game_id)
        if url:
            webbrowser.open(url)
            return url
        return None
    
    def get_game_url(self, game_id):
        """Получить URL игры"""
        return self.running_servers.get(game_id) or self.start_game_server(game_id)

# ============ БАЗА ДАННЫХ ============
class Database:
    def __init__(self, db_file="bot_users.db"):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_tables()
        self.init_games()
    
    def create_tables(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = self.cursor.fetchone()
        
        if not table_exists:
            self.cursor.execute("""
                CREATE TABLE users (
                    user_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    phone TEXT,
                    language TEXT DEFAULT 'ru',
                    points INTEGER DEFAULT 0,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Создана новая таблица users")
        else:
            self.cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in self.cursor.fetchall()]
            
            if 'first_name' not in columns:
                self.cursor.execute("ALTER TABLE users ADD COLUMN first_name TEXT")
            if 'last_name' not in columns:
                self.cursor.execute("ALTER TABLE users ADD COLUMN last_name TEXT")
            if 'language' not in columns:
                self.cursor.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'ru'")
            if 'points' not in columns:
                self.cursor.execute("ALTER TABLE users ADD COLUMN points INTEGER DEFAULT 0")
            if 'registered_at' not in columns:
                self.cursor.execute("ALTER TABLE users ADD COLUMN registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                display_name TEXT,
                link TEXT,
                is_active INTEGER DEFAULT 1,
                icon TEXT
            )
        """)
        
        self.connection.commit()
    
    def init_games(self):
        game_manager = GameManager()
        
        default_games = [
            ('ddos_jump', 'DDoS-Jump', '🕹'),
            ('ddos_bird', 'DDoS-Bird', '🐦'),
            ('ddos_ninja', 'DDoS-Ninja', '🥷'),
            ('ddos_fishing', 'DDoS-Fishing', '🎣'),
            ('ddos_blust', 'DDoS-Blust', '💥')
        ]
        
        for game_id, name, icon in default_games:
            local_url = f"http://{game_manager.local_ip}:{GAMES_PORTS[game_id]}"
            self.cursor.execute("""
                INSERT OR REPLACE INTO games (name, display_name, link, icon) 
                VALUES (?, ?, ?, ?)
            """, (game_id, name, local_url, icon))
        
        self.connection.commit()
    
    def user_exists(self, user_id):
        self.cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone() is not None
    
    def add_user(self, user_id):
        self.cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        self.connection.commit()
    
    def set_language(self, user_id, language):
        self.cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
        self.connection.commit()
    
    def get_language(self, user_id):
        try:
            self.cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
            result = self.cursor.fetchone()
            return result[0] if result else 'ru'
        except:
            return 'ru'
    
    def update_first_name(self, user_id, first_name):
        self.cursor.execute("UPDATE users SET first_name = ? WHERE user_id = ?", (first_name, user_id))
        self.connection.commit()
    
    def update_last_name(self, user_id, last_name):
        self.cursor.execute("UPDATE users SET last_name = ? WHERE user_id = ?", (last_name, user_id))
        self.connection.commit()
    
    def update_phone(self, user_id, phone):
        self.cursor.execute("UPDATE users SET phone = ? WHERE user_id = ?", (phone, user_id))
        self.connection.commit()
    
    def get_user_data(self, user_id):
        self.cursor.execute("SELECT first_name, last_name, phone, points FROM users WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone()
    
    def get_points(self, user_id):
        self.cursor.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0
    
    def get_leaderboard(self, limit=10):
        self.cursor.execute("""
            SELECT first_name, last_name, points 
            FROM users 
            WHERE first_name IS NOT NULL 
            ORDER BY points DESC 
            LIMIT ?
        """, (limit,))
        return self.cursor.fetchall()
    
    def get_active_games(self):
        self.cursor.execute("SELECT name, display_name, link, icon FROM games WHERE is_active = 1")
        return self.cursor.fetchall()
    
    def get_all_games(self):
        self.cursor.execute("SELECT name, display_name, is_active FROM games")
        return self.cursor.fetchall()
    
    def toggle_game(self, game_name):
        self.cursor.execute("""
            UPDATE games 
            SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END 
            WHERE name = ?
        """, (game_name,))
        self.connection.commit()
        return self.cursor.rowcount > 0

# ============ СОСТОЯНИЯ ============
user_states = {}

# ============ КЛАВИАТУРЫ ============
def get_language_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("🇷🇺 Русский", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("🇬🇧 English", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("🇪🇸 Español", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("🇨🇳 中文", color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()

def get_register_keyboard(lang='ru'):
    keyboard = VkKeyboard(one_time=True)
    texts = TRANSLATIONS[lang]
    keyboard.add_button(texts['register_btn'], color=VkKeyboardColor.POSITIVE)
    return keyboard.get_keyboard()

def get_main_keyboard(lang='ru'):
    keyboard = VkKeyboard(one_time=False)
    texts = TRANSLATIONS[lang]
    keyboard.add_button(texts['my_points'], color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button(texts['games_list'], color=VkKeyboardColor.POSITIVE)
    return keyboard.get_keyboard()

def get_games_keyboard(games, lang='ru'):
    keyboard = VkKeyboard(one_time=False)
    texts = TRANSLATIONS[lang]
    
    for i, (game_id, display_name, link, icon) in enumerate(games):
        if i > 0 and i % 2 == 0:
            keyboard.add_line()
        keyboard.add_button(f"{icon} {display_name}", color=VkKeyboardColor.PRIMARY)
    
    keyboard.add_line()
    keyboard.add_button(texts['back'], color=VkKeyboardColor.NEGATIVE)
    
    return keyboard.get_keyboard()

def get_admin_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("📊 Таблица лидеров", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("🎮 Выбрать игру", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("⚙️ Вкл/Выкл игру", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button("🔙 Выйти из админки", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()

def get_admin_games_keyboard(games):
    keyboard = VkKeyboard(one_time=False)
    
    for i, (game_id, display_name, is_active) in enumerate(games):
        if i > 0 and i % 2 == 0:
            keyboard.add_line()
        status = "✅" if is_active else "❌"
        keyboard.add_button(f"{status} {display_name}", color=VkKeyboardColor.SECONDARY)
    
    keyboard.add_line()
    keyboard.add_button("🔙 Назад", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()

# ============ БОТ ============
class VKBot:
    def __init__(self, token, admin_id):
        self.admin_id = admin_id
        self.game_manager = GameManager()
        
        session = requests.Session()
        session.mount('https://', SSLAdapter())
        
        self.vk_session = vk_api.VkApi(token=token, session=session)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)
        self.db = Database()
        
        try:
            group_info = self.vk.groups.getById()
            print(f"✅ Подключено к группе: {group_info[0]['name']}")
            print(f"👑 Admin ID: {admin_id}")
            print(f"🌐 Локальный IP: {self.game_manager.local_ip}")
            print(f"🎮 Игры будут доступны по адресам:")
            for game_id, port in GAMES_PORTS.items():
                print(f"   • {game_id}: http://{self.game_manager.local_ip}:{port}")
        except Exception as e:
            print(f"❌ Ошибка токена: {e}")
            exit(1)
        
        print("🤖 Бот запущен!")
    
    def get_text(self, user_id, key, **kwargs):
        lang = self.db.get_language(user_id)
        text = TRANSLATIONS.get(lang, TRANSLATIONS['ru']).get(key, key)
        return text.format(**kwargs) if kwargs else text
    
    def send_message(self, user_id, message, keyboard=None):
        try:
            params = {
                'user_id': user_id,
                'message': message,
                'random_id': 0
            }
            if keyboard:
                params['keyboard'] = keyboard
            
            self.vk.messages.send(**params)
            return True
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
            return False
    
    def is_admin(self, user_id):
        return user_id == self.admin_id
    
    # ============ ОБРАБОТЧИКИ ============
    def handle_start(self, user_id):
        self.db.add_user(user_id)
        user_states[user_id] = 'select_language'
        self.send_message(
            user_id,
            self.get_text(user_id, 'welcome'),
            get_language_keyboard()
        )
    
    def handle_language_selection(self, user_id, text):
        lang_map = {
            '🇷🇺 русский': 'ru',
            '🇬🇧 english': 'en',
            '🇪🇸 español': 'es',
            '🇨🇳 中文': 'zh'
        }
        
        selected_lang = lang_map.get(text.lower())
        if selected_lang:
            self.db.set_language(user_id, selected_lang)
            user_states[user_id] = 'register'
            
            self.send_message(
                user_id,
                self.get_text(user_id, 'language_set') + "\n\n" + 
                self.get_text(user_id, 'choose_language'),
                get_register_keyboard(selected_lang)
            )
        else:
            self.send_message(user_id, self.get_text(user_id, 'choose_language'), get_language_keyboard())
    
    def handle_register_start(self, user_id):
        user_states[user_id] = 'waiting_first_name'
        self.send_message(user_id, self.get_text(user_id, 'enter_first_name'))
    
    def handle_first_name(self, user_id, text):
        if len(text.strip()) < 2:
            self.send_message(user_id, self.get_text(user_id, 'invalid_name'))
            return
        
        self.db.update_first_name(user_id, text.strip())
        user_states[user_id] = 'waiting_last_name'
        self.send_message(user_id, self.get_text(user_id, 'enter_last_name'))
    
    def handle_last_name(self, user_id, text):
        if len(text.strip()) < 2:
            self.send_message(user_id, self.get_text(user_id, 'invalid_name'))
            return
        
        self.db.update_last_name(user_id, text.strip())
        user_states[user_id] = 'waiting_phone'
        self.send_message(user_id, self.get_text(user_id, 'enter_phone'))
    
    def handle_phone(self, user_id, text):
        phone = text.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        if len(phone) < 7:
            self.send_message(user_id, self.get_text(user_id, 'invalid_phone'))
            return
        
        self.db.update_phone(user_id, phone)
        user_states[user_id] = 'registered'
        
        user_data = self.db.get_user_data(user_id)
        first_name = user_data[0] if user_data else "User"
        
        self.send_message(
            user_id,
            self.get_text(user_id, 'registration_complete', name=first_name),
            get_main_keyboard(self.db.get_language(user_id))
        )
    
    def show_points(self, user_id):
        points = self.db.get_points(user_id)
        self.send_message(
            user_id,
            self.get_text(user_id, 'your_points', points=points),
            get_main_keyboard(self.db.get_language(user_id))
        )
    
    def show_games_menu(self, user_id):
        games = self.db.get_active_games()
        if not games:
            self.send_message(user_id, "🚫 Нет доступных игр")
            return
        
        user_states[user_id] = 'games_menu'
        lang = self.db.get_language(user_id)
        
        self.send_message(
            user_id,
            self.get_text(user_id, 'choose_game'),
            get_games_keyboard(games, lang)
        )
    
    def handle_game_selection(self, user_id, text):
        game_name = text.split(' ', 1)[1] if ' ' in text else text
        
        game_map = {
            'DDoS-Jump': 'ddos_jump',
            'DDoS-Bird': 'ddos_bird',
            'DDoS-Ninja': 'ddos_ninja',
            'DDoS-Fishing': 'ddos_fishing',
            'DDoS-Blust': 'ddos_blust'
        }
        
        game_id = game_map.get(game_name)
        if not game_id:
            self.send_message(user_id, self.get_text(user_id, 'game_not_found'))
            return
        
        lang = self.db.get_language(user_id)
        self.send_message(user_id, self.get_text(user_id, 'game_loading'))
        
        game_url = self.game_manager.start_game_server(game_id)
        
        if game_url:
            if self.is_admin(user_id):
                self.game_manager.open_game_in_browser(game_id)
            
            games = self.db.get_active_games()
            self.send_message(
                user_id,
                self.get_text(user_id, 'game_selected', game=game_name, link=game_url),
                get_games_keyboard(games, lang)
            )
        else:
            self.send_message(
                user_id,
                self.get_text(user_id, 'game_not_found'),
                get_main_keyboard(lang)
            )
    
    # ============ АДМИН ПАНЕЛЬ ============
    def show_admin_panel(self, user_id):
        user_states[user_id] = 'admin_panel'
        self.send_message(
            user_id,
            "👑 Админ-панель\n\nВыберите действие:",
            get_admin_keyboard()
        )
    
    def show_leaderboard(self, user_id):
        leaders = self.db.get_leaderboard(10)
        if not leaders:
            self.send_message(user_id, "📊 Пока нет зарегистрированных пользователей", get_admin_keyboard())
            return
        
        text = "🏆 Таблица лидеров:\n\n"
        for i, (first_name, last_name, points) in enumerate(leaders, 1):
            name = f"{first_name} {last_name}" if first_name and last_name else "Unknown"
            text += f"{i}. {name} — {points} очков\n"
        
        self.send_message(user_id, text, get_admin_keyboard())
    
    def show_admin_games(self, user_id):
        user_states[user_id] = 'admin_select_game'
        games = self.db.get_all_games()
        self.send_message(
            user_id,
            "🎮 Выберите игру для управления:",
            get_admin_games_keyboard(games)
        )
    
    def toggle_game_admin(self, user_id, text):
        game_name = text.replace("✅ ", "").replace("❌ ", "").strip()
        
        games = self.db.get_all_games()
        game_id = None
        for g_id, name, is_active in games:
            if name == game_name:
                game_id = g_id
                break
        
        if game_id:
            self.db.toggle_game(game_id)
            self.send_message(user_id, f"✅ Статус игры '{game_name}' изменён", get_admin_keyboard())
            user_states[user_id] = 'admin_panel'
        else:
            self.send_message(user_id, "❌ Игра не найдена", get_admin_keyboard())
    
    # ============ ГЛАВНЫЙ ЦИКЛ С ОБРАБОТКОЙ ОШИБОК ============
    def run(self):
        print(f"🔍 Проверка админа:")
        print(f"   - self.admin_id: {self.admin_id} (тип: {type(self.admin_id)})")
        print(f"   - ADMIN_ID из env: {ADMIN_ID} (тип: {type(ADMIN_ID)})")
        print("⏳ Ожидание сообщений...")
        print("⚠️ Для остановки бота нажми Ctrl+C")
        
        reconnect_delay = 5  # Начальная задержка переподключения
        
        while True:
            try:
                for event in self.longpoll.listen():
                    # Сброс задержки при успешном соединении
                    reconnect_delay = 5
                    
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        user_id = event.user_id
                        text = event.text.strip()
                        
                        # Проверка на админа
                        if self.is_admin(user_id):
                            if text.lower() == "/admin":
                                self.show_admin_panel(user_id)
                                continue
                        
                        # Команда /start
                        if text.lower() == "/start":
                            self.handle_start(user_id)
                            continue
                        
                        current_state = user_states.get(user_id, 'new')
                        
                        # === АДМИНСКИЕ СОСТОЯНИЯ ===
                        if current_state == 'admin_panel':
                            if text == "📊 Таблица лидеров":
                                self.show_leaderboard(user_id)
                            elif text == "🎮 Выбрать игру":
                                self.show_admin_games(user_id)
                            elif text == "⚙️ Вкл/Выкл игру":
                                self.show_admin_games(user_id)
                                user_states[user_id] = 'admin_toggle_game'
                            elif text == "🔙 Выйти из админки":
                                user_states[user_id] = 'registered'
                                self.send_message(user_id, "🔙 Выход из админки", get_main_keyboard(self.db.get_language(user_id)))
                            else:
                                self.send_message(user_id, "Выберите действие:", get_admin_keyboard())
                        
                        elif current_state == 'admin_select_game':
                            if text == "🔙 Назад":
                                self.show_admin_panel(user_id)
                            else:
                                self.toggle_game_admin(user_id, text)
                        
                        elif current_state == 'admin_toggle_game':
                            if text == "🔙 Назад":
                                self.show_admin_panel(user_id)
                            else:
                                self.toggle_game_admin(user_id, text)
                                user_states[user_id] = 'admin_panel'
                        
                        # === ПОЛЬЗОВАТЕЛЬСКИЕ СОСТОЯНИЯ ===
                        elif current_state == 'select_language':
                            self.handle_language_selection(user_id, text)
                        
                        elif current_state == 'register':
                            if text.lower() in [self.get_text(user_id, 'register_btn').lower(), "📝 зарегистрироваться", "📝 register", "📝 registrarse", "📝 注册"]:
                                self.handle_register_start(user_id)
                            else:
                                self.send_message(user_id, self.get_text(user_id, 'choose_language'), get_register_keyboard(self.db.get_language(user_id)))
                        
                        elif current_state == 'waiting_first_name':
                            self.handle_first_name(user_id, text)
                        
                        elif current_state == 'waiting_last_name':
                            self.handle_last_name(user_id, text)
                        
                        elif current_state == 'waiting_phone':
                            self.handle_phone(user_id, text)
                        
                        elif current_state == 'registered':
                            if text == self.get_text(user_id, 'my_points'):
                                self.show_points(user_id)
                            elif text == self.get_text(user_id, 'games_list'):
                                self.show_games_menu(user_id)
                            else:
                                self.send_message(user_id, self.get_text(user_id, 'use_buttons'), get_main_keyboard(self.db.get_language(user_id)))
                        
                        elif current_state == 'games_menu':
                            if text == self.get_text(user_id, 'back'):
                                user_states[user_id] = 'registered'
                                self.send_message(user_id, self.get_text(user_id, 'use_buttons'), get_main_keyboard(self.db.get_language(user_id)))
                            elif any(game in text for game in ['DDoS-Jump', 'DDoS-Bird', 'DDoS-Ninja', 'DDoS-Fishing', 'DDoS-Blust']):
                                self.handle_game_selection(user_id, text)
                            else:
                                self.show_games_menu(user_id)
                        
                        else:
                            if self.db.user_exists(user_id):
                                user_states[user_id] = 'registered'
                                self.send_message(user_id, self.get_text(user_id, 'use_buttons'), get_main_keyboard(self.db.get_language(user_id)))
                            else:
                                self.send_message(user_id, self.get_text(user_id, 'start_command'))
                            
            except KeyboardInterrupt:
                print("\n\n👋 Бот остановлен пользователем (Ctrl+C)")
                print("💾 Все данные сохранены")
                break  # Корректный выход из цикла
                
            except Exception as e:
                print(f"\n⚠️ Ошибка соединения: {e}")
                print(f"🔄 Переподключение через {reconnect_delay} секунд...")
                
                # Увеличиваем задержку при повторных ошибках (максимум 60 сек)
                reconnect_delay = min(reconnect_delay * 2, 60)
                
                time.sleep(reconnect_delay)
                continue  # Перезапускаем цикл

# ============ ЗАПУСК ============
if __name__ == "__main__":
    print(f"🔑 Токен: {VK_TOKEN[:25]}...")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print("🤖 Запуск бота...")
    
    try:
        bot = VKBot(VK_TOKEN, ADMIN_ID)
        bot.run()
    except KeyboardInterrupt:
        print("\n\n👋 Бот остановлен")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nНажми Enter для закрытия...")