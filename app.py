import streamlit as st
from pathlib import Path

# ══════════════════════════════════════════════
# 설정 (행사마다 여기만 수정)
# ══════════════════════════════════════════════
EVENT_NAME = "9월 정기모임"
BENEFIT_TITLE = "쿠팡 · 네이버 마진계산기"
BENEFIT_SUB = "로켓그로스 소싱판정 대시보드"
ASSETS_DIR = Path(__file__).parent / "assets"
BENEFIT_FILE = ASSETS_DIR / "margin_calculator.html"
DOWNLOAD_NAME = "소싱판정_대시보드_v3.7.0.html"
FALLBACK_CODE = "GANA0905"  # Secrets 미설정 시 임시로 쓰이는 코드
# ══════════════════════════════════════════════

BENEFIT_CODE = st.secrets.get("BENEFIT_CODE", FALLBACK_CODE)

st.set_page_config(
    page_title=f"{EVENT_NAME} 참가혜택",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 사이드바 완전히 숨기기 (단일 페이지 앱)
st.markdown(
    """
    <style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {display: none;}
    #MainMenu, footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎁 참가자 혜택")
st.markdown(f"### {BENEFIT_TITLE}")
st.caption(f"{EVENT_NAME} · {BENEFIT_SUB}")
st.divider()

if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

if not st.session_state.unlocked:
    st.markdown("모임 현장에서 안내드린 **시크릿 코드**를 입력해 주세요.")

    code = st.text_input(
        "시크릿 코드",
        type="password",
        placeholder="현장에서 안내드린 코드",
        label_visibility="collapsed",
    )

    if st.button("확인", type="primary", use_container_width=True):
        if code.strip().upper() == BENEFIT_CODE.strip().upper():
            st.session_state.unlocked = True
            st.rerun()
        else:
            st.error("코드가 일치하지 않습니다.")

    st.caption("🔒 코드는 모임 당일 현장에서 참석자분들께만 안내드립니다.")

else:
    # 지정한 파일이 없으면 assets 폴더의 다른 html 파일을 자동으로 사용
    target = BENEFIT_FILE
    if not target.exists():
        candidates = sorted(ASSETS_DIR.glob("*.html")) if ASSETS_DIR.exists() else []
        target = candidates[0] if candidates else None

    if target is None:
        st.error("자료 파일을 찾을 수 없습니다. 운영자에게 알려주세요.")
        with st.expander("진단 정보"):
            st.write("assets 폴더 존재:", ASSETS_DIR.exists())
            if ASSETS_DIR.exists():
                st.write("폴더 안 파일 목록:", [p.name for p in ASSETS_DIR.iterdir()])
    else:
        st.success("확인되었습니다. 아래 버튼으로 내려받으세요.")

        st.download_button(
            "📥 마진계산기 다운로드 (HTML)",
            data=target.read_bytes(),
            file_name=DOWNLOAD_NAME,
            mime="text/html",
            type="primary",
            use_container_width=True,
        )

        st.divider()
        st.markdown(
            """
            **사용 방법**

            1. 내려받은 파일을 더블클릭하면 브라우저에서 바로 열립니다
            2. 설치나 로그인이 필요 없습니다
            3. 입력하신 값은 서버로 전송되지 않고 기기 안에만 저장됩니다
            4. 즐겨찾기에 추가해두시면 다음에도 바로 여실 수 있습니다
            """
        )

st.divider()
st.caption("가나양말 · 동북 정기모임")
