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

    # 장르가 결측치/기타 타입일 수 있으므로 문자열 변환 후 처리
    # 세로막대(|) 기호로 여러 개 적힌 장르는 첫 번째 장르만 extraction
    df["genre"] = df["genre"].astype(str).str.split("|").str[0]
    return df


df = load_data()

# ---------------------------------------------------------
# 첫 번째 구역: 장르별 영화 편수 도넛 그래프
# ---------------------------------------------------------
st.subheader("1. 장르별 영화 편수 분포")

# 장르별 영화 편수 집계
genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["장르", "영화 편수"]

# 플롯리 도넛 그래프 생성
fig1 = px.pie(
    genre_counts,
    values="영화 편수",
    names="장르",
    hole=0.4,
    title="장르별 영화 편수 비율",
)

# 마우스오버 시 편수와 비율이 보이도록 설정
fig1.update_traces(
    hoverinfo="label+value+percent", textinfo="percent+label", hole=0.4
)

st.plotly_chart(fig1, use_container_width=True)

# 그래프 설명 구역
st.markdown("---")
st.markdown(
    "**이 그래프로 알 수 있는 것:** 특정 장르에 박스오피스 흥행작이 집중되어 있는지, 전체적인 장르 분포 흐름을 한눈에 파악할 수 있습니다."
)

st.markdown("<br><br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 두 번째 구역: 장르 및 영화별 총 관객 수 트리맵 그래프
# ---------------------------------------------------------
st.subheader("2. 장르 및 영화별 총 관객 수 트리맵")

# 플롯리 트리맵 그래프 생성 (계층: 장르 -> 영화명, 크기: 총 관객 수)
fig2 = px.treemap(
    df,
    path=[px.Constant("전체"), "genre", "movieNm"],
    values="total_audi",
    title="장르 및 영화별 총 관객 수 분포",
    hover_data={"total_audi": ":,d"},
)

# 마우스오버 시 영화명과 총 관객 수가 명확히 표시되도록 설정
fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객 수: %{value:,.0f}명<extra></extra>"
)

st.plotly_chart(fig2, use_container_width=True)

# 그래프 설명 구역
st.markdown("---")
st.markdown(
    "**이 그래프로 알 수 있는 것:** 어떤 장르가 전체 총 관객 수에서 큰 비중을 차지하는지, 해당 장르 안에서 흥행을 견인한 대표 영화가 무엇인지 한눈에 비교할 수 있습니다."
)

st.markdown("<br><br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 세 번째 구역: 총 관객 수 히스토그램
# ---------------------------------------------------------
st.subheader("3. 총 관객 수 분포 히스토그램")

# 플롯리 히스토그램 생성
fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    title="총 관객 수 분포",
    labels={"total_audi": "총 관객 수"},
    hover_data=["movieNm"],
)

fig3.update_layout(yaxis_title="영화 수", bargap=0.1)

st.plotly_chart(fig3, use_container_width=True)

# 최다 관객 영화 정보 동적 추출
top_movie = df.loc[df["total_audi"].idxmax()]
top_movie_name = top_movie["movieNm"]
top_movie_audi = top_movie["total_audi"]

# 그래프 설명 구역
st.markdown("---")
st.markdown(
    f"**이 그래프로 알 수 있는 것:** 대부분의 영화는 관객 수 100만 명 미만의 하위 구간에 밀집해 있으며, 가장 많은 관객을 동원한 영화는 **'{top_movie_name}'**(약 {top_movie_audi:,.0f}명)입니다."
)
