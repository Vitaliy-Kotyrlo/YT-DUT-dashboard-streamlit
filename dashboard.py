import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    users_df = pd.read_csv("data_fake/users.csv")
    youtube_requests_df = pd.read_csv("data_fake/youtube_requests.csv")
    videos_df = pd.read_csv("data_fake/videos.csv")
    
    youtube_requests_df['response_time'] = pd.to_datetime(youtube_requests_df['response_time'])
    youtube_requests_df['action_time'] = pd.to_datetime(youtube_requests_df['action_time'])
    users_df['created_at'] = pd.to_datetime(users_df['created_at'])
    
    return users_df, youtube_requests_df, videos_df

users_df, youtube_requests_df, videos_df = load_data()

st.title("Youtube Fake Data Dashboard")

st.sidebar.header("Фільтри")
category_filter = st.sidebar.multiselect("Виберіть категорію відео", options=videos_df['category'].unique(), default=videos_df['category'].unique())
date_filter = st.sidebar.date_input("Виберіть період часу", [youtube_requests_df['response_time'].min(), youtube_requests_df['response_time'].max()])

filtered_youtube_requests = youtube_requests_df[
    (youtube_requests_df['response_time'].dt.date >= date_filter[0]) & 
    (youtube_requests_df['response_time'].dt.date <= date_filter[1])
]

filtered_users_df = users_df[
    (users_df['created_at'].dt.date >= date_filter[0]) & 
    (users_df['created_at'].dt.date <= date_filter[1])
]

filtered_videos_df = videos_df[videos_df['category'].isin(category_filter)]

filtered_youtube_requests = filtered_youtube_requests[
    filtered_youtube_requests['video_id'].isin(filtered_videos_df['video_id'])
]

# Метрики
col1, col2, col3 = st.columns(3)

# Метрика 1
last_month = datetime.now() - timedelta(days=30)
new_users_last_month = filtered_users_df[filtered_users_df['created_at'] >= last_month].shape[0]
total_unique_users = filtered_users_df['user_id'].nunique()
col1.metric(label="Кількість нових користувачів за місяць", value=new_users_last_month, delta=total_unique_users, delta_color="off")

# Метрика 2
avg_response_time = filtered_youtube_requests['response_time'] - filtered_youtube_requests['action_time']
avg_response_time_sec = avg_response_time.mean().total_seconds() / 60  # В хвилинах
long_responses_count = filtered_youtube_requests[avg_response_time > timedelta(minutes=10)].shape[0]
col2.metric(label="Середня тривалість відповіді бота (хв)", value=round(avg_response_time_sec, 2), delta=long_responses_count)

# Метрика 3
total_requests_last_month = filtered_youtube_requests[filtered_youtube_requests['response_time'] >= last_month].shape[0]
total_requests = filtered_youtube_requests.shape[0]
col3.metric(label="Загальна кількість запитів за останній місяць", value=total_requests_last_month, delta=total_requests)

# Лінійний графік
daily_requests = filtered_youtube_requests.groupby(filtered_youtube_requests['response_time'].dt.date).size().reset_index(name='request_count')
fig2 = px.line(daily_requests, x='response_time', y='request_count', title="Кількість запитів по днях")
st.plotly_chart(fig2, use_container_width=True)  # Використовуємо всю ширину

# Топ-10
top_videos = filtered_youtube_requests.groupby('video_id').size().reset_index(name='request_count')
top_videos = top_videos.merge(filtered_videos_df[['video_id', 'title', 'views_count']], on='video_id', how='left')
top_videos = top_videos.nlargest(10, 'request_count')

# Lollipop
category_requests = filtered_youtube_requests.groupby('video_id').size().reset_index(name='request_count')
category_requests = category_requests.merge(filtered_videos_df[['video_id', 'category']], on='video_id', how='left')
category_summary = category_requests.groupby('category')['request_count'].sum().reset_index()


def offset_signal(signal, marker_offset):
    if abs(signal) <= marker_offset:
        return 0
    return signal - marker_offset if signal > 0 else signal + marker_offset

def create_lollipop_chart(category_summary):
    marker_offset = 0.04
    data = [
        go.Scatter(
            y=category_summary['category'],  
            x=category_summary['request_count'],  
            mode='markers',
            marker=dict(color='red', size=10)
        )
    ]
    layout = go.Layout(
        shapes=[dict(
            type='line',
            xref='x',
            yref='y',
            x0=0,
            y0=i,
            x1=offset_signal(category_summary['request_count'].iloc[i], marker_offset),
            y1=i,
            line=dict(
                color='grey',
                width=1
            )
        ) for i in range(len(category_summary))],
        xaxis_title='Кількість запитів',
        yaxis_title='Категорія'
    )

    fig = go.Figure(data, layout)
    return fig

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Топ-10 найпопулярніших відео") 
    st.dataframe(top_videos[['title', 'views_count', 'request_count']], hide_index  = True)

with right_col:
    st.subheader("Lollipop Chart по категоріях")
    fig_lollipop = create_lollipop_chart(category_summary)
    st.plotly_chart(fig_lollipop)
