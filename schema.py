"""사업자등록증 추출 결과의 JSON 스키마 정의.

LiteLLM 의 response_format(JSON schema) 와 프롬프트에 함께 사용한다.
한국 사업자등록증(개인/법인) 표준 항목을 기준으로 한다.
"""

# 사업의 종류 한 줄 (업태/종목은 여러 줄일 수 있음)
_BIZTYPE_PROPS = {
    "업태": {"type": "string"},
    "종목": {"type": "string"},
}

# LiteLLM / OpenAI 호환 JSON Schema
BIZCERT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "과세유형": {
            "type": "string",
            "description": "일반과세자 / 간이과세자 / 면세사업자 / 법인사업자 중 하나",
        },
        "등록번호": {"type": "string", "description": "사업자등록번호 (예: 123-45-67890)"},
        "상호": {"type": "string", "description": "상호 또는 법인명"},
        "대표자": {"type": "string", "description": "대표자 성명"},
        "법인등록번호": {"type": "string", "description": "법인인 경우 (예: 110111-1234567)"},
        "개업연월일": {"type": "string", "description": "예: 2020-03-15"},
        "사업장소재지": {"type": "string", "description": "주된 사업장 소재지(주소)"},
        "본점소재지": {"type": "string", "description": "법인인 경우 본점 소재지"},
        "공동사업자": {"type": "string"},
        "사업자단위과세여부": {"type": "string", "description": "여 / 부"},
        "전자우편주소": {"type": "string", "description": "전자세금계산서 전용 이메일(있으면)"},
        "발급일": {"type": "string", "description": "교부일/발급일 (예: 2020-03-20)"},
        "발급세무서": {"type": "string", "description": "예: 강남세무서장"},
        "사업의종류": {
            "type": "array",
            "description": "업태/종목 표의 각 줄",
            "items": {"type": "object", "properties": _BIZTYPE_PROPS},
        },
    },
    "required": ["등록번호", "상호", "대표자"],
}

# 평탄화된(엑셀 한 행) 컬럼 순서 — 요약 시트에 사용
FLAT_COLUMNS = [
    "파일명",
    "과세유형",
    "등록번호",
    "상호",
    "대표자",
    "법인등록번호",
    "개업연월일",
    "사업장소재지",
    "본점소재지",
    "업태",  # 사업의종류 첫 줄
    "종목",  # 사업의종류 첫 줄
    "공동사업자",
    "사업자단위과세여부",
    "전자우편주소",
    "발급일",
    "발급세무서",
]
