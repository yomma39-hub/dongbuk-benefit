import io
import re
import zipfile
from pathlib import Path

import streamlit as st

# ══════════════════════════════════════════════
# 설정 (행사마다 여기만 수정)
# ══════════════════════════════════════════════
EVENT_NAME = "9월 정기모임"
BENEFIT_TITLE = "쿠팡 · 네이버 마진계산기"

BASE_DIR = Path(__file__).parent
PACK_DIR = BASE_DIR / "배포_소싱판정기"

# 대시보드 파일명 규칙 — 버전은 여기서 자동으로 읽습니다.
# 새 버전을 올릴 때 이 파일을 고칠 필요가 없습니다.
# 배포 폴더에 새 html 을 넣고 옛 파일만 지우면 끝입니다.
DASH_PATTERN = "소싱판정_대시보드_v*.html"

# 표시 순서 · 설명. 키는 파일명의 앞부분만 적으면 됩니다(버전 무관).
FILE_GUIDE = {
    "소싱판정_대시보드": "메인 계산기 — 더블클릭하면 브라우저에서 바로 열립니다",
    "소싱판정기_설명서": "사용 설명서 — 입력값과 판정 기준 안내",
    "윙요율표수집기": "쿠팡 윙 요율표 자동 수집 스크립트",
    "수집기_사용법": "요율표 수집기 사용법 (메모장으로 열어보세요)",
}

MIME = {
    ".html": "text/html",
    ".js": "text/javascript",
    ".md": "text/markdown",
}

FALLBACK_CODE = "GANA0905"  # Secrets 미설정 시 임시로 쓰이는 코드
# ══════════════════════════════════════════════

BENEFIT_CODE = st.secrets.get("BENEFIT_CODE", FALLBACK_CODE)


def dashboard_file():
    """배포 폴더에서 대시보드 파일을 찾습니다. 여러 개면 버전이 가장 높은 것."""
    if not PACK_DIR.exists():
        return None

    def key(p):
        nums = re.findall(r"\d+", p.stem.split("_v")[-1])
        return [int(n) for n in nums] or [0]

    hits = sorted(PACK_DIR.glob(DASH_PATTERN), key=key)
    return hits[-1] if hits else None


def dashboard_version():
    """파일명에서 버전 문자열을 뽑습니다. 예: v4.2.1"""
    p = dashboard_file()
    if not p:
        return ""
    m = re.search(r"_(v[\d.]+)$", p.stem)
    return m.group(1) if m else ""


def guide_for(name):
    """파일명 앞부분으로 설명을 찾습니다 (버전 숫자와 무관하게 매칭)."""
    for prefix, desc in FILE_GUIDE.items():
        if name.startswith(prefix):
            return desc
    return ""


def guide_rank(name):
    """FILE_GUIDE 에 적힌 순서대로 정렬하고, 목록에 없으면 맨 뒤로."""
    for i, prefix in enumerate(FILE_GUIDE):
        if name.startswith(prefix):
            return i
    return len(FILE_GUIDE)


VERSION = dashboard_version()
DASH_NAME = dashboard_file().name if dashboard_file() else ""
BENEFIT_SUB = f"로켓그로스 소싱판정 대시보드 {VERSION}".strip()
ZIP_NAME = f"소싱판정기_패키지_{VERSION}.zip" if VERSION else "소싱판정기_패키지.zip"

st.set_page_config(
    page_title=f"{EVENT_NAME} 참가혜택",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed",
)

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


def collect_files():
    """배포 폴더의 파일을 FILE_GUIDE 순서대로 모으고, 목록에 없는 파일은 뒤에 붙인다."""
    if not PACK_DIR.exists():
        return []

    files = [p for p in PACK_DIR.iterdir() if p.is_file()]
    return sorted(files, key=lambda p: (guide_rank(p.name), p.name))


@st.cache_data(show_spinner=False)
def build_zip(names_and_bytes):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in names_and_bytes:
            zf.writestr(name, data)
    return buf.getvalue()


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
    files = collect_files()

    if not files:
        st.error("자료 파일을 찾을 수 없습니다. 운영자에게 알려주세요.")
        with st.expander("진단 정보"):
            st.write("배포 폴더 경로:", str(PACK_DIR))
            st.write("폴더 존재:", PACK_DIR.exists())
            st.write("저장소 루트 목록:", [p.name for p in BASE_DIR.iterdir()])
    else:
        st.success("확인되었습니다. 아래에서 내려받으세요.")

        payload = tuple((p.name, p.read_bytes()) for p in files)
        st.download_button(
            f"📦 전체 받기 ({len(files)}개 파일 ZIP)",
            data=build_zip(payload),
            file_name=ZIP_NAME,
            mime="application/zip",
            type="primary",
            use_container_width=True,
        )

        st.divider()
        st.markdown("**개별로 받으시려면**")

        for path in files:
            desc = guide_for(path.name)
            if desc:
                st.caption(f"**{path.name}** — {desc}")
            st.download_button(
                f"⬇️ {path.name}",
                data=path.read_bytes(),
                file_name=path.name,
                mime=MIME.get(path.suffix.lower(), "application/octet-stream"),
                key=f"dl_{path.name}",
                use_container_width=True,
            )

        st.divider()
        st.markdown(
            f"""
            **사용 방법**

            1. ZIP을 받으신 뒤 압축을 풀어주세요
            2. `{DASH_NAME}`을 더블클릭하면 브라우저에서 바로 열립니다
            3. 설치나 로그인이 필요 없습니다
            4. 입력하신 값은 서버로 전송되지 않고 기기 안에만 저장됩니다
            5. 즐겨찾기에 추가해두시면 다음에도 바로 여실 수 있습니다
            """
        )

st.divider()
st.caption("가나양말 · 동북 정기모임")
