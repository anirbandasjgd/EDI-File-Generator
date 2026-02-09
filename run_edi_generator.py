#!/usr/bin/env python3
"""
Run EDI File Generator from the command line.
Usage (from project root Gen-AI-Dev-Course):
  python EDI_File_Generator/run_edi_generator.py
  python EDI_File_Generator/run_edi_generator.py 837P
  python EDI_File_Generator/run_edi_generator.py 837I
"""
import sys
from pathlib import Path

# Add project root so EDI_File_Generator can be imported when run from anywhere
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from EDI_File_Generator import generate_837_file


def sample_837p_data():
    """Minimal sample form data for 837P (Professional) claim."""
    return {
        "1000A": {"NM101": "41", "NM102": "2", "NM103": "Acme Corp", "PER01": "IC", "PER02": "Jane Doe"},
        "1000B": {"NM101": "40", "NM102": "2", "NM103": "Payer Inc"},
        "2000A": {
            "HL01": "0", "HL02": "1", "HL03": "20",
            "NM101": "85", "NM102": "2", "NM103": "Provider Org", "NM108": "XX", "NM109": "1234567890",
            "N301": "123 Main St", "N401": "Anytown", "N402": "TX", "N403": "75001",
        },
        "2000B": {
            "HL01": "1", "HL02": "2", "HL03": "22",
            "SBR01": "P", "SBR09": "11",
            "NM101": "IL", "NM102": "1", "NM103": "Doe", "NM104": "John", "NM109": "MEM001",
            "DMG01": "D8", "DMG02": "19800101", "DMG03": "M",
        },
        "2000C": {
            "HL01": "2", "HL02": "3", "HL03": "23",
            "NM101": "QC", "NM102": "1", "NM103": "Doe", "NM104": "Jane",
            "DMG01": "D8", "DMG02": "19900515",
        },
        "2300": {
            "CLM01": "CLM001", "CLM02": "150.00", "CLM05": "11",
            "DTP01": "431", "DTP02": "D8", "DTP03": "20260201",
            "HI01": "ABK", "HI02": "Z00.00",
        },
        "2400": [
            {"LX01": "1", "SV101": "HC", "SV102": "99213", "SV103": "150.00", "SV104": "UN", "SV105": "1",
             "DTP01": "472", "DTP02": "D8", "DTP03": "20260201"},
        ],
    }


def sample_837i_data():
    """Minimal sample form data for 837I (Institutional) claim."""
    data = sample_837p_data()
    data["2300"] = {
        "CLM01": "CLM001", "CLM02": "5000.00", "CLM05": "011", "CLM07": "Y", "CLM08": "Y",
        "DTP01": "434", "DTP02": "D8", "DTP03": "20260201",
        "DTP01_2": "096", "DTP02_2": "D8", "DTP03_2": "20260205",
        "HI01": "ABK", "HI02": "Z00.00",
    }
    data["2400"] = [
        {"LX01": "1", "SV201": "0250", "SV202": "5000.00", "SV203": "UN", "SV204": "1",
         "DTP01": "472", "DTP02": "D8", "DTP03": "20260201"},
    ]
    return data


def main():
    claim_type = "837P"
    if len(sys.argv) > 1:
        claim_type = sys.argv[1].upper()
        if claim_type not in ("837P", "837I"):
            print("Usage: python run_edi_generator.py [837P|837I]")
            sys.exit(1)

    form_data = sample_837i_data() if claim_type == "837I" else sample_837p_data()
    print(f"Generating {claim_type} EDI file...")
    result = generate_837_file(claim_type, form_data)

    if result["success"]:
        print("Success:", result["message"])
        print("File:", result["file_path"])
        if result.get("errors"):
            for e in result["errors"]:
                print("  Warning:", e)
    else:
        print("Error:", result["message"])
        for e in result.get("errors", []):
            print("  ", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
