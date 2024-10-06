import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

# Ініціалізуємо Faker
fake = Faker()

# Функція для генерації випадкових дат
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

# Категорії відео
CATEGORIES = ["Music", "Sports", "Entertainment", "News", "Gaming", "Education"]

# 1. Users
def generate_users(n=10_000):
    user_ids = list(range(10000, 10000 + n))  # Гарантуємо унікальні user_id
    users_data = []
    for user_id in user_ids:
        user = {
            "user_id": user_id,  # Унікальні user_id
            "username": fake.user_name(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "language_code": fake.language_code(),
            "created_at": fake.date_time_between(start_date="-1y", end_date="now")
        }
        users_data.append(user)
    users_df = pd.DataFrame(users_data)
    users_df.to_csv("data_fake/users.csv", index=False)
    return users_df

# 2. Videos
def generate_videos(n=15_000):
    videos_data = []
    for _ in range(n):
        video = {
            "video_id": fake.uuid4(),  # Ідентифікатор відео
            "title": fake.sentence(nb_words=6),
            "description": fake.text(max_nb_chars=300),
            "channel_id": fake.uuid4(),
            "channel_title": fake.company(),
            "category": random.choice(CATEGORIES),  # Випадкова категорія відео
            "published_at": random_date(datetime(2019, 1, 1), datetime.now()),
            "views_count": fake.random_int(min=1000, max=1000000),
            "likes_count": fake.random_int(min=100, max=50000),
            "comments_count": fake.random_int(min=0, max=1000)
        }
        videos_data.append(video)
    videos_df = pd.DataFrame(videos_data)
    videos_df.to_csv("data_fake/videos.csv", index=False)
    return videos_df

# 3. YouTubeRequests
def generate_youtube_requests(users_df, videos_df, n=20_000):
    youtube_requests_data = []
    for _ in range(n):
        user_id = random.choice(users_df["user_id"])
        video = videos_df.sample(1).iloc[0]  # Випадковий відео з таблиці videos
        action_time = fake.date_time_between(start_date="-1y", end_date="now")
        response_time = fake.date_time_between(start_date=action_time, end_date=action_time + timedelta(seconds=random.randint(0, 60*60)))
        request = {
            "request_id": fake.random_int(min=10000, max=99999),
            "user_id": user_id,
            "query": fake.sentence(nb_words=4),
            "video_id": video["video_id"],  # Підв'язуємо до існуючого відео
            "video_title": video["title"],
            "video_url": f"https://www.youtube.com/watch?v={video['video_id']}",
            "response_time": response_time,
            "action": random.choice(["search", "view", "like", "share"]),  # Дія користувача
            "action_time": action_time,  # Час дії
            "summary": fake.text(max_nb_chars=200)  # Результат саммарі
        }
        youtube_requests_data.append(request)
    youtube_requests_df = pd.DataFrame(youtube_requests_data)
    youtube_requests_df.to_csv("data_fake/youtube_requests.csv", index=False)
    return youtube_requests_df

# Генерація та збереження CSV файлів
users_df = generate_users(n=10_000)
videos_df = generate_videos(n=15_000)
youtube_requests_df = generate_youtube_requests(users_df, videos_df, n=20_000)

print("CSV файли згенеровані!")
