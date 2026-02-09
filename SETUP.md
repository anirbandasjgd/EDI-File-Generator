# EDI File Generator – Setup & Run

## Quick run: Streamlit UI

From the **project root** (`Gen-AI-Dev-Course`):

```bash
source .venv/bin/activate   # macOS/Linux (or .venv\Scripts\activate on Windows)
pip install streamlit       # only needed once

streamlit run EDI_File_Generator/app.py
```

In the UI: (1) **Select the type of file** (837P or 837I), (2) **Enter segment values** for each loop (expand each section), (3) Click **Create EDI file** and use the download button. Output is saved under **`EDI_File_Generator/edi_output/`** as `837P_YYYYMMDD_HHMMSS.edi` or `837I_YYYYMMDD_HHMMSS.edi`.

---

## Command line (sample data, no UI)

```bash
python EDI_File_Generator/run_edi_generator.py 837P
python EDI_File_Generator/run_edi_generator.py 837I
```

No `pip install` needed for the script (stdlib only).

---

## Option A: Run via Smart Office Assistant (Streamlit UI)

The EDI Claims UI runs inside the Streamlit app. Use the project root venv and the app’s requirements.

### 1. Create and activate virtual environment (project root)

```bash
# From Gen-AI-Dev-Course (project root)
python3 -m venv .venv

# Activate:
# macOS/Linux:
source .venv/bin/activate
# Windows (cmd):
# .venv\Scripts\activate.bat
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r Decrypt_AIMessaging/requirements.txt
# or from project root:
pip install -r requirements-edi-app.txt
```

### 3. Environment variables

```bash
# Copy template and edit with your values
cp .env.example .env
# Set at least OPENAI_API_KEY in .env for the app's NLU/chat features.
# EDI generation does not require API keys.
```

### 4. Run the app

```bash
# From project root (Gen-AI-Dev-Course)
streamlit run Decrypt_AIMessaging/app.py
```

Open **EDI Claims** in the sidebar to generate 837P/837I files.

---

## Option B: Use EDI_File_Generator as a library only

The EDI module has **no pip dependencies** (stdlib only).

```bash
# Optional: create a venv for a clean environment
python3 -m venv .venv
source .venv/bin/activate  # or Windows equivalent

# No pip install needed for EDI_File_Generator
```

```python
from EDI_File_Generator import get_loops, generate_837_file

form_data = {
    "1000A": {"NM101": "41", "NM102": "2", "NM103": "Acme", ...},
    # ...
}
result = generate_837_file("837P", form_data)
# Files are saved under EDI_File_Generator/edi_output/
```

When running from a different directory, ensure the project root is on `sys.path` so `EDI_File_Generator` can be imported.

---

## Generated files

- Path: **`EDI_File_Generator/edi_output/`**
- Names: **`837P_YYYYMMDD_HHMMSS.edi`**, **`837I_YYYYMMDD_HHMMSS.edi`**
