REVIEW_WINDOW = {
    "start": "2026-08-18",
    "end": "2026-08-24",
    "label": "18–24 Aug 2026",
}

CASES = [
    {
        "id": "mbi-chen",
        "sequence": 1,
        "title": "Gut translocation, not the line",
        "hook": "Four-day neutropenic nadir. E. coli in paired bottles. ΔTTP of 12 minutes.",
        "whyItMatters": (
            "Without MBI logic this event hits the CLABSI SIR. The child is profoundly "
            "neutropenic after induction — the organism came through mucosa, not the Broviac. "
            "Counting it punishes oncology care the hospital cannot prevent, and pulling the "
            "line would strand her without access at the worst possible moment."
        ),
        "patient": {
            "id": "p-chen",
            "mrn": "00821456",
            "name": "Maya Chen",
            "ageYears": 8,
            "sex": "F",
            "unit": "Peds Oncology 4B",
            "service": "Pediatric hematology-oncology",
            "diagnosis": "B-ALL, day 12 of induction",
        },
        "line": {
            "type": "Tunneled Broviac (double lumen)",
            "placedAt": "2026-07-08",
            "firstAccessedInpatientAt": "2026-07-08",
            "firstAccessLocation": "Peds Oncology 4B",
            "inPlace": True,
        },
        "bloodCultures": [
            {
                "id": "bc-chen-c",
                "drawnAt": "2026-08-22T06:14:00-05:00",
                "source": "central",
                "organism": "Escherichia coli",
                "organismKey": "escherichia-coli",
                "timeToPositivityHours": 11.2,
            },
            {
                "id": "bc-chen-p",
                "drawnAt": "2026-08-22T06:16:00-05:00",
                "source": "peripheral",
                "organism": "Escherichia coli",
                "organismKey": "escherichia-coli",
                "timeToPositivityHours": 11.4,
            },
        ],
        "extraVascularCultures": [],
        "ancSeries": [
            {"at": "2026-08-19T05:40:00-05:00", "anc": 120},
            {"at": "2026-08-20T05:35:00-05:00", "anc": 80},
            {"at": "2026-08-21T05:50:00-05:00", "anc": 40},
            {"at": "2026-08-22T05:42:00-05:00", "anc": 30},
            {"at": "2026-08-23T05:38:00-05:00", "anc": 90},
            {"at": "2026-08-24T05:44:00-05:00", "anc": 210},
        ],
        "symptoms": [
            {"at": "2026-08-22T05:10:00-05:00", "type": "fever", "value": "38.4°C"},
        ],
        "expected": {
            "surveillanceLabel": "MBI-LCBI",
            "lcbiType": "LCBI-1",
            "mbiType": "MBI-LCBI-1",
            "countsInSir": False,
            "nhsNReportable": True,
            "bedsideStatus": "biofilm-not-supported",
            "deltaTtpMinutes": 12,
            "salvageEligible": True,
        },
    },
    {
        "id": "clabsi-reyes",
        "sequence": 2,
        "title": "True line biofilm",
        "hook": "PICC day 36. Paired S. epidermidis. Central bottle flagged 160 minutes first.",
        "whyItMatters": (
            "This is the event quality programs exist to catch. A skin commensal in two "
            "specimens, a long-dwell PICC, and a ΔTTP well above two hours — the line is "
            "the source. The workbench does not soften it. It tells the team to pull."
        ),
        "patient": {
            "id": "p-reyes",
            "mrn": "00819302",
            "name": "Jonah Reyes",
            "ageYears": 4,
            "sex": "M",
            "unit": "PICU 1",
            "service": "Pediatric critical care",
            "diagnosis": "Short-gut syndrome on home TPN",
        },
        "line": {
            "type": "PICC (3 Fr, single lumen)",
            "placedAt": "2026-07-16",
            "firstAccessedInpatientAt": "2026-07-16",
            "firstAccessLocation": "PICU 1",
            "inPlace": True,
        },
        "bloodCultures": [
            {
                "id": "bc-reyes-c",
                "drawnAt": "2026-08-20T09:04:00-05:00",
                "source": "central",
                "organism": "Staphylococcus epidermidis",
                "organismKey": "staphylococcus-epidermidis",
                "timeToPositivityHours": 8.2,
            },
            {
                "id": "bc-reyes-p",
                "drawnAt": "2026-08-20T09:06:00-05:00",
                "source": "peripheral",
                "organism": "Staphylococcus epidermidis",
                "organismKey": "staphylococcus-epidermidis",
                "timeToPositivityHours": 10.87,
            },
        ],
        "extraVascularCultures": [],
        "ancSeries": [
            {"at": "2026-08-18T06:00:00-05:00", "anc": 4100},
            {"at": "2026-08-20T06:10:00-05:00", "anc": 3200},
            {"at": "2026-08-22T06:05:00-05:00", "anc": 3600},
        ],
        "symptoms": [
            {"at": "2026-08-20T08:40:00-05:00", "type": "fever", "value": "38.6°C"},
        ],
        "expected": {
            "surveillanceLabel": "Primary CLABSI",
            "lcbiType": "LCBI-2",
            "mbiType": None,
            "countsInSir": True,
            "nhsNReportable": True,
            "bedsideStatus": "biofilm-supported",
            "deltaTtpMinutes": 160,
            "salvageEligible": False,
        },
    },
    {
        "id": "secondary-haddad",
        "sequence": 3,
        "title": "Pulmonary spillover",
        "hook": "CF flare. Sputum and blood grow the same Pseudomonas inside the SBAP.",
        "whyItMatters": (
            "A port in a cystic fibrosis patient is a lifeline. The lung is the source — "
            "sputum two days earlier, new infiltrate, identical organism in blood. Calling "
            "this a CLABSI inflates the SIR and tempts the team to explant a port they should treat through."
        ),
        "patient": {
            "id": "p-haddad",
            "mrn": "00798811",
            "name": "Amira Haddad",
            "ageYears": 14,
            "sex": "F",
            "unit": "Pulmonary 3W",
            "service": "Pediatric pulmonology",
            "diagnosis": "Cystic fibrosis, acute pulmonary exacerbation",
        },
        "line": {
            "type": "Port-a-cath",
            "placedAt": "2026-04-22",
            "firstAccessedInpatientAt": "2026-08-16",
            "firstAccessLocation": "Pulmonary 3W",
            "inPlace": True,
        },
        "bloodCultures": [
            {
                "id": "bc-haddad-c",
                "drawnAt": "2026-08-20T14:22:00-05:00",
                "source": "central",
                "organism": "Pseudomonas aeruginosa",
                "organismKey": "pseudomonas-aeruginosa",
                "timeToPositivityHours": 9.1,
            },
            {
                "id": "bc-haddad-p",
                "drawnAt": "2026-08-20T14:24:00-05:00",
                "source": "peripheral",
                "organism": "Pseudomonas aeruginosa",
                "organismKey": "pseudomonas-aeruginosa",
                "timeToPositivityHours": 9.4,
            },
        ],
        "extraVascularCultures": [
            {
                "id": "ev-haddad-sputum",
                "drawnAt": "2026-08-18T11:05:00-05:00",
                "site": "sputum",
                "siteLabel": "Expectorated sputum",
                "organism": "Pseudomonas aeruginosa",
                "organismKey": "pseudomonas-aeruginosa",
                "nhsNSite": "PNEU",
            },
        ],
        "ancSeries": [
            {"at": "2026-08-18T06:20:00-05:00", "anc": 7800},
            {"at": "2026-08-20T06:15:00-05:00", "anc": 9100},
        ],
        "symptoms": [
            {"at": "2026-08-20T13:50:00-05:00", "type": "fever", "value": "38.2°C"},
        ],
        "siteSpecificInfection": {
            "site": "PNEU",
            "criteriaMet": True,
            "note": "Acute CF exacerbation with new infiltrate on 19 Aug CT; sputum isolate required to close PNEU, blood is a matching secondary.",
        },
        "imagingNotes": "CT chest 19 Aug 2026: new right-lower-lobe infiltrate versus prior.",
        "expected": {
            "surveillanceLabel": "Secondary BSI",
            "lcbiType": "LCBI-1",
            "mbiType": None,
            "countsInSir": False,
            "nhsNReportable": True,
            "bedsideStatus": "biofilm-not-supported",
            "deltaTtpMinutes": 18,
            "salvageEligible": True,
        },
    },
    {
        "id": "gap-park",
        "sequence": 4,
        "title": "Surveillance complete, bedside blocked",
        "hook": "S. aureus from the Hickman only. No peripheral set. ΔTTP unknown.",
        "whyItMatters": (
            "The reporting engine can still classify this as a primary CLABSI — S. aureus is a "
            "recognized pathogen. The clinical engine cannot. Without a paired peripheral culture, "
            "extraction is a guess. The Gaps card stops the reflex pull and sends nursing back for the missing set."
        ),
        "patient": {
            "id": "p-park",
            "mrn": "00825019",
            "name": "Leo Park",
            "ageYears": 6,
            "sex": "M",
            "unit": "Hem/Onc 4A",
            "service": "Pediatric oncology",
            "diagnosis": "Relapsed neuroblastoma",
        },
        "line": {
            "type": "Hickman (double lumen)",
            "placedAt": "2026-08-02",
            "firstAccessedInpatientAt": "2026-08-02",
            "firstAccessLocation": "Hem/Onc 4A",
            "inPlace": True,
        },
        "bloodCultures": [
            {
                "id": "bc-park-c",
                "drawnAt": "2026-08-23T16:48:00-05:00",
                "source": "central",
                "organism": "Staphylococcus aureus",
                "organismKey": "staphylococcus-aureus",
                "timeToPositivityHours": 7.4,
            },
        ],
        "extraVascularCultures": [],
        "ancSeries": [
            {"at": "2026-08-21T06:00:00-05:00", "anc": 2100},
            {"at": "2026-08-23T06:12:00-05:00", "anc": 1800},
        ],
        "symptoms": [
            {"at": "2026-08-23T15:20:00-05:00", "type": "fever", "value": "39.1°C"},
        ],
        "expected": {
            "surveillanceLabel": "Primary CLABSI",
            "lcbiType": "LCBI-1",
            "mbiType": None,
            "countsInSir": True,
            "nhsNReportable": True,
            "bedsideStatus": "missing-data",
            "deltaTtpMinutes": None,
            "salvageEligible": False,
        },
    },
    {
        "id": "contaminant-alvarez",
        "sequence": 5,
        "title": "One bottle, no symptoms",
        "hook": "Single S. epidermidis from the Broviac. Afebrile. Nothing else grows.",
        "whyItMatters": (
            "A naive dashboard would fire a CLABSI alert. NHSN would not. One commensal bottle "
            "without fever, chills, or hypotension is a contaminant. Suppressing the alert protects "
            "the SIR and keeps the team from treating a lab accident as an infection."
        ),
        "patient": {
            "id": "p-alvarez",
            "mrn": "00817644",
            "name": "Sofia Alvarez",
            "ageYears": 11,
            "sex": "F",
            "unit": "Surgical 2E",
            "service": "Pediatric surgery",
            "diagnosis": "Postoperative day 6, bowel resection",
        },
        "line": {
            "type": "Tunneled Broviac",
            "placedAt": "2026-08-10",
            "firstAccessedInpatientAt": "2026-08-10",
            "firstAccessLocation": "OR / Surgical 2E",
            "inPlace": True,
        },
        "bloodCultures": [
            {
                "id": "bc-alvarez-c",
                "drawnAt": "2026-08-21T10:12:00-05:00",
                "source": "central",
                "organism": "Staphylococcus epidermidis",
                "organismKey": "staphylococcus-epidermidis",
                "timeToPositivityHours": 18.6,
            },
        ],
        "extraVascularCultures": [],
        "ancSeries": [
            {"at": "2026-08-20T06:00:00-05:00", "anc": 5400},
            {"at": "2026-08-22T06:00:00-05:00", "anc": 6100},
        ],
        "symptoms": [],
        "expected": {
            "surveillanceLabel": "Contaminant",
            "lcbiType": None,
            "mbiType": None,
            "countsInSir": False,
            "nhsNReportable": False,
            "bedsideStatus": "missing-data",
            "deltaTtpMinutes": None,
            "salvageEligible": False,
        },
    },
]


def get_case(case_id: str):
    return next((c for c in CASES if c["id"] == case_id), None)
