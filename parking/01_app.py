import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="공영주차장 정보 제공",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 공영주차장 정보 제공 서비스")

# CSV 업로드
uploaded_file = st.file_uploader(
    "공영주차장 CSV 파일을 업로드하세요.",
    type=["csv"]
)

if uploaded_file is not None:

    # -----------------------------
    # CSV 읽기 (인코딩 자동 처리)
    # -----------------------------
    df = None

    encodings = ["utf-8", "utf-8-sig", "cp949", "euc-kr"]

    for enc in encodings:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc)
            st.success(f"파일을 성공적으로 불러왔습니다. (인코딩: {enc})")
            break
        except Exception:
            pass

    if df is None:
        st.error("CSV 파일을 읽을 수 없습니다. 인코딩을 확인해주세요.")
        st.stop()

    # 데이터 확인
    st.subheader("📋 주차장 데이터")
    st.dataframe(df)

    # 필요한 컬럼 확인
    required_columns = [
        "주차장명",
        "주소",
        "위도",
        "경도",
        "기본요금",
        "추가요금",
        "운영시간"
    ]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        st.error(f"다음 컬럼이 없습니다.\n\n{missing}")
        st.write("현재 CSV 컬럼")
        st.write(df.columns.tolist())
        st.stop()

    # -----------------------------
    # 주소 검색
    # -----------------------------
    st.subheader("🔍 주소 검색")

    keyword = st.text_input("주소를 입력하세요.")

    if keyword:

        result = df[df["주소"].astype(str).str.contains(keyword, case=False, na=False)]

        if result.empty:
            st.warning("검색 결과가 없습니다.")

        else:
            st.success(f"{len(result)}개의 주차장을 찾았습니다.")

            st.dataframe(
                result[
                    [
                        "주차장명",
                        "주소",
                        "기본요금",
                        "추가요금",
                        "운영시간"
                    ]
                ]
            )

    # -----------------------------
    # 지도
    # -----------------------------
    st.subheader("🗺️ 공영주차장 위치")

    center = [
        df["위도"].astype(float).mean(),
        df["경도"].astype(float).mean()
    ]

    m = folium.Map(location=center, zoom_start=12)

    for _, row in df.iterrows():

        popup = f"""
        <b>{row['주차장명']}</b><br>
        주소 : {row['주소']}<br>
        기본요금 : {row['기본요금']}<br>
        추가요금 : {row['추가요금']}<br>
        운영시간 : {row['운영시간']}
        """

        tooltip = f"""
        {row['주소']}<br>
        기본요금 : {row['기본요금']}
        """

        folium.Marker(
            location=[
                float(row["위도"]),
                float(row["경도"])
            ],
            popup=popup,
            tooltip=tooltip,
            icon=folium.Icon(color="blue")
        ).add_to(m)

    st_folium(
        m,
        width=1200,
        height=600
    )

else:
    st.info("CSV 파일을 업로드하면 서비스를 이용할 수 있습니다.")
