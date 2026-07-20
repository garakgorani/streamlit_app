import streamlit as st
import googleapiclient.discovery
import re
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter

# 한글 폰트 설정 (Streamlit Cloud 환경 고려)
# 리눅스 기반 환경에서 기본 제공되는 나눔 또는 기타 한글 폰트가 없을 경우를 대비해 
# 시스템 폰트 경로를 유연하게 잡거나 기본 폰트를 사용합니다.
import matplotlib
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['axes.unicode_minus'] = False

# 1. 유튜브 영상 ID 추출 함수
def get_video_id(url):
    regex = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/(watch\?v=)?([^?&\n]+)'
    match = re.search(regex, url)
    if match:
        return match.group(5)
    return None

# 2. 유튜브 댓글 수집 함수
def get_youtube_comments(api_key, video_id, max_count):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    comments = []
    next_page_token = None
    
    while len(comments) < max_count:
        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(100, max_count - len(comments)),
                pageToken=next_page_token,
                textFormat="plainText"
            )
            response = request.execute()
            
            for item in response.get('items', []):
                snippet = item['snippet']['topLevelComment']['snippet']
                text = snippet['textDisplay']
                published_at = snippet['publishedAt']
                like_count = snippet['likeCount']
                comments.append({
                    'text': text,
                    'published_at': pd.to_datetime(published_at),
                    'likes': like_count
                })
                
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        except Exception as e:
            st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
            break
            
    return pd.DataFrame(comments)

# 3. 간단한 텍스트 기반 감성 분석 (반응도 체크용 자작 사전)
def analyze_sentiment(text):
    # 실제 자연어 처리 모델 대신 가벼운 키워드 매칭 방식을 사용합니다.
    pos_words = ['좋다', '좋아', '최고', '대박', '유익', '재밌', '감사', '짱', '추천', '굳', 'good', 'love']
    neg_words = ['별로', '실망', '노잼', '최악', '아쉽', '불편', '나쁨', '지루', '싫어']
    
    pos_score = sum(1 for word in pos_words if word in text.lower())
    neg_score = sum(1 for word in neg_words if word in text.lower())
    
    if pos_score > neg_score:
        return '긍정'
    elif neg_score > pos_score:
        return '부정'
    else:
        return '중립'

# --- 스트림릿 UI 레이아웃 ---
st.set_page_config(page_title="유튜브 댓글 분석기", layout="wide")
st.title("📊 유튜브 댓글 분석기")
st.caption("유튜브 영상의 댓글을 수집하여 시간별 추이, 반응도, 워드클라우드를 분석합니다.")

# 사이드바 설정
st.sidebar.header("⚙️ 설정")
api_key = st.sidebar.text_input("YouTube API Key 입력", type="password")
video_url = st.sidebar.text_input("유튜브 영상 링크 입력", placeholder="https://www.youtube.com/watch?v=...")
max_comments = st.sidebar.slider("분석할 댓글 개수 설정", min_value=10, max_value=500, value=100, step=10)

if st.sidebar.button("분석 시작"):
    if not api_key:
        st.warning("YouTube API Key를 입력해주세요.")
    elif not video_url:
        st.warning("유튜브 영상 링크를 입력해주세요.")
    else:
        video_id = get_video_id(video_url)
        
        if not video_id:
            st.error("올바른 유튜브 링크 형식이 아닙니다.")
        else:
            # 메인 화면 영역 분할
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📺 선택한 영상")
                st.video(video_url)
                
            with col2:
                with st.spinner("댓글 수집 및 분석 중..."):
                    df = get_youtube_comments(api_key, video_id, max_comments)
                    
                if df.empty:
                    st.warning("수집된 댓글이 없거나 API Key를 확인해주세요.")
                else:
                    st.subheader("📈 분석 결과 요약")
                    st.success(f"총 {len(df)}개의 댓글을 성공적으로 분석했습니다.")
                    
                    # 1. 시간대별 댓글 작성 추이
                    st.write("#### 🕒 시간대별 댓글 작성 추이")
                    df['date_hour'] = df['published_at'].dt.to_period('H').dt.to_timestamp()
                    timeline = df.groupby('date_hour').size().reset_index(name='댓글 수')
                    st.line_chart(timeline.set_index('date_hour'))
                    
                    # 2. 댓글 반응도 (감성 분석)
                    st.write("#### 🎭 댓글 반응도 (긍정 / 중립 / 부정)")
                    df['sentiment'] = df['text'].apply(analyze_sentiment)
                    sentiment_counts = df['sentiment'].value_counts()
                    st.bar_chart(sentiment_counts)
                    
                    # 3. 한글 워드클라우드
                    st.write("#### ☁️ 한글 워드클라우드")
                    
                    # 한글 단어 추출 (정규표현식 사용, 2글자 이상 변환)
                    korean_text = " ".join(df['text'].tolist())
                    words = re.findall(r'[가-힣]{2,}', korean_text)
                    
                    # 불용어(의미 없는 단어) 필터링 예시
                    stopwords = ['진짜', '너무', '정말', '보고', '영상', '확인', '이거', '그냥', '보면']
                    filtered_words = [word for word in words if word not in stopwords]
                    
                    if filtered_words:
                        word_counts = Counter(filtered_words)
                        
                        # 워드클라우드 생성 (폰트 경로 생략 시 시스템 기본 폰트 사용)
                        wc = WordCloud(
                            background_color="white",
                            width=800,
                            height=400,
                            font_path=None  # 리눅스 환경 대응을 위해 None 혹은 설치된 폰트 지정 가능
                        ).generate_from_frequencies(word_counts)
                        
                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.imshow(wc, interpolation='bilinear')
                        ax.axis('off')
                        st.pyplot(fig)
                    else:
                        st.info("워드클라우드를 생성할 만큼 충분한 한글 단어가 없습니다.")
