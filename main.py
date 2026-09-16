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
    # 세로막대(|) 기호로 여러 개 적힌 장르는 첫 번째 장르만 추출
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

st.markdown("<br><br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 네 번째 구역: 개봉일 스크린 수 vs 총 관객 수 산점도
# ---------------------------------------------------------
st.subheader("4. 개봉일 스크린 수와 총 관객 수의 관계")

# 플롯리 산점도 생성
fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린 수 대비 총 관객 수 분포",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객 수",
        "genre": "장르",
    },
    hover_data={"first_scrn": ":,d", "total_audi": ":,d"},
)

fig4.update_traces(marker=dict(size=9, opacity=0.8))

st.plotly_chart(fig4, use_container_width=True)

# 그래프 설명 구역
st.markdown("---")
st.markdown(
    "**이 그래프로 알 수 있는 것:** 개봉일 스크린 수가 많을수록 대체로 총 관객 수도 증가하는 양의 상관관계를 보이며, 장르별 선점 스크린 규모와 최종 흥행 성과 간의 관계를 확인할 수 있습니다."
)

st.markdown("<br><br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 다섯 번째 구역: 영화 10편 이상 장르별 총 관객 수 박스플롯
# ---------------------------------------------------------
st.subheader("5. 주요 장르별 총 관객 수 분포 (10편 이상 장르)")

# 영화가 10편 이상인 장르 필터링
genre_counts_series = df["genre"].value_counts()
top_genres = genre_counts_series[genre_counts_series >= 10].index
df_filtered = df[df["genre"].isin(top_genres)]

# 플롯리 박스플롯 생성
fig5 = px.box(
    df_filtered,
    x="genre",
    y="total_audi",
    color="genre",
    points="outliers",  # 이상치를 점으로 표현
    hover_name="movieNm",  # 점에 마우스를 올릴 때 영화명 표시
    title="10편 이상 개봉한 주요 장르별 관객 수 분포",
    labels={"genre": "장르", "total_audi": "총 관객 수"},
    hover_data={"total_audi": ":,d"},
)

st.plotly_chart(fig5, use_container_width=True)

# 그래프 설명 구역
st.markdown("---")
st.markdown(
    "**이 그래프로 알 수 있는 것:** 주요 장르별 관객 수의 중앙값과 범위를 비교할 수 있으며, 이상치(Outlier) 점을 통해 해당 장르 내에서 대흥행을 이끌어낸 극소수의 '대박' 작품들을 한눈에 확인할 수 있습니다."
)

st.markdown("<br><br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 여섯 번째 구역: 개봉일 스크린 수 vs 총 관객 수 버블 차트 (첫 주 관객 수 = 크기)
# ---------------------------------------------------------
st.subheader("6. 개봉일 스크린 수, 총 관객 수 및 첫 주 관객 수의 버블 차트")

# 플롯리 버블 차트 생성
fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    size_max=40,  # 버블 최대 크기 지정
    title="개봉일 스크린 수 vs 총 관객 수 (버블 크기: 첫 주 관객 수)",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객 수",
        "first_week_audi": "첫 주 관객 수",
        "genre": "장르",
    },
    hover_data={
        "first_scrn": ":,d",
        "total_audi": ":,d",
        "first_week_audi": ":,d",
    },
)

st.plotly_chart(fig6, use_container_width=True)

# 그래프 설명 구역
st.markdown("---")
st.markdown(
    "**이 그래프로 알 수 있는 것:** 개봉일 스크린 수와 최종 관객 수 외에도, 버블 크기를 통해 '개봉 첫 주 초반 흥행 동력(첫 주 관객 수)'이 최종 성과 및 스크린 확보에 미친 선순환 관계를 입체적으로 확인할 수 있습니다."
)

st.markdown("<br><br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 일곱 번째 구역: 국가별-장르별 영화 편수 선버스트 차트
# ---------------------------------------------------------
st.subheader("7. 제작 국가 및 장르별 영화 편수 분포 (선버스트)")

# 국가 및 장르별 영화 편수 집계 Dataframe 생성
sunburst_df = df.groupby(["nation", "genre"]).size().reset_index(name="count")

# 플롯리 선버스트 차트 생성
fig7 = px.sunburst(
    sunburst_df,
    path=["nation", "genre"],
    values="count",
    title="제작 국가 → 장르별 영화 편수 계층 구조",
    color="nation",
)

fig7.update_traces(
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<extra></extra>"
)

st.plotly_chart(fig7, use_container_width=True)

# 그래프 설명 구역
st.markdown("---")
st.markdown(
    "**이 그래프로 알 수 있는 것:** 제작 국가별 전체 점유율과 함께, 각 국가 내에서 어떤 장르의 영화가 주로 개봉했는지 계층적 비중을 다차원적으로 파악할 수 있습니다."
)
