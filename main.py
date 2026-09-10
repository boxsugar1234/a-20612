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

# 누적관객수 최대값 기준으로 영화명 정렬 (중복 제거)
movie_rank = (
    data.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 사이드바 드롭다운(Selectbox)에서 영화 선택
selected_movie = st.sidebar.selectbox("영화 이름을 선택하세요:", movie_rank)

# 선택된 영화 데이터만 필터링 (두 그래프 공통 사용)
filtered_df = data[data["영화명"] == selected_movie]


# [5. 구역 나누기]
# 분석 주제별로 탭(Tab) 구역 생성
tab1, tab2 = st.tabs(["📈 일별 관객수 추이", "📊 누적 관객수 추이 (영역차트)"])


# [첫 번째 탭: 일별 관객수 선그래프]
with tab1:
    st.subheader(f"'{selected_movie}' 일별 관객수 변화")

    # Plotly Express를 활용한 Line Chart 생성
    fig1 = px.line(
        filtered_df,
        x="기준일자",
        y="해당일관객수",
        title=f"'{selected_movie}' 기준일자별 해당일 관객수 추이",
        markers=True,  # 데이터 포인트 마커 표시
    )

    # 그래프 레이아웃 커스텀
    fig1.update_layout(
        xaxis_title="기준일자",
        yaxis_title="해당일 관객수 (명)",
        hovermode="x unified",  # 마우스 호버 시 정보 한눈에 보기
    )

    # Streamlit 화면에 Plotly 그래프 출력
    st.plotly_chart(fig1, use_container_width=True)

    # 그래프 하단 설명 문구 공간
    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 개봉 후 날짜별 관객수 증감 추이와 최고 관객수를 기록한 시점을 확인할 수 있습니다."
    )


# [두 번째 탭: 누적 관객수 영역차트]
with tab2:
    st.subheader(f"'{selected_movie}' 누적 관객수 변화")

    # Plotly Express를 활용한 Area Chart 생성
    fig2 = px.area(
        filtered_df,
        x="기준일자",
        y="누적관객수",
        title=f"'{selected_movie}' 기준일자별 누적 관객수 추이",
    )

    # 그래프 레이아웃 커스텀
    fig2.update_layout(
        xaxis_title="기준일자",
        yaxis_title="누적 관객수 (명)",
        hovermode="x unified",
    )

    # Streamlit 화면에 Plotly 그래프 출력
    st.plotly_chart(fig2, use_container_width=True)

    # 그래프 하단 설명 문구 공간
    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 시간이 지남에 따른 총 관객 수의 누적 성장 곡선과 관객 수가 가파르게 증가한 구간을 한눈에 볼 수 있습니다."
    )
