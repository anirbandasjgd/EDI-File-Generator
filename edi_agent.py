"""
EDI Claim Agent - Orchestrates EDI 837 generation from form data.
Generates HIPAA-compliant 837P/837I files and saves with timestamped filenames.
"""
from pathlib import Path
from datetime import datetime

from .edi_schemas import get_loops
from .edi_generator import build_edi_content, recount_se_and_fix

# Output directory: inside EDI File Generator folder
EDI_OUTPUT_DIR = Path(__file__).resolve().parent / "edi_output"
EDI_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_837_file(claim_type: str, form_data: dict) -> dict:
    """
    Generate an 837P or 837I EDI file from user-supplied form data.
    claim_type: "837P" or "837I"
    form_data: Nested dict keyed by loop_id (1000A, 1000B, 2000A, ...), then element ids.
    Returns: {
        "success": bool,
        "file_path": str or None,
        "file_name": str or None,
        "errors": list[str],
        "message": str
    }
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

    try:
        loops_schema = get_loops(claim_type)
    except ValueError as e:
        return {
            "success": False,
            "file_path": None,
            "file_name": None,
            "errors": [str(e)],
            "message": str(e),
        }

    form_data["_ISA"] = form_data.get("_ISA", form_data.get("ISA", {}))
    edi_content, validation_errors = build_edi_content(claim_type, form_data, loops_schema)
    edi_content = recount_se_and_fix(edi_content)

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
            "errors": validation_errors + [f"Failed to write file: {e}"],
            "message": f"File could not be saved: {e}",
        }

    return {
        "success": True,
        "file_path": str(file_path),
        "file_name": file_name,
        "errors": validation_errors,
        "message": f"EDI file generated: {file_name}" + (
            f" ({len(validation_errors)} validation warning(s).)" if validation_errors else "."
        ),
    }
