"""
EDI 837P and 837I Loop/Segment Schemas (HIPAA 5010)
Defines loops and segments for UI forms and EDI generation.
Reference: ASC X12N 005010X222A1 (837P), 005010X223A2 (837I)
"""


def _el(edi_id: str, label: str, required: bool = False, help_text: str = "") -> dict:
    return {"id": edi_id, "label": label, "required": required, "help": help_text}


# ─── 837P (Professional) Loops ─────────────────────────────────────────────────

LOOPS_837P = [
    {
        "loop_id": "1000A",
        "name": "Submitter Information",
        "description": "Identifies the entity submitting the claim.",
        "segments": [
            {
                "seg_id": "NM1",
                "name": "Submitter Name",
                "elements": [
                    _el("NM101", "Entity Identifier (41=Submitter)", True, "Use 41"),
                    _el("NM102", "Entity Type (1=Person, 2=Non-Person)", True, "1 or 2"),
                    _el("NM103", "Submitter Last/Org Name", True, ""),
                    _el("NM104", "Submitter First Name", False, ""),
                    _el("NM108", "ID Code Qualifier (46=EIN)", False, "46 for EIN"),
                    _el("NM109", "Submitter EIN/NPI", False, "9-digit EIN"),
                ],
            },
            {
                "seg_id": "PER",
                "name": "Submitter Contact",
                "elements": [
                    _el("PER01", "Contact Function (IC=Info Contact)", True, "IC"),
                    _el("PER02", "Contact Name", False, ""),
                    _el("PER03", "Comm Qualifier (TE=Telephone)", False, "TE"),
                    _el("PER04", "Contact Number", False, ""),
                ],
            },
        ],
    },
    {
        "loop_id": "1000B",
        "name": "Receiver Information",
        "description": "Identifies the receiver (payer/clearinghouse).",
        "segments": [
            {
                "seg_id": "NM1",
                "name": "Receiver Name",
                "elements": [
                    _el("NM101", "Entity Identifier (40=Receiver)", True, "40"),
                    _el("NM102", "Entity Type (1=Person, 2=Non-Person)", True, "2"),
                    _el("NM103", "Receiver Name", True, "Payer or clearinghouse name"),
                    _el("NM108", "ID Code Qualifier (46=EIN)", False, "46"),
                    _el("NM109", "Receiver EIN", False, ""),
                ],
            },
        ],
    },
    {
        "loop_id": "2000A",
        "name": "Billing Provider Hierarchy",
        "description": "Billing provider and pay-to provider information.",
        "segments": [
            {
                "seg_id": "HL",
                "name": "Hierarchical Level",
                "elements": [
                    _el("HL01", "Parent ID", True, "0 for top level"),
                    _el("HL02", "ID", True, "1"),
                    _el("HL03", "Level (20=Billing Provider)", True, "20"),
                ],
            },
            {
                "seg_id": "NM1",
                "name": "Billing Provider Name",
                "elements": [
                    _el("NM101", "Entity Identifier (85=Billing Provider)", True, "85"),
                    _el("NM102", "Entity Type", True, "1 or 2"),
                    _el("NM103", "Provider Last/Org Name", True, ""),
                    _el("NM104", "Provider First Name", False, ""),
                    _el("NM108", "ID Qualifier (XX=NPI)", True, "XX"),
                    _el("NM109", "National Provider Identifier (NPI)", True, "10 digits"),
                ],
            },
            {
                "seg_id": "N3",
                "name": "Provider Address",
                "elements": [
                    _el("N301", "Address Line 1", True, ""),
                    _el("N302", "Address Line 2", False, ""),
                ],
            },
            {
                "seg_id": "N4",
                "name": "Provider City/State/ZIP",
                "elements": [
                    _el("N401", "City", True, ""),
                    _el("N402", "State (2-letter)", True, ""),
                    _el("N403", "ZIP", True, "5 or 9 digits"),
                ],
            },
        ],
    },
    {
        "loop_id": "2000B",
        "name": "Subscriber Information",
        "description": "Subscriber (insured) demographic and insurance info.",
        "segments": [
            {
                "seg_id": "HL",
                "name": "Hierarchical Level",
                "elements": [
                    _el("HL01", "Parent ID", True, "1"),
                    _el("HL02", "ID", True, "2"),
                    _el("HL03", "Level (22=Subscriber)", True, "22"),
                ],
            },
            {
                "seg_id": "SBR",
                "name": "Subscriber Info",
                "elements": [
                    _el("SBR01", "Payer Responsibility (P=Primary)", True, "P, S, or T"),
                    _el("SBR02", "Individual Relationship (18=Self)", False, "18=Self"),
                    _el("SBR03", "Group Policy Number", False, ""),
                    _el("SBR09", "Claim Filing Code", True, "e.g. 11=Other, 12=Medicare"),
                ],
            },
            {
                "seg_id": "NM1",
                "name": "Subscriber Name",
                "elements": [
                    _el("NM101", "Entity Identifier (IL=Insured)", True, "IL"),
                    _el("NM102", "Entity Type", True, "1 or 2"),
                    _el("NM103", "Subscriber Last Name", True, ""),
                    _el("NM104", "Subscriber First Name", False, ""),
                    _el("NM108", "ID Qualifier (MI=Member ID)", False, "MI"),
                    _el("NM109", "Subscriber ID (Member ID)", True, ""),
                ],
            },
            {
                "seg_id": "N3",
                "name": "Subscriber Address",
                "elements": [
                    _el("N301", "Address Line 1", False, ""),
                    _el("N302", "Address Line 2", False, ""),
                ],
            },
            {
                "seg_id": "N4",
                "name": "Subscriber City/State/ZIP",
                "elements": [
                    _el("N401", "City", False, ""),
                    _el("N402", "State", False, ""),
                    _el("N403", "ZIP", False, ""),
                ],
            },
            {
                "seg_id": "DMG",
                "name": "Subscriber Demographics",
                "elements": [
                    _el("DMG01", "Date Time Qualifier (D8=Date)", True, "D8"),
                    _el("DMG02", "Date of Birth (YYYYMMDD)", True, ""),
                    _el("DMG03", "Gender (F/M/U)", False, "F, M, or U"),
                ],
            },
        ],
    },
    {
        "loop_id": "2000C",
        "name": "Patient Information",
        "description": "Patient (if different from subscriber).",
        "segments": [
            {
                "seg_id": "HL",
                "name": "Hierarchical Level",
                "elements": [
                    _el("HL01", "Parent ID", True, "2"),
                    _el("HL02", "ID", True, "3"),
                    _el("HL03", "Level (23=Dependent)", True, "23"),
                ],
            },
            {
                "seg_id": "PAT",
                "name": "Patient Info",
                "elements": [
                    _el("PAT01", "Individual Relationship (01=Spouse, 19=Child)", False, "01, 19, 20, etc."),
                ],
            },
            {
                "seg_id": "NM1",
                "name": "Patient Name",
                "elements": [
                    _el("NM101", "Entity Identifier (QC=Patient)", True, "QC"),
                    _el("NM102", "Entity Type", True, "1"),
                    _el("NM103", "Patient Last Name", True, ""),
                    _el("NM104", "Patient First Name", False, ""),
                    _el("NM108", "ID Qualifier", False, ""),
                    _el("NM109", "Patient ID", False, ""),
                ],
            },
            {
                "seg_id": "DMG",
                "name": "Patient Demographics",
                "elements": [
                    _el("DMG01", "Date Time Qualifier (D8)", True, "D8"),
                    _el("DMG02", "Date of Birth (YYYYMMDD)", True, ""),
                    _el("DMG03", "Gender (F/M/U)", False, ""),
                ],
            },
        ],
    },
    {
        "loop_id": "2300",
        "name": "Claim Information",
        "description": "Claim-level data (dates, diagnosis, charges).",
        "segments": [
            {
                "seg_id": "CLM",
                "name": "Claim",
                "elements": [
                    _el("CLM01", "Patient Control Number", True, "Unique claim ID"),
                    _el("CLM02", "Total Claim Charge Amount", True, "Total charges"),
                    _el("CLM05", "Place of Service Code", True, "2-digit POS code"),
                    _el("CLM06", "Claim Type (B=Medical, A=Accident)", False, "B or A"),
                    _el("CLM09", "Claim Filing Code", False, "11, 12, etc."),
                    _el("CLM11", "Provider or Supplier Signature (Y/N)", False, "Y"),
                ],
            },
            {
                "seg_id": "DTP",
                "name": "Date of Service",
                "elements": [
                    _el("DTP01", "Date Qualifier (431=Onset)", True, "431 or 472"),
                    _el("DTP02", "Date Format (D8=YYYYMMDD)", True, "D8"),
                    _el("DTP03", "Service Date (YYYYMMDD)", True, ""),
                ],
            },
            {
                "seg_id": "HI",
                "name": "Diagnosis Codes",
                "elements": [
                    _el("HI01", "Code List Qualifier (ABK=ICD-10)", True, "ABK, BF=ICD-9"),
                    _el("HI02", "Diagnosis Code 1", True, "ICD-10 code"),
                    _el("HI03", "Code 2", False, ""),
                    _el("HI04", "Code 3", False, ""),
                    _el("HI05", "Code 4", False, ""),
                ],
            },
        ],
    },
    {
        "loop_id": "2320",
        "name": "COB (Coordination of Benefits)",
        "description": "Optional. Other payer / coordination of benefits information. Include only when COB applies.",
        "segments": [
            {
                "seg_id": "SBR",
                "name": "Other Subscriber Information",
                "elements": [
                    _el("SBR01", "Payer Responsibility (P=Primary, S=Secondary, T=Tertiary)", False, "P, S, or T"),
                    _el("SBR02", "Individual Relationship Code (18=Self, 01=Spouse)", False, ""),
                    _el("SBR03", "Group Policy Number", False, ""),
                    _el("SBR04", "Group or Policy Number", False, ""),
                    _el("SBR09", "Claim Filing Code (11=Other, 12=Medicare)", False, "11, 12, etc."),
                ],
            },
            {
                "seg_id": "AMT",
                "name": "COB Amount (e.g. Paid / Allowed)",
                "elements": [
                    _el("AMT01", "Amount Qualifier (D=Amount Paid, B6=Allowed)", False, "D or B6"),
                    _el("AMT02", "Amount", False, "Numeric amount"),
                ],
            },
            {
                "seg_id": "OI",
                "name": "Other Insurance Coverage",
                "elements": [
                    _el("OI01", "Benefits Assignment (Y/N)", False, "Y or N"),
                    _el("OI02", "Release of Information (Y/N)", False, "Y or N"),
                    _el("OI03", "Provider Accept Assignment (Y/N)", False, "Y or N"),
                ],
            },
            {
                "seg_id": "REF",
                "name": "Other Payer Reference",
                "elements": [
                    _el("REF01", "Reference Qualifier (1L=Group, 17=Member ID)", False, "1L or 17"),
                    _el("REF02", "Reference Identifier", False, "Other payer ID or group number"),
                ],
            },
        ],
    },
    {
        "loop_id": "2400",
        "name": "Service Line",
        "description": "Line-level service and charge (repeat for each line).",
        "repeatable": True,
        "segments": [
            {
                "seg_id": "LX",
                "name": "Service Line Number",
                "elements": [
                    _el("LX01", "Assigned Number", True, "1, 2, 3..."),
                ],
            },
            {
                "seg_id": "SV1",
                "name": "Professional Service",
                "elements": [
                    _el("SV101", "Product/Service ID Qualifier (HC=HCPCS)", True, "HC"),
                    _el("SV102", "Procedure Code (HCPCS/CPT)", True, ""),
                    _el("SV103", "Line Charge Amount", True, ""),
                    _el("SV104", "Unit or Basis (UN=Unit)", True, "UN"),
                    _el("SV105", "Service Unit Count", True, "1 or quantity"),
                ],
            },
            {
                "seg_id": "DTP",
                "name": "Service Date",
                "elements": [
                    _el("DTP01", "Date Qualifier (472=Service)", True, "472"),
                    _el("DTP02", "Date Format (D8)", True, "D8"),
                    _el("DTP03", "Date (YYYYMMDD)", True, ""),
                ],
            },
        ],
    },
]

# ─── 837I (Institutional) Loops ───────────────────────────────────────────────

LOOPS_837I = [
    {
        "loop_id": "1000A",
        "name": "Submitter Information",
        "description": "Identifies the entity submitting the claim.",
        "segments": [
            {
                "seg_id": "NM1",
                "name": "Submitter Name",
                "elements": [
                    _el("NM101", "Entity Identifier (41=Submitter)", True, "41"),
                    _el("NM102", "Entity Type (1=Person, 2=Non-Person)", True, "1 or 2"),
                    _el("NM103", "Submitter Last/Org Name", True, ""),
                    _el("NM104", "Submitter First Name", False, ""),
                    _el("NM108", "ID Code Qualifier (46=EIN)", False, "46"),
                    _el("NM109", "Submitter EIN", False, ""),
                ],
            },
            {
                "seg_id": "PER",
                "name": "Submitter Contact",
                "elements": [
                    _el("PER01", "Contact Function (IC)", True, "IC"),
                    _el("PER02", "Contact Name", False, ""),
                    _el("PER03", "Comm Qualifier (TE)", False, "TE"),
                    _el("PER04", "Contact Number", False, ""),
                ],
            },
        ],
    },
    {
        "loop_id": "1000B",
        "name": "Receiver Information",
        "description": "Identifies the receiver (payer).",
        "segments": [
            {
                "seg_id": "NM1",
                "name": "Receiver Name",
                "elements": [
                    _el("NM101", "Entity Identifier (40=Receiver)", True, "40"),
                    _el("NM102", "Entity Type", True, "2"),
                    _el("NM103", "Receiver Name", True, ""),
                    _el("NM108", "ID Code Qualifier", False, "46"),
                    _el("NM109", "Receiver EIN", False, ""),
                ],
            },
        ],
    },
    {
        "loop_id": "2000A",
        "name": "Billing Provider",
        "description": "Billing provider hierarchy.",
        "segments": [
            {
                "seg_id": "HL",
                "name": "Hierarchical Level",
                "elements": [
                    _el("HL01", "Parent ID", True, "0"),
                    _el("HL02", "ID", True, "1"),
                    _el("HL03", "Level (20=Billing Provider)", True, "20"),
                ],
            },
            {
                "seg_id": "NM1",
                "name": "Billing Provider Name",
                "elements": [
                    _el("NM101", "Entity Identifier (85)", True, "85"),
                    _el("NM102", "Entity Type", True, "2"),
                    _el("NM103", "Provider Name", True, ""),
                    _el("NM108", "ID Qualifier (XX=NPI)", True, "XX"),
                    _el("NM109", "NPI (10 digits)", True, ""),
                ],
            },
            {
                "seg_id": "N3",
                "name": "Provider Address",
                "elements": [
                    _el("N301", "Address Line 1", True, ""),
                    _el("N302", "Address Line 2", False, ""),
                ],
            },
            {
                "seg_id": "N4",
                "name": "Provider City/State/ZIP",
                "elements": [
                    _el("N401", "City", True, ""),
                    _el("N402", "State", True, ""),
                    _el("N403", "ZIP", True, ""),
                ],
            },
        ],
    },
    {
        "loop_id": "2000B",
        "name": "Subscriber Information",
        "description": "Subscriber (insured) information.",
        "segments": [
            {
                "seg_id": "HL",
                "name": "Hierarchical Level",
                "elements": [
                    _el("HL01", "Parent ID", True, "1"),
                    _el("HL02", "ID", True, "2"),
                    _el("HL03", "Level (22=Subscriber)", True, "22"),
                ],
            },
            {
                "seg_id": "SBR",
                "name": "Subscriber Info",
                "elements": [
                    _el("SBR01", "Payer Responsibility (P/S/T)", True, "P"),
                    _el("SBR02", "Individual Relationship", False, "18=Self"),
                    _el("SBR03", "Group Policy Number", False, ""),
                    _el("SBR09", "Claim Filing Code", True, "11, 12, etc."),
                ],
            },
            {
                "seg_id": "NM1",
                "name": "Subscriber Name",
                "elements": [
                    _el("NM101", "Entity Identifier (IL)", True, "IL"),
                    _el("NM102", "Entity Type", True, "1 or 2"),
                    _el("NM103", "Subscriber Last Name", True, ""),
                    _el("NM104", "Subscriber First Name", False, ""),
                    _el("NM108", "ID Qualifier (MI)", False, "MI"),
                    _el("NM109", "Subscriber ID", True, ""),
                ],
            },
            {
                "seg_id": "N3",
                "name": "Subscriber Address",
                "elements": [
                    _el("N301", "Address Line 1", False, ""),
                    _el("N302", "Address Line 2", False, ""),
                ],
            },
            {
                "seg_id": "N4",
                "name": "Subscriber City/State/ZIP",
                "elements": [
                    _el("N401", "City", False, ""),
                    _el("N402", "State", False, ""),
                    _el("N403", "ZIP", False, ""),
                ],
            },
            {
                "seg_id": "DMG",
                "name": "Subscriber Demographics",
                "elements": [
                    _el("DMG01", "Date Time Qualifier (D8)", True, "D8"),
                    _el("DMG02", "Date of Birth (YYYYMMDD)", True, ""),
                    _el("DMG03", "Gender (F/M/U)", False, ""),
                ],
            },
        ],
    },
    {
        "loop_id": "2000C",
        "name": "Patient Information",
        "description": "Patient demographic information.",
        "segments": [
            {
                "seg_id": "HL",
                "name": "Hierarchical Level",
                "elements": [
                    _el("HL01", "Parent ID", True, "2"),
                    _el("HL02", "ID", True, "3"),
                    _el("HL03", "Level (23=Patient)", True, "23"),
                ],
            },
            {
                "seg_id": "PAT",
                "name": "Patient Info",
                "elements": [
                    _el("PAT01", "Individual Relationship", False, "01, 19, 20"),
                ],
            },
            {
                "seg_id": "NM1",
                "name": "Patient Name",
                "elements": [
                    _el("NM101", "Entity Identifier (QC)", True, "QC"),
                    _el("NM102", "Entity Type", True, "1"),
                    _el("NM103", "Patient Last Name", True, ""),
                    _el("NM104", "Patient First Name", False, ""),
                    _el("NM108", "ID Qualifier", False, ""),
                    _el("NM109", "Patient ID", False, ""),
                ],
            },
            {
                "seg_id": "DMG",
                "name": "Patient Demographics",
                "elements": [
                    _el("DMG01", "Date Time Qualifier (D8)", True, "D8"),
                    _el("DMG02", "Date of Birth (YYYYMMDD)", True, ""),
                    _el("DMG03", "Gender (F/M/U)", False, ""),
                ],
            },
        ],
    },
    {
        "loop_id": "2300",
        "name": "Claim Information (Institutional)",
        "description": "Claim-level data including type of bill and statement dates.",
        "segments": [
            {
                "seg_id": "CLM",
                "name": "Claim",
                "elements": [
                    _el("CLM01", "Patient Control Number", True, ""),
                    _el("CLM02", "Total Claim Charge Amount", True, ""),
                    _el("CLM05", "Type of Bill (TOB)", True, "3-digit (e.g. 011x)"),
                    _el("CLM06", "Claim Type", False, "A or B"),
                    _el("CLM07", "Assignment (Y/N)", False, "Y"),
                    _el("CLM08", "Benefits Assignment (Y/N)", False, "Y"),
                    _el("CLM11", "Provider Signature (Y/N)", False, "Y"),
                ],
            },
            {
                "seg_id": "DTP",
                "name": "Statement Date",
                "elements": [
                    _el("DTP01", "Date Qualifier (434=Admission)", True, "434 or 435"),
                    _el("DTP02", "Date Format (D8)", True, "D8"),
                    _el("DTP03", "Date (YYYYMMDD)", True, ""),
                ],
            },
            {
                "seg_id": "DTP",
                "name": "Discharge Date",
                "elements": [
                    _el("DTP01_2", "Date Qualifier (096=Discharge)", True, "096"),
                    _el("DTP02_2", "Date Format (D8)", True, "D8"),
                    _el("DTP03_2", "Discharge Date (YYYYMMDD)", True, ""),
                ],
            },
            {
                "seg_id": "HI",
                "name": "Diagnosis Codes",
                "elements": [
                    _el("HI01", "Code List Qualifier (ABK=ICD-10)", True, "ABK or BF"),
                    _el("HI02", "Diagnosis Code 1", True, ""),
                    _el("HI03", "Code 2", False, ""),
                    _el("HI04", "Code 3", False, ""),
                    _el("HI05", "Code 4", False, ""),
                ],
            },
        ],
    },
    {
        "loop_id": "2320",
        "name": "COB (Coordination of Benefits)",
        "description": "Optional. Other payer / coordination of benefits information. Include only when COB applies.",
        "segments": [
            {
                "seg_id": "SBR",
                "name": "Other Subscriber Information",
                "elements": [
                    _el("SBR01", "Payer Responsibility (P=Primary, S=Secondary, T=Tertiary)", False, "P, S, or T"),
                    _el("SBR02", "Individual Relationship Code (18=Self, 01=Spouse)", False, ""),
                    _el("SBR03", "Group Policy Number", False, ""),
                    _el("SBR04", "Group or Policy Number", False, ""),
                    _el("SBR09", "Claim Filing Code (11=Other, 12=Medicare)", False, "11, 12, etc."),
                ],
            },
            {
                "seg_id": "AMT",
                "name": "COB Amount (e.g. Paid / Allowed)",
                "elements": [
                    _el("AMT01", "Amount Qualifier (D=Amount Paid, B6=Allowed)", False, "D or B6"),
                    _el("AMT02", "Amount", False, "Numeric amount"),
                ],
            },
            {
                "seg_id": "OI",
                "name": "Other Insurance Coverage",
                "elements": [
                    _el("OI01", "Benefits Assignment (Y/N)", False, "Y or N"),
                    _el("OI02", "Release of Information (Y/N)", False, "Y or N"),
                    _el("OI03", "Provider Accept Assignment (Y/N)", False, "Y or N"),
                ],
            },
            {
                "seg_id": "REF",
                "name": "Other Payer Reference",
                "elements": [
                    _el("REF01", "Reference Qualifier (1L=Group, 17=Member ID)", False, "1L or 17"),
                    _el("REF02", "Reference Identifier", False, "Other payer ID or group number"),
                ],
            },
        ],
    },
    {
        "loop_id": "2400",
        "name": "Service Line (Institutional)",
        "description": "Revenue code and charge per line (repeatable).",
        "repeatable": True,
        "segments": [
            {
                "seg_id": "LX",
                "name": "Service Line Number",
                "elements": [
                    _el("LX01", "Assigned Number", True, "1, 2, 3..."),
                ],
            },
            {
                "seg_id": "SV2",
                "name": "Institutional Service",
                "elements": [
                    _el("SV201", "Revenue Code", True, "3-digit revenue code"),
                    _el("SV202", "Line Charge Amount", True, ""),
                    _el("SV203", "Unit or Basis (UN=Unit)", True, "UN"),
                    _el("SV204", "Service Unit Count", True, "1 or quantity"),
                ],
            },
            {
                "seg_id": "DTP",
                "name": "Service Date",
                "elements": [
                    _el("DTP01", "Date Qualifier (472)", True, "472"),
                    _el("DTP02", "Date Format (D8)", True, "D8"),
                    _el("DTP03", "Date (YYYYMMDD)", True, ""),
                ],
            },
        ],
    },
]


def get_loops(claim_type: str):
    """Return loop definitions for 837P or 837I."""
    if claim_type.upper() == "837P":
        return LOOPS_837P
    if claim_type.upper() == "837I":
        return LOOPS_837I
    raise ValueError("claim_type must be 837P or 837I")
