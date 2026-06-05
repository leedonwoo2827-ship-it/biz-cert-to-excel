"""추출된 사업자등록증 dict 들을 엑셀(xlsx) 파일로 저장한다.

- 시트1 '사업자등록증': 한 행 = 한 장의 요약
- 시트2 '사업의종류': 파일명 기준으로 업태/종목 줄들을 펼쳐서 기록
"""

from __future__ import annotations

import io

import pandas as pd

from schema import FLAT_COLUMNS


def _flatten(filename: str, data: dict) -> dict:
    """중첩 dict 를 엑셀 한 행(평탄화)으로 변환."""
    biztypes = data.get("사업의종류", []) or []
    first = biztypes[0] if biztypes else {}
    return {
        "파일명": filename,
        "과세유형": data.get("과세유형", ""),
        "등록번호": data.get("등록번호", ""),
        "상호": data.get("상호", ""),
        "대표자": data.get("대표자", ""),
        "법인등록번호": data.get("법인등록번호", ""),
        "개업연월일": data.get("개업연월일", ""),
        "사업장소재지": data.get("사업장소재지", ""),
        "본점소재지": data.get("본점소재지", ""),
        "업태": first.get("업태", ""),
        "종목": first.get("종목", ""),
        "공동사업자": data.get("공동사업자", ""),
        "사업자단위과세여부": data.get("사업자단위과세여부", ""),
        "전자우편주소": data.get("전자우편주소", ""),
        "발급일": data.get("발급일", ""),
        "발급세무서": data.get("발급세무서", ""),
    }


def build_excel(results: list[tuple[str, dict]]) -> bytes:
    """results = [(파일명, 추출dict), ...] → xlsx bytes 반환."""
    summary_rows = [_flatten(name, data) for name, data in results]
    summary_df = pd.DataFrame(summary_rows, columns=FLAT_COLUMNS)

    biztype_rows = []
    for name, data in results:
        for item in data.get("사업의종류", []) or []:
            row = {"파일명": name}
            row.update(item)
            biztype_rows.append(row)
    biztypes_df = pd.DataFrame(biztype_rows)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="사업자등록증", index=False)
        if not biztypes_df.empty:
            biztypes_df.to_excel(writer, sheet_name="사업의종류", index=False)
        # 컬럼 폭 자동 조정
        for sheet_name, df in (("사업자등록증", summary_df), ("사업의종류", biztypes_df)):
            if df.empty:
                continue
            ws = writer.sheets[sheet_name]
            for i, col in enumerate(df.columns, start=1):
                width = max(len(str(col)), *(len(str(v)) for v in df[col])) if len(df) else len(str(col))
                ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = min(width + 2, 40)

    buf.seek(0)
    return buf.getvalue()
