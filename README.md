# EDI File Generator

Generates HIPAA-compliant **837P** (Professional) and **837I** (Institutional) health care claim EDI files from user-entered segment values.

## How to execute

### Option 1: Streamlit UI (recommended)

From project root (`Gen-AI-Dev-Course`):

```bash
# Optional: activate venv and install streamlit
source .venv/bin/activate
pip install streamlit

streamlit run EDI_File_Generator/app.py
```

Then in the UI: (1) select file type (837P or 837I), (2) enter segment values in each loop, (3) click **Create EDI file** and download.

### Option 2: Command line (sample data)

```bash
python EDI_File_Generator/run_edi_generator.py        # 837P sample
python EDI_File_Generator/run_edi_generator.py 837P
python EDI_File_Generator/run_edi_generator.py 837I
```

Generated files: **`edi_output/837P_YYYYMMDD_HHMMSS.edi`** (and 837I). See **SETUP.md** for full setup.

## Push to a new Git remote

This folder is its own Git repo. To push it to GitHub/GitLab as a new repo, see **PUSH.md**.

## Features

- **837P** – Professional (physician/ambulatory) claims per ASC X12N 005010X222A1  
- **837I** – Institutional (hospital/facility) claims per ASC X12N 005010X223A2  
- **HIPAA 5010** envelope (ISA/IEA, GS/GE, ST/SE, BHT) and delimiters  
- **SNIP2-style validation** – required elements and segment structure  
- **Per-loop UI** – one screen (expander) per loop for entering segment values  
- **Agent** – `generate_837_file(claim_type, form_data)` builds and saves the file  
- **File naming** – `837P_YYYYMMDD_HHMMSS.edi` or `837I_YYYYMMDD_HHMMSS.edi` in `edi_output/`

## Module layout

| File | Purpose |
|------|--------|
| `edi_schemas.py` | Loop/segment definitions for 837P and 837I (1000A, 1000B, 2000A, 2000B, 2000C, 2300, 2400) |
| `edi_generator.py` | Builds X12 837 content and runs SNIP2-style validation |
| `edi_agent.py` | Orchestrates generation and saves file with timestamped name |
| `edi_output/` | Generated `.edi` files (created automatically) |

## Usage from app

The main Streamlit app adds an **EDI Claims** page that:

1. Lets the user choose 837P or 837I.  
2. Shows one expander per loop with inputs for each segment element.  
3. On **Generate EDI File**, collects form data, calls `generate_837_file()`, and offers a download.

## Usage as a package

```python
from EDI_File_Generator import get_loops, generate_837_file

loops = get_loops("837P")  # or "837I"
form_data = {
    "1000A": {"NM101": "41", "NM102": "2", "NM103": "Acme", ...},
    "1000B": {...},
    # ...
    "2400": [{"LX01": "1", "SV101": "HC", "SV102": "99213", ...}],
}
result = generate_837_file("837P", form_data)
# result["success"], result["file_path"], result["file_name"], result["errors"]
```

Generated files are written to `EDI_File_Generator/edi_output/`.
