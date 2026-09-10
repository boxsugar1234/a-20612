import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📈 개별 영화 일별 관객수",
        "📊 개별 영화 누적 관객수",
        "🏆 TOP 5 영화 누적 관객수 비교",
        "📉 전체 시장 일별 관객수 및 7일 이동평균",
        "📊 월별 총 관객수 비교",
        "🗓️ 캘린더 히트맵 (요일/월별)",
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


# [세 번째 탭: TOP 5 영화 누적 관객수 비교]
with tab3:
    st.subheader("🏆 long-run TOP 5 영화 누적 관객수 비교 (TOP10 차트 20일 이상 유지)")

    # 등장 일수가 20일 이상인 영화 필터링
    movie_days = data.groupby("영화명")["기준일자"].count()
    filtered_movies_20days = movie_days[movie_days >= 20].index

    # 20일 이상 등장한 영화 중 누적관객수 상위 5개 선택
    top5_movies = (
        data[data["영화명"].isin(filtered_movies_20days)]
        .groupby("영화명")["누적관객수"]
        .max()
        .sort_values(ascending=False)
        .head(5)
        .index.tolist()
    )

    top5_df = data[data["영화명"].isin(top5_movies)]

    fig3 = px.line(
        top5_df,
        x="기준일자",
        y="누적관객수",
        color="영화명",
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

    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** TOP10 차트에 20일 이상 장기 집계된 주요 흥행작({', '.join(top5_movies)})의 누적 관객수 증가 추이와 꾸준한 흥행력을 비교해볼 수 있습니다."
    )


# [네 번째 탭: 전체 시장 일별 관객수 및 7일 이동평균]
with tab4:
    st.subheader("📉 전체 박스오피스 일별 관객수 및 7일 이동평균 추이")

    # 1. 기준일자별 TOP10 영화의 해당일관객수 총합 계산
    daily_market = (
        data.groupby("기준일자")["해당일관객수"].sum().reset_index()
    )

    # 2. 7일 이동평균(Moving Average) 계산
    daily_market["7일_이동평균"] = (
        daily_market["해당일관객수"].rolling(window=7).mean()
    )

    # 3. Plotly Graph Objects를 사용한 시각화
    fig4 = go.Figure()

    fig4.add_trace(
        go.Scatter(
            x=daily_market["기준일자"],
            y=daily_market["해당일관객수"],
            mode="lines",
            name="일별 총 관객수 (일간)",
            line=dict(color="rgba(150, 150, 150, 0.4)", width=1.5),
        )
    )

    fig4.add_trace(
        go.Scatter(
            x=daily_market["기준일자"],
            y=daily_market["7일_이동평균"],
            mode="lines",
            name="7일 이동평균",
            line=dict(color="#FF4B4B", width=3),
        )
    )

    fig4.update_layout(
        title="전체 박스오피스 일별 관객수 합계 및 7일 이동평균 추이",
        xaxis_title="기준일자",
        yaxis_title="총 관객수 (명)",
        hovermode="x unified",
        legend_title_text="구분",
    )

    st.plotly_chart(fig4, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 주말/평일 반복으로 인한 일별 관객수의 단기적 변동 요동(노이즈)을 제거하고, 전체 극장가 시장의 전반적인 흥행 흐름과 성수기·비성수기 추세를 명확하게 파악할 수 있습니다."
    )


# [다섯 번째 탭: 월별 총 관객수 비교 막대그래프]
with tab5:
    st.subheader("📊 전체 박스오피스 월별 총 관객수 비교")

    # 1. 기준일자별 관객수 합계 데이터 생성
    daily_sum = data.groupby("기준일자")["해당일관객수"].sum().reset_index()

    # 2. '연-월' 컬럼 생성 (YYYY-MM)
    daily_sum["연월"] = daily_sum["기준일자"].dt.strftime("%Y-%m")

    # 3. 월(연월) 단위로 관객수 다시 그룹화하여 합산
    monthly_market = (
        daily_sum.groupby("연월")["해당일관객수"].sum().reset_index()
    )

    # 4. Plotly Express를 활용한 막대그래프 생성
    fig5 = px.bar(
        monthly_market,
        x="연월",
        y="해당일관객수",
        title="월별 전체 박스오피스 관객수 합계",
        text_auto=".2s",
    )

    fig5.update_layout(
        xaxis_title="연-월",
        yaxis_title="월간 총 관객수 (명)",
        xaxis=dict(type="category"),
    )

    fig5.update_traces(
        marker_color="#4C78A8", textposition="outside"
    )

    st.plotly_chart(fig5, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 월별 총 극장 관객 규모를 비교하여 영화 시장의 월별 성수기(여름 휴가철, 명절 연휴 등)와 비성수기를 한눈에 파악할 수 있습니다."
    )


# [여섯 번째 탭: 캘린더 히트맵]
with tab6:
    st.subheader("🗓️ 일별 관객수 캘린더 히트맵")

    # 1. 기준일자별 전체 관객수 합계 데이터 계산
    daily_heatmap_df = (
        data.groupby("기준일자")["해당일관객수"].sum().reset_index()
    )

    # 2. 날짜 전처리: 연월, 요일, yyyy-mm-dd 문자열 추출
    daily_heatmap_df["연월"] = daily_heatmap_df["기준일자"].dt.strftime(
        "%Y-%m"
    )
    # yyyy-mm-dd 형식 문자열 저장 (마우스 호버 시 표시용)
    daily_heatmap_df["날짜_str"] = daily_heatmap_df["기준일자"].dt.strftime(
        "%Y-%m-%d"
    )

    # 요일 이름 추출 및 월요일~일요일 순서 정렬
    days_order = [
        "월요일",
        "화요일",
        "수요일",
        "목요일",
        "금요일",
        "토요일",
        "일요일",
    ]
    # dt.day_name() 사용 후 한글 변환
    day_map = {
        "Monday": "월요일",
        "Tuesday": "화요일",
        "Wednesday": "수요일",
        "Thursday": "목요일",
        "Friday": "금요일",
        "Saturday": "토요일",
        "Sunday": "일요일",
    }
    daily_heatmap_df["요일"] = daily_heatmap_df["기준일자"].dt.day_name().map(day_map)

    # 3. Plotly Density Heatmap (히트맵) 생성
    fig6 = px.density_heatmap(
        daily_heatmap_df,
        x="연월",
        y="요일",
        z="해당일관객수",
        category_orders={"요일": days_order},  # 월요일~일요일 순서 고정
        color_continuous_scale="Reds",  # 색상이 진할수록 관객수 많음
        title="연월 및 요일별 일관객수 히트맵",
        hover_data={
            "연월": False,
            "요일": False,
            "해당일관객수": ":,명",  # 천단위 쉼표 추가
            "날짜_str": True,  # yyyy-mm-dd 표시
        },
        labels={"날짜_str": "기준일자", "해당일관객수": "관객수"},
    )

    fig6.update_layout(
        xaxis_title="연-월",
        yaxis_title="요일",
        coloraxis_colorbar=dict(title="관객수 (명)"),
    )

    st.plotly_chart(fig6, use_container_width=True)

    # 그래프 하단 설명 문구
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 요일 및 연월별 관객 분포 밀도를 시각적으로 확인하여, 주말(토·일) 대목과 특정 연월의 붐비는 날짜 패턴을 직관적으로 비교할 수 있습니다."
    )
