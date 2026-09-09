import datetime
import requests
import pandas as pd
import pytz
import streamlit as st


# -------------------------------------------------------------------
# 1. API 데이터 요청 및 캐싱 함수
# -------------------------------------------------------------------
# @st.cache_data를 사용해 같은 날짜로 요청하면 1시간(3600초) 동안 결과를 재사용합니다.
@st.cache_data(ttl=3600)
def fetch_box_office_data(target_date, api_key):
    """KOBIS API로부터 일별 박스오피스 데이터를 가져오는 함수"""
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_date}

    try:
        # API 요청 보내기 (타임아웃 10초 설정)
        response = requests.get(url, params=params, timeout=10)

        # HTTP 응답 상태 코드가 200(성공)이 아닌 경우 에러
        if response.status_code != 200:
            return None, f"서버 통신 실패 (상태 코드: {response.status_code})"

        data = response.json()

        # 1) 인증키 오류 등으로 faultInfo가 반환된 경우
        if "faultInfo" in data:
            message = data["faultInfo"].get("message", "알 수 없는 에러")
            return None, f"API 오류 발생: {message}"

        # 2) 정상 응답 내부 데이터 확인
        box_office_result = data.get("boxOfficeResult", {})
        daily_list = box_office_result.get("dailyBoxOfficeList", [])

        # 영화 목록이 비어있는 경우
        if not daily_list:
            return (
                None,
                "선택한 날짜의 박스오피스 데이터가 비어 있습니다. (집계 중이거나 데이터 없음)",
            )

        # 데이터 가져오기 성공
        return daily_list, None

    except requests.exceptions.RequestException as e:
        # 네트워크 연결 문제 등의 예외 처리
        return None, f"네트워크 요청 중 오류가 발생했습니다: {e}"


# -------------------------------------------------------------------
# 2. 메인 Streamlit 앱 화면 구성
# -------------------------------------------------------------------
def main():
    # 페이지 기본 설정
    st.set_page_config(page_title="어제의 박스오피스", layout="wide")

    # App 제목
    st.title("🎬 어제의 박스오피스 Top 10")

    # ---------------------------------------------------------------
    # 비밀 금고(st.secrets)에서 API 키 불러오기
    # ---------------------------------------------------------------
    if "KOBIS_KEY" not in st.secrets:
        st.error("🔑 API 인증키가 설정되지 않았습니다.")
        st.info(
            "Streamlit Cloud의 App Settings > Secrets 메뉴에 `KOBIS_KEY`를 등록해 주세요."
        )
        st.stop()

    api_key = st.secrets["KOBIS_KEY"]

    # ---------------------------------------------------------------
    # 한국 시간(Asia/Seoul) 기준 '어제' 날짜 자동 계산
    # ---------------------------------------------------------------
    seoul_tz = pytz.timezone("Asia/Seoul")
    now_in_korea = datetime.datetime.now(seoul_tz)
    yesterday = now_in_korea - datetime.timedelta(days=1)

    # API 조회용 날짜 형식 (YYYYMMDD)
    target_date_str = yesterday.strftime("%Y%m%d")
    # 화면 표시용 날짜 형식 (YYYY년 MM월 DD일)
    display_date_str = yesterday.strftime("%Y년 %m월 %d일")

    st.subheader(f"📅 {display_date_str} 기준")

    # ---------------------------------------------------------------
    # 데이터 불러오기 및 예외 처리
    # ---------------------------------------------------------------
    raw_data, error_message = fetch_box_office_data(target_date_str, api_key)

    # 에러가 발생했거나 데이터가 없는 경우 안내 문구 표시
    if error_message:
        st.error("🚨 데이터를 불러오지 못했습니다.")
        st.warning(f"**상세 원인:** {error_message}")

        # 초보자/사용자를 위한 확인사항 안내
        with st.expander("💡 문제 해결 가이드 (확인할 사항)"):
            st.markdown(
                """
            1. **인증키 확인**: Secrets에 등록한 `KOBIS_KEY`가 올바른 발급 키인지 확인하세요.
            2. **일일 트래픽 제한**: KOBIS API의 하루 무료 요청 수량이 초과되었을 수 있습니다.
            3. **집계 시간**: 새벽 시간대에는 아직 전날 데이터 집계가 완료되지 않았을 수 있습니다.
            4. **네트워크 상태**: KOBIS 서버 자체 점검 중인지 확인해 보세요.
            """
            )
        st.stop()

    # ---------------------------------------------------------------
    # 데이터 가공 (Pandas DataFrame 변환 및 숫자형 변환)
    # ---------------------------------------------------------------
    df = pd.DataFrame(raw_data)

    # 문자열로 들어온 숫자 데이터들을 정수형(int)으로 변환
    numeric_columns = ["rank", "audiCnt", "audiAcc", "scrnCnt"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 순위(rank) 기준으로 정렬
    df = df.sort_values(by="rank", ascending=True)

    # ---------------------------------------------------------------
    # 화면 구성 1: 1위 영화 주요 지표 카드 (st.metric)
    # ---------------------------------------------------------------
    top_1 = df.iloc[0]

    st.markdown(f"### 🏆 1위 영화: **{top_1['movieNm']}**")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="어제 관객수", value=f"{top_1['audiCnt']:,} 명")
    with col2:
        st.metric(label="누적 관객수", value=f"{top_1['audiAcc']:,} 명")
    with col3:
        st.metric(label="스크린수", value=f"{top_1['scrnCnt']:,} 개")

    st.divider()

    # ---------------------------------------------------------------
    # 화면 구성 2: 관객수 상위 5편 막대그래프
    # ---------------------------------------------------------------
    st.subheader("📊 관객수 상위 5개 영화")

    top_5_df = df.head(5).copy()

    # Streamlit의 st.bar_chart 활용
    # 영화명을 X축(인덱스)으로 설정하고 일별 관객수를 표시
    chart_data = top_5_df.set_index("movieNm")[["audiCnt"]]
    chart_data.columns = ["어제 관객수"]
    st.bar_chart(chart_data)

    st.divider()

    # ---------------------------------------------------------------
    # 화면 구성 3: 전체 순위 표 (Top 10)
    # ---------------------------------------------------------------
    st.subheader("📋 박스오피스 전체 순위")

    # 필요한 컬럼만 추출 및 이름 변경
    display_df = df[
        ["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]
    ].copy()
    display_df.columns = [
        "순위",
        "영화명",
        "개봉일",
        "어제 관객수",
        "누적 관객수",
        "스크린수",
    ]

    # 표 화면 출력 (숫자 세 자릿수 콤마 적용)
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "순위": st.column_config.NumberColumn(format="%d 위"),
            "어제 관객수": st.column_config.NumberColumn(format="%d 명"),
            "누적 관객수": st.column_config.NumberColumn(format="%d 명"),
            "스크린수": st.column_config.NumberColumn(format="%d 개"),
        },
    )


if __name__ == "__main__":
    main()
