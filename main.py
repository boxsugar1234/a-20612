import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="영화 데이터 그래프 - 분포와 관계", layout="wide")

st.title("영화 데이터 그래프 - 분포와 관계")


# 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # 장르가 여덟 자리 숫자로 들어오거나 결측치일 수 있으므로 문자열 변환 후 처리
    # 세로막대(|) 기호로 여러 개 적힌 장르는 첫 번째 장르만 extraction
    df["genre"] = df["genre"].astype(str).str.split("|").str[0]
    return df


df = load_data()

# 구역 구분: 첫 그래프 (장르별 영화 편수 도넛 그래프)
st.subheader("1. 장르별 영화 편수 분포")

# 장르별 영화 편수 집계
genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["장르", "영화 편수"]

# 플롯리 도넛 그래프 생성
fig = px.pie(
    genre_counts,
    values="영화 편수",
    names="장르",
    hole=0.4,
    title="장르별 영화 편수 비율",
)

# 마우스오버 시 편수와 비율이 보이도록 설정
fig.update_traces(
    hoverinfo="label+value+percent", textinfo="percent+label", hole=0.4
)

st.plotly_chart(fig, use_container_width=True)

# 그래프 설명 구역
st.markdown("---")
st.markdown(
    "**이 그래프로 알 수 있는 것:** 특정 장르에 박스오피스 흥행작이 집중되어 있는지, 전체적인 장르 분포 흐름을 한눈에 파악할 수 있습니다."
)
