"""사업자등록증 → 엑셀 변환기 (Streamlit + LiteLLM 비전)

실행:  streamlit run app.py
"""

from __future__ import annotations

import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from excel_writer import build_excel
from extractor import extract_cert
from imaging import to_png_pages

load_dotenv()

# 비전 모델 — 고정(사용자 변경 불가)
FIXED_MODEL = "gemini-2.5-flash"

st.set_page_config(page_title="사업자등록증 → 엑셀", page_icon="📄", layout="wide")
st.title("📄 사업자등록증 → 엑셀 변환기")
st.caption("사업자등록증 이미지/PDF 를 비전 LLM 으로 읽어 엑셀로 저장합니다.")

# ---- 사이드바: 모델 설정 ----
with st.sidebar:
    st.header("⚙️ 설정")
    st.caption(f"비전 모델: **{FIXED_MODEL}** (고정)")

    base_url = st.text_input(
        "프록시 URL",
        value=os.getenv("LITELLM_API_BASE", "http://192.168.50.119:4000/v1"),
        help="예) http://192.168.50.119:4000/v1",
    )
    api_key = st.text_input(
        "API 키",
        value=os.getenv("LITELLM_API_KEY", ""),
        type="password",
        help="사내 LiteLLM 키 (.env 에 미리 넣어두면 자동 채워짐)",
    )

    # 모델은 코드에 고정 — 사용자가 바꿀 수 없음
    os.environ["LITELLM_MODEL"] = f"openai/{FIXED_MODEL}"
    os.environ["LITELLM_API_BASE"] = base_url
    if api_key:
        os.environ["LITELLM_API_KEY"] = api_key

    if base_url and api_key:
        st.success("프록시 연결 준비됨")
    else:
        st.warning("URL 과 API 키를 모두 입력하세요.")

# ---- 파일 업로드 (드래그앤드롭 지원) ----
st.markdown("#### 📥 여기로 파일을 끌어다 놓으세요 (드래그앤드롭) — 여러 개 가능")
files = st.file_uploader(
    "사업자등록증 파일을 드래그앤드롭 하거나 클릭해서 선택하세요",
    type=["png", "jpg", "jpeg", "webp", "pdf"],
    accept_multiple_files=True,
    label_visibility="visible",
)

if files and st.button("📤 추출 시작", type="primary"):
    results: list[tuple[str, dict]] = []
    errors: list[str] = []
    progress = st.progress(0.0, text="처리 중...")

    for idx, f in enumerate(files):
        try:
            pages = to_png_pages(f.getvalue(), f.name)
            # PDF 등 여러 페이지면 각 페이지를 한 장으로 취급
            for p_idx, png in enumerate(pages):
                label = f.name if len(pages) == 1 else f"{f.name} (p{p_idx + 1})"
                progress.progress((idx) / len(files), text=f"읽는 중: {label}")
                data = extract_cert(png, mime="image/png")
                results.append((label, data))
        except Exception as e:  # noqa: BLE001
            errors.append(f"{f.name}: {e}")
        progress.progress((idx + 1) / len(files), text=f"완료: {f.name}")

    progress.empty()

    if errors:
        for err in errors:
            st.error(err)

    if results:
        st.session_state["results"] = results
        st.success(f"{len(results)}건 추출 완료")

# ---- 결과 표시 & 다운로드 ----
if st.session_state.get("results"):
    results = st.session_state["results"]

    from schema import FLAT_COLUMNS
    from excel_writer import _flatten

    preview = pd.DataFrame([_flatten(n, d) for n, d in results], columns=FLAT_COLUMNS)
    st.subheader("미리보기 (요약)")
    st.dataframe(preview, use_container_width=True)

    with st.expander("원본 추출 JSON 보기"):
        for name, data in results:
            st.markdown(f"**{name}**")
            st.json(data)

    xlsx = build_excel(results)
    st.download_button(
        "💾 엑셀(.xlsx) 다운로드",
        data=xlsx,
        file_name="사업자등록증.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
    )
