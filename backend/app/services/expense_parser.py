import json
import logging

from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

CATEGORIES = [
    "Nhà ở",
    "Ăn uống",
    "Chợ - Siêu thị",
    "Di chuyển",
    "Mua sắm",
    "Giải trí",
    "Làm đẹp",
    "Sức khoẻ",
    "Hoá đơn",
    "Nhà cửa",
    "Người thân",
    "Đầu tư",
    "Khác",
]

SYSTEM_PROMPT = (
    "Bạn là trợ lý phân tích chi tiêu. Trích xuất thông tin từ câu mô tả và trả về JSON thuần.\n"
    "Quy ước: k=1000, tr=1.000.000\n"
    f"Danh mục hợp lệ: {json.dumps(CATEGORIES, ensure_ascii=False)}"
)

USER_PROMPT = (
    "Trích xuất: description (sửa lỗi chính tả), amount (VND, số nguyên), category.\n"
    'Trả về JSON: {{"description": "...", "amount": 0, "category": "..."}}\n'
    'Input: "{text}"'
)


def parse_spending(text: str) -> dict[str, str | float]:
    """Return dict with description, amount, category. Falls back on error."""
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT.format(text=text)},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        return {
            "description": data.get("description") or text,
            "amount": float(data.get("amount") or 0),
            "category": data["category"] if data.get("category") in CATEGORIES else "Khác",
        }
    except Exception as e:
        logger.warning("GPT parse failed: %s", e)
        return {"description": text, "amount": 0.0, "category": "Khác"}
