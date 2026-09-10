import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="영화 박스오피스 분석 앱", layout="wide")

# App 제목
st.title("🎬 영화 박스오피스 데이터 분석")


# [1. 데이터 불러오기]
# @st.cache_data 데코레이터를 사용하여 매번 불러오지 않고 캐싱 처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # [2. 날짜 전처리]
    # 결측치가 하나라도 있는 행 삭제
    df = df.dropna()

    # '기준일자' 컬럼을 datetime 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"])

    # 기준일자 오름차순으로 데이터 정렬
    df = df.sort_values(by="기준일자", ascending=True)

    return df


# 데이터 로드
data = load_data()


# [3. 영화 선택 기능]
# 사이드바 영역에 영화 선택 UI 구성
st.sidebar.header("🔍 옵션 선택")

# 누적관객수 최대값 기준으로 전체 영화명 정렬 (중복 제거)
movie_rank = (
    data.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 사이드바 드롭다운(Selectbox)에서 영화 선택 (탭 1, 2에서 사용)
selected_movie = st.sidebar.selectbox("영화 이름을 선택하세요:", movie_rank)

# 선택된 단일 영화 데이터 필터링
filtered_df = data[data["영화명"] == selected_movie]


# [5. 구역 나누기]
# 분석 주제별로 탭(Tab) 구역 생성
tab1, tab2, tab3 = st.tabs(
    [
        "📈 개별 영화 일별 관객수",
        "📊 개별 영화 누적 관객수",
        "🏆 TOP 5 영화 누적 관객수 비교 (20일 이상 유지)",
    ]
)


# [첫 번째 탭: 개별 영화 일별 관객수 선그래프]
with tab1:
    st.subheader(f"'{selected_movie}' 일별 관객수 변화")

    fig1 = px.line(
        filtered_df,
        x="기준일자",
        y="해당일관객수",
        title=f"'{selected_movie}' 기준일자별 해당일 관객수 추이",
        markers=True,
    )

    fig1.update_layout(
        xaxis_title="기준일자",
        yaxis_title="해당일 관객수 (명)",
        hovermode="x unified",
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 개봉 후 날짜별 관객수 증감 추이와 최고 관객수를 기록한 시점을 확인할 수 있습니다."
    )


# [두 번째 탭: 개별 영화 누적 관객수 영역차트]
with tab2:
    st.subheader(f"'{selected_movie}' 누적 관객수 변화")

    fig2 = px.area(
        filtered_df,
        x="기준일자",
        y="누적관객수",
        title=f"'{selected_movie}' 기준일자별 누적 관객수 추이",
    )

    fig2.update_layout(
        xaxis_title="기준일자",
        yaxis_title="누적 관객수 (명)",
        hovermode="x unified",
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 시간이 지남에 따른 총 관객 수의 누적 성장 곡선과 관객 수가 가파르게 증가한 구간을 한눈에 볼 수 있습니다."
    )


# [세 번째 탭: 조건을 만족하는 TOP 5 영화 누적 관객수 비교 다중 선그래프]
with tab3:
    st.subheader("🏆 long-run TOP 5 영화 누적 관객수 비교 (TOP10 차트 20일 이상 유지)")

    # 1. 영화별 등장 일수(데이터에 등장한 횟수) 계산
    movie_days = data.groupby("영화명")["기준일자"].count()

    # 2. 등장 일수가 20일 이상인 영화만 필터링
    filtered_movies_20days = movie_days[movie_days >= 20].index

    # 3. 20일 이상 등장한 영화들 중에서 누적관객수 상위 5개 영화 선택
    top5_movies = (
        data[data["영화명"].isin(filtered_movies_20days)]
        .groupby("영화명")["누적관객수"]
        .max()
        .sort_values(ascending=False)
        .head(5)
        .index.tolist()
    )

    # 4. 최종 선택된 TOP 5 영화의 전체 데이터 필터링
    top5_df = data[data["영화명"].isin(top5_movies)]

    # 5. Plotly 다중 선그래프 생성
    fig3 = px.line(
        top5_df,
        x="기준일자",
        y="누적관객수",
        color="영화명",  # 영화별로 선 색상 구분 및 범례 표시
        title="20일 이상 차트 유지 영화 중 TOP 5의 누적 관객수 추이 비교",
        markers=False,
    )

    fig3.update_layout(
        xaxis_title="기준일자",
        yaxis_title="누적 관객수 (명)",
        hovermode="x unified",
        legend_title_text="영화명",
    )

    st.plotly_chart(fig3, use_container_width=True)

    # 그래프 하단 설명 문구
    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** TOP10 차트에 20일 이상 장기 집계된 주요 흥행작({', '.join(top5_movies)})의 누적 관객수 증가 추이와 꾸준한 흥행력을 비교해볼 수 있습니다."
    )
