"""
Generate 837 EDI file via OpenAI: UI data → JSON template → API → EDI file.
"""
import json
import os
import re
from pathlib import Path
from datetime import datetime

# Load .env from project root (parent of EDI_File_Generator)
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(_env_path)
except ImportError:
    pass

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EDI_OUTPUT_DIR = Path(__file__).resolve().parent / "edi_output"
EDI_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_MESSAGE = (
    "You are a helpful assistant and an expert on claims to generate an 837 file. "
    "Given claim data as JSON, you produce a valid HIPAA 5010 X12 837P or 837I EDI file. "
    "Use standard delimiters: segment terminator ~, element separator *, component :. "
    "Output only the raw EDI content from ISA through IEA, with no explanation or markdown."
)


def build_claim_json(form_data: dict, claim_type: str) -> dict:
    """
    Build a JSON template with all elements from the UI form data.
    Structure: { "claim_type": "837P"|"837I", "loops": { "1000A": {...}, "2300": {...}, "2400": [...] } }
    """
    claim_type = claim_type.upper().strip()
    loops = {}
    for loop_id, value in form_data.items():
        if loop_id.startswith("_"):
            continue
        loops[loop_id] = value
    return {
        "claim_type": claim_type,
        "loops": loops,
    }


def _extract_edi_from_response(text: str) -> str:
    """Extract raw EDI from API response; strip markdown code blocks if present."""
    if not text or not text.strip():
        return ""
    text = text.strip()
    # Remove optional markdown code block
    m = re.search(r"```(?:edi|edi\s*)?\s*\n?([\s\S]*?)```", text, re.IGNORECASE)
    if m:
        text = m.group(1).strip()
    return text


def generate_837_via_openai(claim_type: str, claim_json: dict) -> dict:
    """
    Send claim JSON to OpenAI with system message; save returned EDI to file.
    claim_type: "837P" or "837I"
    claim_json: from build_claim_json(form_data, claim_type)
    Returns: { "success", "file_path", "file_name", "errors", "message" }
    """
    claim_type = claim_type.upper().strip()
    if claim_type not in ("837P", "837I"):
        return {
            "success": False,
            "file_path": None,
            "file_name": None,
            "errors": [f"Invalid claim type: {claim_type}. Use 837P or 837I."],
            "message": "Invalid claim type.",
        }

    if not OPENAI_API_KEY:
        return {
            "success": False,
            "file_path": None,
            "file_name": None,
            "errors": ["OPENAI_API_KEY is not set. Add it to your .env file."],
            "message": "OpenAI API key is missing.",
        }

    user_content = (
        f"Generate a valid HIPAA 5010 {claim_type} EDI file from the following claim data. "
        "Output only the raw EDI content (ISA through IEA), no explanation.\n\n"
        + json.dumps(claim_json, indent=2)
    )

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": user_content},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or ""
    except Exception as e:
        return {
            "success": False,
            "file_path": None,
            "file_name": None,
            "errors": [str(e)],
            "message": f"OpenAI API error: {e}",
        }

    edi_content = _extract_edi_from_response(content)
    if not edi_content or "ISA" not in edi_content:
        return {
            "success": False,
            "file_path": None,
            "file_name": None,
            "errors": ["OpenAI did not return valid EDI content (expected ISA segment)."],
            "message": "Invalid or empty EDI content from API.",
        }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{claim_type}_{timestamp}.edi"
    file_path = EDI_OUTPUT_DIR / file_name

    try:
        file_path.write_text(edi_content, encoding="utf-8")
    except Exception as e:
        return {
            "success": False,
            "file_path": None,
            "file_name": file_name,
            "errors": [f"Failed to write file: {e}"],
            "message": f"File could not be saved: {e}",
        }

    return {
        "success": True,
        "file_path": str(file_path),
        "file_name": file_name,
        "errors": [],
        "message": f"EDI file generated via OpenAI: {file_name}",
    }
