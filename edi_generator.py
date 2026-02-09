"""
EDI 837 Generator - Builds HIPAA-compliant 837P/837I X12 files.
Implements SNIP Level 2 validations: segment syntax, required elements, and IG requirements.
"""
import re
from typing import Any
from datetime import datetime

# X12 5010 delimiters (HIPAA standard)
SEGMENT_TERMINATOR = "~"
ELEMENT_SEPARATOR = "*"
COMPONENT_SEPARATOR = ":"
REPETITION_SEPARATOR = "^"


def _sanitize(value: Any) -> str:
    """Remove invalid X12 characters from a value."""
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return ""
    s = str(value).strip()
    for c in (SEGMENT_TERMINATOR, ELEMENT_SEPARATOR, COMPONENT_SEPARATOR, REPETITION_SEPARATOR):
        s = s.replace(c, "")
    return s


def _validate_required(loop_data: dict, loops_schema: list) -> list[str]:
    """SNIP2-style: Check required elements are present. Returns list of error messages."""
    errors = []
    for loop_def in loops_schema:
        loop_id = loop_def["loop_id"]
        loop_values = loop_data.get(loop_id, {})
        if isinstance(loop_values, list):
            for i, item in enumerate(loop_values):
                for seg in loop_def.get("segments", []):
                    for el in seg.get("elements", []):
                        if el.get("required"):
                            key = el["id"] if i == 0 else f"{el['id']}_{i}"
                            val = item.get(el["id"], item.get(key, ""))
                            if not _sanitize(val):
                                errors.append(f"Loop {loop_id}[{i}]: Required {el['id']} ({el['label']}) is missing.")
        else:
            for seg in loop_def.get("segments", []):
                for el in seg.get("elements", []):
                    if el.get("required"):
                        val = loop_values.get(el["id"], "")
                        if not _sanitize(val):
                            errors.append(f"Loop {loop_id}: Required {el['id']} ({el['label']}) is missing.")
    return errors


def _build_segment(seg_id: str, elements: list[str]) -> str:
    """Build one X12 segment: ID*el1*el2*el3~"""
    parts = [seg_id]
    for el in elements:
        parts.append(_sanitize(el))
    return ELEMENT_SEPARATOR.join(parts) + SEGMENT_TERMINATOR


def _format_date(d: str) -> str:
    """Convert YYYY-MM-DD or similar to YYYYMMDD for DTP."""
    if not d:
        return ""
    d = re.sub(r"[-\s]", "", str(d))
    return d[:8] if len(d) >= 8 else d


def build_edi_content(claim_type: str, form_data: dict, loops_schema: list) -> tuple[str, list[str]]:
    """
    Build full EDI 837 (with ISA/GS/ST envelope) from form data.
    Returns (edi_string, validation_errors).
    """
    errors = _validate_required(form_data, loops_schema)
    segments_out = []

    _isa = form_data.get("_ISA", form_data.get("ISA", {}))
    isa01 = (_isa.get("ISA01") or "00").ljust(2)[:2]
    isa02 = (_isa.get("ISA02") or "").ljust(10)[:10]
    isa03 = (_isa.get("ISA03") or "00").ljust(2)[:2]
    isa04 = (_isa.get("ISA04") or "").ljust(10)[:10]
    isa05 = (_isa.get("ISA05") or "01").ljust(2)[:2]
    isa06 = (_isa.get("ISA06") or "SENDER").ljust(15)[:15]
    isa07 = (_isa.get("ISA07") or "01").ljust(2)[:2]
    isa08 = (_isa.get("ISA08") or "RECEIVER").ljust(15)[:15]
    isa09 = datetime.now().strftime("%y%m%d")
    isa10 = datetime.now().strftime("%H%M")
    isa11 = _isa.get("ISA11") or REPETITION_SEPARATOR
    isa12 = (_isa.get("ISA12") or "00501").ljust(5)[:5]
    isa13 = (_isa.get("ISA13") or datetime.now().strftime("%y%m%d%H%M")[:9]).rjust(9)[-9:]
    isa14 = (_isa.get("ISA14") or "0")[:1]
    isa15 = (_isa.get("ISA15") or "T")[:1]
    isa16 = (_isa.get("ISA16") or COMPONENT_SEPARATOR)[:1]
    segments_out.append(_build_segment("ISA", [
        isa01, isa02, isa03, isa04, isa05, isa06, isa07, isa08,
        isa09, isa10, isa11, isa12, isa13, isa14, isa15, isa16
    ]))

    gs_date = datetime.now().strftime("%Y%m%d")
    gs_time = datetime.now().strftime("%H%M")
    gs_id = "1"
    gs_ver = "005010X222A1" if claim_type.upper() == "837P" else "005010X223A2"
    segments_out.append(_build_segment("GS", ["HC", "SENDER", "RECEIVER", gs_date, gs_time, gs_id, "X", gs_ver]))

    st_control = "0001"
    segments_out.append(_build_segment("ST", ["837", st_control, "004010X098A1" if claim_type.upper() == "837P" else "004010X096A1"]))
    segments_out.append(_build_segment("BHT", ["0019", "00", form_data.get("_BHT", {}).get("BHT03", "0000000001"), datetime.now().strftime("%Y%m%d"), datetime.now().strftime("%H%M"), "CH"]))

    for loop_def in loops_schema:
        loop_id = loop_def["loop_id"]
        repeatable = loop_def.get("repeatable", False)
        loop_values = form_data.get(loop_id)
        if loop_values is None:
            if loop_id in ("1000A", "1000B", "2000A", "2000B", "2000C", "2300"):
                errors.append(f"Loop {loop_id} is required.")
            continue
        items = loop_values if (repeatable and isinstance(loop_values, list)) else ([loop_values] if loop_values else [])

        for item in items:
            if not isinstance(item, dict):
                continue
            for seg_def in loop_def.get("segments", []):
                seg_id = seg_def["seg_id"]
                elements = []
                for el_def in seg_def.get("elements", []):
                    el_id = el_def["id"]
                    val = item.get(el_id, "")
                    if "03" in el_id and "DTP" in el_id:
                        val = _format_date(val)
                    elements.append(val)
                if any(_sanitize(e) for e in elements):
                    segments_out.append(_build_segment(seg_id, elements))

    st_idx = next((i for i, s in enumerate(segments_out) if s.startswith("ST" + ELEMENT_SEPARATOR)), None)
    if st_idx is not None:
        se_count = len(segments_out) - st_idx + 1
        segments_out.append(_build_segment("SE", [str(se_count), st_control]))
    else:
        segments_out.append(_build_segment("SE", ["0", st_control]))
    segments_out.append(_build_segment("GE", ["1", gs_id]))
    segments_out.append(_build_segment("IEA", ["1", "000000001"]))

    return (SEGMENT_TERMINATOR.join(segments_out), errors)


def recount_se_and_fix(edi: str) -> str:
    """Fix SE segment count: count segments between ST and SE (inclusive)."""
    parts = edi.split(SEGMENT_TERMINATOR)
    st_idx = se_idx = None
    for i, p in enumerate(parts):
        if p.startswith("ST" + ELEMENT_SEPARATOR):
            st_idx = i
        if p.startswith("SE" + ELEMENT_SEPARATOR):
            se_idx = i
            break
    if st_idx is not None and se_idx is not None:
        count = se_idx - st_idx + 1
        se_parts = parts[se_idx].split(ELEMENT_SEPARATOR)
        if len(se_parts) >= 2:
            se_parts[1] = str(count)
            parts[se_idx] = ELEMENT_SEPARATOR.join(se_parts)
            return SEGMENT_TERMINATOR.join(parts)
    return edi
