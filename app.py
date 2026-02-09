"""
EDI File Generator - Streamlit UI
Select claim type (837P/837I), enter segment values for each loop, then generate the EDI file.
Run from project root: streamlit run EDI_File_Generator/app.py
"""
import re
import sys
from pathlib import Path

# Ensure project root is on path so EDI_File_Generator package can be imported
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from EDI_File_Generator import get_loops, generate_837_file

st.set_page_config(
    page_title="EDI File Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .main-header h1 { margin: 0; font-size: 1.8rem; }
    .main-header p { margin: 0.3rem 0 0 0; opacity: 0.9; font-size: 0.95rem; }
    .loop-card { background: #f8fafc; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem; }
    .edi-error-label { color: #dc3545; font-size: 0.85rem; margin-bottom: 0.25rem; font-weight: 500; }
    .edi-error-row { background: #fff5f5; border-left: 4px solid #dc3545; padding: 0.5rem 0.75rem; border-radius: 4px; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)


def _parse_error_keys(claim_type: str, error_messages: list) -> set:
    """
    Parse validation error messages and return the set of UI keys for fields that are missing.
    Errors look like: "Loop 1000A: Required NM101 (...) is missing." or "Loop 2400[1]: Required LX01 (...) is missing."
    """
    keys = set()
    prefix = f"edi_{claim_type}_"
    # Loop 2400[1]: Required LX01 (...) is missing.  (match repeatable first)
    pattern_repeat = re.compile(r"Loop (\w+)\[(\d+)\]: Required ([A-Z0-9_]+) ")
    # Loop 1000A: Required NM101 (...) is missing.  (el_id can be NM101, DTP01_2, etc.)
    pattern_simple = re.compile(r"Loop (\w+): Required ([A-Z0-9_]+) ")
    for msg in error_messages:
        m = pattern_repeat.match(msg)
        if m:
            loop_id, idx, el_id = m.group(1), m.group(2), m.group(3)
            keys.add(f"{prefix}{loop_id}_{idx}_{el_id}")
            continue
        m = pattern_simple.match(msg)
        if m:
            loop_id, el_id = m.group(1), m.group(2)
            keys.add(f"{prefix}{loop_id}_{el_id}")
    return keys


def _collect_form_data(claim_type: str) -> dict:
    """Build form_data from session_state keys prefixed with edi_{claim_type}_."""
    form_data = {}
    prefix = f"edi_{claim_type}_"
    for key, value in list(st.session_state.items()):
        if not key.startswith(prefix) or not isinstance(value, str):
            continue
        if "_2400_count" in key:
            continue
        rest = key[len(prefix):]
        parts = rest.split("_")
        if len(parts) >= 2 and parts[0] == "2400" and parts[1].isdigit():
            idx = int(parts[1])
            el_id = "_".join(parts[2:]) if len(parts) > 2 else parts[1]
            if "2400" not in form_data:
                form_data["2400"] = []
            while len(form_data["2400"]) <= idx:
                form_data["2400"].append({})
            form_data["2400"][idx][el_id] = value
        elif len(parts) >= 2:
            loop_id = parts[0]
            el_id = "_".join(parts[1:])
            if loop_id not in form_data:
                form_data[loop_id] = {}
            form_data[loop_id][el_id] = value
    form_data["_ISA"] = form_data.get("ISA", form_data.get("_ISA", {}))
    return form_data


def _render_field_with_error(claim_type: str, loop_id: str, el: dict, key: str, index: int | None = None):
    """Render a text input, wrapped with red highlight and error message when key is in edi_error_keys."""
    error_keys = st.session_state.get("edi_error_keys", set())
    is_error = key in error_keys
    if is_error:
        st.markdown(
            '<p class="edi-error-label">⚠ Required – please enter a value</p>',
            unsafe_allow_html=True,
        )
    col_bar, col_input = st.columns([0.02, 0.98])
    with col_bar:
        if is_error:
            st.markdown(
                '<div style="background:#dc3545; min-height:2.5em; border-radius:4px;"></div>',
                unsafe_allow_html=True,
            )
    with col_input:
        st.text_input(
            el["label"],
            key=key,
            placeholder=el.get("help", ""),
            help=el.get("help") if not el.get("required") else f"Required. {el.get('help', '')}",
        )


def main():
    st.markdown("""
    <div class="main-header">
        <h1>📄 EDI File Generator</h1>
        <p>Generate HIPAA-compliant 837P (Professional) or 837I (Institutional) claim files. Select the file type, then enter segment values for each loop.</p>
    </div>
    """, unsafe_allow_html=True)

    # 1. Select type of file
    claim_type = st.radio(
        "**1. Select the type of file**",
        ["837P", "837I"],
        format_func=lambda x: "837P – Professional (Physician/Ambulatory)" if x == "837P" else "837I – Institutional (Hospital/Facility)",
        key="edi_claim_type",
        horizontal=True,
    )

    try:
        loops = get_loops(claim_type)
    except ValueError as e:
        st.error(str(e))
        return

    # Show validation error banner when fields are highlighted in red (after rerun)
    all_error_keys = st.session_state.get("edi_error_keys", set())
    error_keys = {k for k in all_error_keys if k.startswith(f"edi_{claim_type}_")}
    if error_keys:
        st.error("**Please fix the required fields highlighted in red below.**")

    # Optional ISA (interchange) section
    with st.expander("Interchange / ISA (optional – leave blank for defaults)", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Sender ID (ISA06)", key=f"edi_{claim_type}_ISA_ISA06", placeholder="SENDER")
            st.text_input("Receiver ID (ISA08)", key=f"edi_{claim_type}_ISA_ISA08", placeholder="RECEIVER")
        with c2:
            st.text_input("ISA Control Number (ISA13)", key=f"edi_{claim_type}_ISA_ISA13", placeholder="Auto-generated")
        st.caption("Other ISA elements use standard 5010 defaults.")

    # 2. For each loop: allow user to enter segment values
    st.markdown("---")
    st.markdown("**2. Enter segment values for each loop**")

    for loop_def in loops:
        loop_id = loop_def["loop_id"]
        name = loop_def["name"]
        desc = loop_def.get("description", "")
        repeatable = loop_def.get("repeatable", False)

        with st.expander(f"**Loop {loop_id}**: {name}", expanded=(loop_id in ("1000A", "2300"))):
            if desc:
                st.caption(desc)
            if repeatable and loop_id == "2400":
                n_lines = st.number_input(
                    "Number of service lines",
                    min_value=1,
                    max_value=20,
                    value=st.session_state.get("edi_service_line_count", 1),
                    key=f"edi_{claim_type}_2400_count",
                )
                st.session_state.edi_service_line_count = n_lines
                for i in range(n_lines):
                    st.markdown(f"**Service line {i + 1}**")
                    for seg in loop_def.get("segments", []):
                        for el in seg.get("elements", []):
                            key = f"edi_{claim_type}_2400_{i}_{el['id']}"
                            _render_field_with_error(claim_type, loop_id, el, key, index=i)
            else:
                for seg in loop_def.get("segments", []):
                    st.markdown(f"*{seg['name']}*")
                    for el in seg.get("elements", []):
                        key = f"edi_{claim_type}_{loop_id}_{el['id']}"
                        _render_field_with_error(claim_type, loop_id, el, key)

    # 3. Generate EDI file from user inputs
    st.markdown("---")
    if st.button("**Create EDI file**", type="primary", use_container_width=True):
        form_data = _collect_form_data(claim_type)
        with st.spinner("Creating EDI file..."):
            result = generate_837_file(claim_type, form_data)
        if result["success"]:
            st.session_state.pop("edi_error_keys", None)
            st.success(result["message"])
            if result.get("errors"):
                for err in result["errors"]:
                    st.warning(err)
            file_path = result.get("file_path")
            file_name = result.get("file_name")
            if file_path and Path(file_path).exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                st.download_button(
                    "Download EDI file",
                    content,
                    file_name=file_name,
                    mime="application/octet-stream",
                    key="edi_download_btn",
                )
        else:
            errors = result.get("errors", [])
            st.session_state["edi_error_keys"] = _parse_error_keys(claim_type, errors)
            st.error(result["message"])
            for err in errors:
                st.warning(err)
            st.rerun()


if __name__ == "__main__":
    main()
