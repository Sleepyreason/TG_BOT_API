import requests
import os
import time
import threading

# === НАСТРОЙКИ ===
YOUTUBE_API_KEY = 'Ключ ютаба'
YOUTUBE_CHANNEL_ID = 'ID канала'
TWITCH_CLIENT_ID = 'ID твича'
TWITCH_CLIENT_SECRET = 'Секретный код твича'
TWITCH_USER_LOGIN = 'Логин твича'
TELEGRAM_BOT_TOKEN = 'Бот токен'
TELEGRAM_CHAT_ID = 'Телеграм канал'
LAST_VIDEO_FILE = 'last_video.txt'

# === TELEGRAM ===
def send_telegram_message(text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': text, 'parse_mode': 'HTML'}
    r = requests.post(url, data=payload)
    print("Ответ от Telegram:", r.status_code, r.text)

# === YOUTUBE ===
def get_latest_video():
    try:
        url = f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}&channelId={YOUTUBE_CHANNEL_ID}&part=snippet,id&order=date&maxResults=1"
        r = requests.get(url)
        data = r.json()
        print("Ответ от YouTube API:", data)
        video = data['items'][0]
        video_id = video['id']['videoId']
        title = video['snippet']['title']
        link = f"https://www.youtube.com/watch?v={video_id}"
        return video_id, title, link
    except Exception as e:
        print("Ошибка при получении видео:", e)
        return None, None, None

def read_last_video_id():
    if os.path.exists(LAST_VIDEO_FILE):
        with open(LAST_VIDEO_FILE, 'r') as f:
            return f.read().strip()
    return None

def save_last_video_id(video_id):
    with open(LAST_VIDEO_FILE, 'w') as f:
        f.write(video_id)

def youtube_check_loop():
    while True:
        print("🔍 Проверка YouTube...")
        last_video_id = read_last_video_id()
        video_id, title, link = get_latest_video()
        if video_id and video_id != last_video_id:
            print("🆕 Новое видео найдено!")
            message = (
                "🔥 Вышло новое видео на канале!\n\n"
                f"<b>{title}</b>\n{link}\n\n"
                "👉 Поддержи лайком и комментом!"
            )
            send_telegram_message(message)
            save_last_video_id(video_id)
        time.sleep(60)  # Проверка каждые 60 минут

# === TWITCH ===
def get_twitch_access_token():
    try:
        url = 'https://id.twitch.tv/oauth2/token'
        params = {
            'client_id': TWITCH_CLIENT_ID,
            'client_secret': TWITCH_CLIENT_SECRET,
            'grant_type': 'client_credentials'
        }
        r = requests.post(url, params=params)
        return r.json().get('access_token')
    except Exception as e:
        print("Ошибка получения токена Twitch:", e)
        return None

def is_stream_live(token):
    try:
        url = 'https://api.twitch.tv/helix/streams'
        headers = {
            'Client-ID': TWITCH_CLIENT_ID,
            'Authorization': f'Bearer {token}'
        }
        params = {'user_login': TWITCH_USER_LOGIN}
        r = requests.get(url, headers=headers, params=params)
        data = r.json()
        print("Ответ от Twitch API:", data)
        return bool(data.get('data'))
    except Exception as e:
        print("Ошибка Twitch:", e)
        return False

def twitch_check_loop():
    was_live = False
    token = get_twitch_access_token()
    while True:
        if not token:
            token = get_twitch_access_token()

        if token:
            try:
                if is_stream_live(token):
                    if not was_live:
                        was_live = True
                        message = (
                            "🔴 Прямо сейчас идёт стрим на <b>Twitch</b>!\n\n"
                            "👉 Заходи: https://www.twitch.tv/sleepyreason"
                        )
                        send_telegram_message(message)
                else:
                    if was_live:
                        print("📴 Стрим завершён.")
                    was_live = False
            except Exception as e:
                print("Ошибка при проверке Twitch:", e)
        time.sleep(60)  # Проверка каждую минуту

# === MAIN ===
def main():
    print("✅ Бот запущен!")
    yt_thread = threading.Thread(target=youtube_check_loop, daemon=True)
    twitch_thread = threading.Thread(target=twitch_check_loop, daemon=True)

    yt_thread.start()
    twitch_thread.start()

    yt_thread.join()
    twitch_thread.join()

if __name__ == '__main__':
    main()
