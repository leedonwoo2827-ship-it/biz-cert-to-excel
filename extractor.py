"""세금계산서 이미지를 LiteLLM(비전) 으로 읽어 구조화 JSON 으로 추출한다.

- 로컬(Ollama) / 클라우드(OpenAI·Gemini·Anthropic 등) 무엇이든
  LITELLM_MODEL 문자열만 바꾸면 동작한다.
- 출력은 schema.INVOICE_JSON_SCHEMA 구조의 dict.
"""

from __future__ import annotations

import base64
import io
import json
import os
import re

import litellm

from schema import BIZCERT_JSON_SCHEMA

litellm.drop_params = True  # 모델이 지원 안 하는 파라미터는 자동 제거

_PROMPT = """당신은 한국 사업자등록증을 읽는 OCR 추출 도우미입니다.
첨부된 이미지(사업자등록증)에서 항목을 정확히 읽어 JSON 으로만 응답하세요.

규칙:
- 칸이 비어 있으면 빈 문자열("")로 두세요. 값을 지어내지 마세요.
- 사업자등록번호는 'NNN-NN-NNNNN' 형식으로 적으세요.
- 날짜는 'YYYY-MM-DD' 형식으로 적으세요.
- 과세유형은 문서 상단/제목의 표기를 보고 일반과세자/간이과세자/면세사업자/법인사업자 중 하나로 적으세요.
- '사업의 종류'에 업태/종목이 여러 줄이면 각 줄을 배열 원소로 만드세요.
- 설명/주석 없이 JSON 객체 하나만 출력하세요.

다음 JSON 스키마를 따르세요:
""" + json.dumps(BIZCERT_JSON_SCHEMA, ensure_ascii=False, indent=2)


def _img_to_data_uri(image_bytes: bytes, mime: str = "image/png") -> str:
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def _extract_json(text: str) -> dict:
    """모델 응답 문자열에서 JSON 객체를 안전하게 파싱한다."""
    text = text.strip()
    # ```json ... ``` 코드펜스 제거
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 본문 중 첫 '{' ~ 마지막 '}' 구간만 잘라 재시도
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def extract_cert(image_bytes: bytes, mime: str = "image/png") -> dict:
    """사업자등록증 이미지 1장을 추출하여 dict 반환."""
    model = os.getenv("LITELLM_MODEL", "openai/gemini-2.5-flash")
    timeout = float(os.getenv("LITELLM_TIMEOUT", "600"))

    kwargs = {
        "model": model,
        "timeout": timeout,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _PROMPT},
                    {"type": "image_url", "image_url": {"url": _img_to_data_uri(image_bytes, mime)}},
                ],
            }
        ],
    }

    # 사내 LiteLLM 프록시 (OpenAI 호환) 자격증명
    api_base = os.getenv("LITELLM_API_BASE")
    api_key = os.getenv("LITELLM_API_KEY")
    if api_base:
        kwargs["api_base"] = api_base
    if api_key:
        kwargs["api_key"] = api_key

    # JSON 강제(지원 모델만 — drop_params 로 미지원 시 무시됨)
    kwargs["response_format"] = {"type": "json_object"}

    resp = litellm.completion(**kwargs)
    content = resp["choices"][0]["message"]["content"]
    return _extract_json(content)
