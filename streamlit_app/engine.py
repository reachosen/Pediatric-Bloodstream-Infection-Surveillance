from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

ORGANISMS = {
    "escherichia-coli": {
        "key": "escherichia-coli",
        "name": "Escherichia coli",
        "short": "E. coli",
        "class": "recognized-pathogen",
        "mbi": True,
    },
    "klebsiella-pneumoniae": {
        "key": "klebsiella-pneumoniae",
        "name": "Klebsiella pneumoniae",
        "short": "K. pneumoniae",
        "class": "recognized-pathogen",
        "mbi": True,
    },
    "enterococcus-faecium": {
        "key": "enterococcus-faecium",
        "name": "Enterococcus faecium",
        "short": "E. faecium",
        "class": "recognized-pathogen",
        "mbi": True,
    },
    "candida-albicans": {
        "key": "candida-albicans",
        "name": "Candida albicans",
        "short": "C. albicans",
        "class": "recognized-pathogen",
        "mbi": True,
    },
    "staphylococcus-aureus": {
        "key": "staphylococcus-aureus",
        "name": "Staphylococcus aureus",
        "short": "S. aureus",
        "class": "recognized-pathogen",
        "mbi": False,
    },
    "staphylococcus-epidermidis": {
        "key": "staphylococcus-epidermidis",
        "name": "Staphylococcus epidermidis",
        "short": "S. epidermidis",
        "class": "common-commensal",
        "mbi": False,
    },
    "pseudomonas-aeruginosa": {
        "key": "pseudomonas-aeruginosa",
        "name": "Pseudomonas aeruginosa",
        "short": "P. aeruginosa",
        "class": "recognized-pathogen",
        "mbi": False,
    },
}

IWP_RADIUS_DAYS = 3
RIT_DAYS = 14
NEUTROPENIA_THRESHOLD = 500
LINE_ELIGIBLE_AFTER_DAYS = 2
BIOFILM_MINUTES = 120
HSCT_WINDOW_DAYS = 365


def parse_iso(value: str) -> datetime:
    text = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        if len(text) >= 6 and text[-6] in "+-" and text[-3] == ":":
            text = text[:-3] + text[-2:]
        return datetime.fromisoformat(text)


def iso_day(dt: datetime) -> str:
    return dt.date().isoformat()


def day(iso: str) -> datetime:
    return parse_iso(iso).replace(hour=0, minute=0, second=0, microsecond=0)


def in_window(iso: str, start: datetime, end: datetime) -> bool:
    d = parse_iso(iso)
    return start <= d < (end + timedelta(days=1))


def unique_days(dates: list[str]) -> int:
    return len({iso_day(day(d)) for d in dates})


def calendar_line_days(placed_at: str, doe: datetime) -> int:
    return (doe.date() - day(placed_at).date()).days + 1


def lookup_organism(key: str) -> dict[str, Any]:
    found = ORGANISMS.get(key)
    if found:
        return found
    return {
        "key": key,
        "name": key,
        "short": key,
        "class": "recognized-pathogen",
        "mbi": False,
    }


def skipped_phase(key: str, node: str, name: str, reason: str) -> dict[str, Any]:
    return {
        "key": key,
        "node": node,
        "name": name,
        "status": "skipped",
        "verdict": "Not reached",
        "math": reason,
        "facts": [{"label": "Why skipped", "value": reason, "tone": "neutral"}],
    }


def outcomes_equal(expected: dict, actual: dict) -> bool:
    a, b = expected.get("deltaTtpMinutes"), actual.get("deltaTtpMinutes")
    ttp_ok = a == b if a is None or b is None else abs(a - b) <= 1
    return (
        expected.get("surveillanceLabel") == actual.get("surveillanceLabel")
        and expected.get("lcbiType") == actual.get("lcbiType")
        and expected.get("mbiType") == actual.get("mbiType")
        and expected.get("countsInSir") == actual.get("countsInSir")
        and expected.get("nhsNReportable") == actual.get("nhsNReportable")
        and expected.get("bedsideStatus") == actual.get("bedsideStatus")
        and expected.get("salvageEligible") == actual.get("salvageEligible")
        and ttp_ok
    )


def evaluate_case(c: dict[str, Any]) -> dict[str, Any]:
    positives = sorted(c["bloodCultures"], key=lambda x: parse_iso(x["drawnAt"]))
    first = positives[0]
    doe = day(first["drawnAt"])
    iwp_start = doe - timedelta(days=IWP_RADIUS_DAYS)
    iwp_end = doe + timedelta(days=IWP_RADIUS_DAYS)
    sbap_end = doe + timedelta(days=RIT_DAYS - 1)

    org = lookup_organism(first["organismKey"])
    same = [x for x in positives if x["organismKey"] == first["organismKey"]]
    occasions = unique_days([x["drawnAt"] for x in same])
    specimen_count = len(same)
    symptoms = any(
        in_window(s["at"], doe - timedelta(days=1), doe + timedelta(days=1))
        for s in c.get("symptoms", [])
    )
    infant = c["patient"]["ageYears"] <= 1

    lcbi_type = None
    if org["class"] == "recognized-pathogen" and specimen_count >= 1:
        lcbi_type = "LCBI-1"
        integrity_verdict = "lcbi"
        integrity_math = (
            "LCBI 1: a recognized bacterial or fungal pathogen isolated from ≥1 blood specimen."
        )
    elif (
        org["class"] == "common-commensal"
        and specimen_count >= 2
        and occasions >= 1
        and symptoms
    ):
        lcbi_type = "LCBI-3" if infant else "LCBI-2"
        integrity_verdict = "lcbi"
        integrity_math = (
            "LCBI 3: common commensal from ≥2 specimens in a patient ≤1 year with fever, hypothermia, apnea, or bradycardia."
            if infant
            else "LCBI 2: common commensal from ≥2 specimens on the same or consecutive days plus fever >38.0°C, chills, or hypotension."
        )
    else:
        integrity_verdict = "contaminant"
        integrity_math = (
            "Surveillance non-event: common commensal from a single bottle, or no matching clinical symptoms — treated as a contaminant."
        )

    integrity = {
        "key": "integrity",
        "node": "1.0",
        "name": "Integrity check",
        "status": "verdict",
        "verdict": f"True BSI · {lcbi_type}" if integrity_verdict == "lcbi" else "Contaminant · non-event",
        "math": integrity_math,
        "facts": [
            {"label": "Organism", "value": org["name"], "tone": "neutral"},
            {
                "label": "NHSN class",
                "value": "Recognized pathogen" if org["class"] == "recognized-pathogen" else "Common commensal",
                "tone": "ok" if org["class"] == "recognized-pathogen" else "warn",
            },
            {
                "label": "Positive specimens",
                "value": f"{specimen_count} ({occasions} calendar day{'s' if occasions != 1 else ''})",
                "tone": "neutral",
            },
            {
                "label": "Symptoms in DOE ±1d",
                "value": "; ".join(f"{s['type']} {s['value']}" for s in c.get("symptoms", []))
                if symptoms
                else "None documented",
                "tone": "warn" if symptoms else "neutral",
            },
        ],
    }

    extra_matches = [
        ev
        for ev in c.get("extraVascularCultures", [])
        if ev["organismKey"] == first["organismKey"] and in_window(ev["drawnAt"], iwp_start, sbap_end)
    ]
    site_cfg = c.get("siteSpecificInfection")
    if site_cfg and site_cfg.get("criteriaMet") and extra_matches:
        site_specific = site_cfg
    elif extra_matches and extra_matches[0].get("nhsNSite"):
        site_specific = {
            "site": extra_matches[0]["nhsNSite"],
            "criteriaMet": True,
            "note": f"Taxonomic match from {extra_matches[0]['siteLabel']} inside the SBAP.",
        }
    elif site_cfg and site_cfg.get("criteriaMet"):
        site_specific = site_cfg
    else:
        site_specific = None

    is_secondary = integrity_verdict == "lcbi" and (len(extra_matches) > 0 or bool(site_specific))

    if integrity_verdict == "contaminant":
        source = skipped_phase("source", "2.0", "Source origin", "No LCBI — secondary attribution is not evaluated.")
    else:
        site_name = None
        if site_specific:
            site_name = site_specific.get("site")
        elif extra_matches:
            site_name = extra_matches[0].get("nhsNSite") or "localized"
        source = {
            "key": "source",
            "node": "2.0",
            "name": "Source origin",
            "status": "verdict",
            "verdict": f"Secondary BSI · {site_name}" if is_secondary else "Primary BSI",
            "math": (
                "Blood isolate genus/species matches an extravascular culture inside the Secondary BSI Attribution Period, or the blood culture is a required element of a site-specific infection."
                if is_secondary
                else "No matching qualifying extravascular infection under NHSN rules inside the SBAP."
            ),
            "facts": [
                {"label": "SBAP", "value": f"{iso_day(iwp_start)} → {iso_day(sbap_end)}", "tone": "neutral"},
                {
                    "label": "Matching extravascular cultures",
                    "value": "None"
                    if not extra_matches
                    else "; ".join(f"{m['organism']} · {m['siteLabel']}" for m in extra_matches),
                    "tone": "ok" if extra_matches else "neutral",
                },
                {
                    "label": "Site-specific infection",
                    "value": f"{site_specific['site']} — {site_specific['note']}" if site_specific else "Not verified",
                    "tone": "ok" if site_specific else "neutral",
                },
            ],
        }

    iwp_blood = [x for x in positives if in_window(x["drawnAt"], iwp_start, iwp_end)]
    iwp_keys = list(dict.fromkeys(x["organismKey"] for x in iwp_blood))
    non_mbi = [lookup_organism(k)["name"] for k in iwp_keys if not lookup_organism(k)["mbi"]]
    organism_on_master = org["mbi"]
    anc_in_iwp = [a for a in c.get("ancSeries", []) if in_window(a["at"], iwp_start, iwp_end)]
    neutropenic_days = unique_days(
        [a["at"] for a in anc_in_iwp if a["anc"] < NEUTROPENIA_THRESHOLD]
    )
    neutropenia_met = neutropenic_days >= 2
    hsct_at = c["patient"].get("allogeneicHsctAt")
    hsct_met = bool(
        hsct_at
        and 0 <= (doe.date() - day(hsct_at).date()).days <= HSCT_WINDOW_DAYS
        and (c["patient"].get("gvhd") or c["patient"].get("severeDiarrhea"))
    )
    is_mbi = (
        integrity_verdict == "lcbi"
        and not is_secondary
        and organism_on_master
        and len(non_mbi) == 0
        and (neutropenia_met or hsct_met)
    )
    mbi_type = f"MBI-{lcbi_type}" if is_mbi and lcbi_type else None

    if integrity_verdict == "contaminant" or is_secondary:
        mbi_phase = skipped_phase(
            "mbi",
            "3.0",
            "Pathophysiology",
            "Secondary BSI already attributed — MBI filter is not applied."
            if is_secondary
            else "No LCBI — MBI criteria are not evaluated.",
        )
    else:
        mbi_phase = {
            "key": "mbi",
            "node": "3.0",
            "name": "Pathophysiology",
            "status": "verdict",
            "verdict": mbi_type if is_mbi else "Standard primary BSI",
            "math": (
                "MBI-LCBI: organism is on the NHSN MBI master list, no non-MBI co-isolates in the 7-day IWP, and neutropenia (ANC <500 on ≥2 days) or allogeneic HSCT pathway is met."
                if is_mbi
                else "Host does not meet neutropenia/HSCT criteria, or the isolate is not an MBI organism."
            ),
            "facts": [
                {
                    "label": "MBI master list",
                    "value": "Match" if organism_on_master else "Not an MBI organism",
                    "tone": "ok" if organism_on_master else "neutral",
                },
                {
                    "label": "Non-MBI co-isolates in IWP",
                    "value": ", ".join(non_mbi) if non_mbi else "None",
                    "tone": "warn" if non_mbi else "ok",
                },
                {
                    "label": "Neutropenia pathway",
                    "value": f"{neutropenic_days} IWP day{'s' if neutropenic_days != 1 else ''} with ANC <500 (need ≥2)",
                    "tone": "ok" if neutropenia_met else "neutral",
                },
                {
                    "label": "Allogeneic HSCT pathway",
                    "value": "Met (transplant ≤1 year with GVHD or severe diarrhea)"
                    if hsct_met
                    else (
                        "Transplant recorded — accompanying GVHD/diarrhea not met"
                        if hsct_at
                        else "No allogeneic HSCT"
                    ),
                    "tone": "ok" if hsct_met else "neutral",
                },
            ],
        }

    line = c.get("line")
    line_days = calendar_line_days(line["firstAccessedInpatientAt"], doe) if line else None
    line_eligible = line_days is not None and line_days > LINE_ELIGIBLE_AFTER_DAYS and bool(line)
    evaluate_device = integrity_verdict == "lcbi" and not is_secondary and not is_mbi

    if not evaluate_device:
        if is_mbi:
            reason = f"Line would be calendar day {line_days if line_days is not None else '—'} — MBI exclusion applies before CLABSI assignment."
        elif is_secondary:
            reason = "Secondary BSI is attributed to the localized infection, not the line."
        else:
            reason = "No LCBI — device eligibility is not evaluated."
        device = skipped_phase("device", "4.0", "Device eligibility", reason)
    else:
        device = {
            "key": "device",
            "node": "4.0",
            "name": "Device eligibility",
            "status": "verdict",
            "verdict": "Primary CLABSI" if line_eligible else "Primary non-line LCBI",
            "math": (
                "Eligible central line first accessed in an inpatient location and in place >2 consecutive calendar days on the date of event."
                if line_eligible
                else "Line in place ≤2 calendar days, never accessed inpatient, or no eligible central line."
            ),
            "facts": [
                {"label": "Device", "value": line["type"] if line else "None", "tone": "neutral"},
                {
                    "label": "First inpatient access",
                    "value": line["firstAccessLocation"] if line else "—",
                    "tone": "neutral",
                },
                {
                    "label": "Calendar day on DOE",
                    "value": f"Day {line_days}" if line_days is not None else "—",
                    "tone": "danger" if line_eligible else "ok",
                },
                {"label": "Eligibility threshold", "value": ">2 consecutive calendar days", "tone": "neutral"},
            ],
        }

    central = next(
        (x for x in positives if x["source"] == "central" and x.get("timeToPositivityHours") is not None),
        None,
    )
    peripheral = next(
        (x for x in positives if x["source"] == "peripheral" and x.get("timeToPositivityHours") is not None),
        None,
    )
    delta = None
    bedside_status = "missing-data"
    if central and peripheral:
        delta = (peripheral["timeToPositivityHours"] - central["timeToPositivityHours"]) * 60
        bedside_status = "biofilm-supported" if delta >= BIOFILM_MINUTES else "biofilm-not-supported"

    salvage = bedside_status == "biofilm-not-supported"
    if bedside_status == "biofilm-supported":
        rec = "Intraluminal biofilm supported. Catheter salvage is unlikely — prioritize line extraction."
        verdict = "Intraluminal biofilm supported"
    elif bedside_status == "biofilm-not-supported":
        rec = "Biofilm pattern not supported. Infection is likely systemic or translocational — the line is eligible for salvage with targeted antibiotics."
        verdict = "Biofilm pattern not supported"
    else:
        rec = "ΔTTP cannot be calculated. Draw a paired peripheral set before any extraction decision."
        verdict = "Actionable gap · missing pair"

    bedside_phase = {
        "key": "bedside",
        "node": "5.0",
        "name": "Catheter preservation",
        "status": "parallel",
        "verdict": verdict,
        "math": "Paired central and peripheral cultures: ΔTTP ≥120 minutes (central flags ≥2 hours earlier) supports CRBSI biofilm. Simultaneous or near-simultaneous positivity does not.",
        "facts": [
            {
                "label": "Central TTP",
                "value": f"{central['timeToPositivityHours']:.2f} h" if central else "Not drawn",
                "tone": "neutral" if central else "warn",
            },
            {
                "label": "Peripheral TTP",
                "value": f"{peripheral['timeToPositivityHours']:.2f} h" if peripheral else "Not drawn",
                "tone": "neutral" if peripheral else "warn",
            },
            {
                "label": "ΔTTP",
                "value": "Cannot calculate"
                if delta is None
                else f"{round(delta)} min (threshold ≥{BIOFILM_MINUTES})",
                "tone": "danger"
                if bedside_status == "biofilm-supported"
                else "ok"
                if bedside_status == "biofilm-not-supported"
                else "warn",
            },
        ],
    }

    counts_in_sir = False
    nhsn = False
    if integrity_verdict == "contaminant":
        label = "Contaminant"
        sir_impact = "non-event"
    elif is_secondary:
        label = "Secondary BSI"
        sir_impact = "excluded-secondary"
        nhsn = True
    elif is_mbi:
        label = "MBI-LCBI"
        sir_impact = "excluded-mbi"
        nhsn = True
    elif line_eligible:
        label = "Primary CLABSI"
        sir_impact = "counts"
        counts_in_sir = True
        nhsn = True
    else:
        label = "Primary Non-Line LCBI"
        sir_impact = "non-line"
        nhsn = True

    gaps = []
    if not peripheral:
        gaps.append(
            {
                "id": "no-peripheral",
                "title": "No peripheral comparative draw",
                "detail": "ΔTTP cannot be calculated. Nursing should obtain a paired peripheral set before line extraction is initiated.",
                "actionable": True,
            }
        )
    if not central:
        gaps.append(
            {
                "id": "no-central",
                "title": "No central-line culture",
                "detail": "A central specimen was not logged, so biofilm kinetics are incomplete.",
                "actionable": True,
            }
        )
    if org["class"] == "common-commensal" and specimen_count < 2:
        gaps.append(
            {
                "id": "single-commensal",
                "title": "Single commensal isolate",
                "detail": "Repeat blood culture kinetics should be watched. A second specimen on the same or next day would reopen LCBI 2/3.",
                "actionable": True,
            }
        )
    if org["class"] == "common-commensal" and specimen_count >= 2 and not symptoms:
        gaps.append(
            {
                "id": "no-symptoms",
                "title": "Commensal without qualifying symptoms",
                "detail": "LCBI 2/3 requires fever >38.0°C, chills, or hypotension (or infant equivalents).",
                "actionable": False,
            }
        )
    if integrity_verdict == "lcbi" and not is_secondary and len(anc_in_iwp) < 2:
        gaps.append(
            {
                "id": "sparse-anc",
                "title": "Sparse ANC in the IWP",
                "detail": "MBI neutropenia pathway needs ANC or WBC on two separate IWP days.",
                "actionable": False,
            }
        )
    if central and peripheral:
        mins = abs(
            (parse_iso(central["drawnAt"]) - parse_iso(peripheral["drawnAt"])).total_seconds()
        ) / 60
        if mins > 15:
            gaps.append(
                {
                    "id": "nonsimultaneous",
                    "title": "Paired draws more than 15 minutes apart",
                    "detail": "ΔTTP is most reliable when central and peripheral bottles are drawn simultaneously.",
                    "actionable": False,
                }
            )

    actual = {
        "surveillanceLabel": label,
        "lcbiType": lcbi_type,
        "mbiType": mbi_type,
        "countsInSir": counts_in_sir,
        "nhsNReportable": nhsn,
        "bedsideStatus": bedside_status,
        "deltaTtpMinutes": None if delta is None else round(delta),
        "salvageEligible": salvage,
    }

    return {
        "caseId": c["id"],
        "doe": iso_day(doe),
        "iwp": {"start": iso_day(iwp_start), "end": iso_day(iwp_end)},
        "sbap": {"start": iso_day(iwp_start), "end": iso_day(sbap_end)},
        "primaryOrganism": org["name"],
        "primaryOrganismKey": org["key"],
        "lineCalendarDays": line_days,
        "phases": {
            "integrity": integrity,
            "source": source,
            "mbi": mbi_phase,
            "device": device,
            "bedside": bedside_phase,
        },
        "surveillance": {
            "label": label,
            "lcbiType": lcbi_type,
            "mbiType": mbi_type,
            "nhsNReportable": nhsn,
            "countsInSir": counts_in_sir,
            "sirImpact": sir_impact,
            "attributionSite": site_specific.get("site") if site_specific else None,
        },
        "bedside": {
            "status": bedside_status,
            "deltaTtpMinutes": actual["deltaTtpMinutes"],
            "centralTtpHours": central["timeToPositivityHours"] if central else None,
            "peripheralTtpHours": peripheral["timeToPositivityHours"] if peripheral else None,
            "recommendation": rec,
            "salvageEligible": salvage,
        },
        "mbi": {
            "organismOnMasterList": organism_on_master,
            "nonMbiCoisolates": non_mbi,
            "neutropenicDays": neutropenic_days,
            "neutropeniaMet": neutropenia_met,
            "hsctMet": hsct_met,
        },
        "gaps": gaps,
        "fixture": {
            "matches": outcomes_equal(c["expected"], actual),
            "expected": c["expected"],
            "actual": actual,
        },
    }


def summarize_queue(cases: list[dict], results: list[dict]) -> dict[str, int]:
    return {
        "total": len(cases),
        "naiveClabsi": sum(1 for c in cases if c.get("line") and c.get("bloodCultures")),
        "sirNumerator": sum(1 for r in results if r["surveillance"]["countsInSir"]),
        "excluded": sum(
            1
            for r in results
            if r["surveillance"]["sirImpact"] in ("excluded-mbi", "excluded-secondary", "non-event")
        ),
        "salvage": sum(1 for r in results if r["bedside"]["salvageEligible"]),
        "extract": sum(1 for r in results if r["bedside"]["status"] == "biofilm-supported"),
        "gaps": sum(1 for r in results if r["bedside"]["status"] == "missing-data"),
    }


def surveillance_tone(label: str) -> str:
    if label == "Primary CLABSI":
        return "danger"
    return "ok"


def sir_copy(impact: str) -> str:
    return {
        "counts": "Counts in SIR numerator",
        "excluded-mbi": "Reported to NHSN · excluded from SIR",
        "excluded-secondary": "Attributed off the line · not a CLABSI",
        "non-event": "Suppressed · surveillance non-event",
        "non-line": "Primary LCBI · not device-associated",
    }.get(impact, impact)


def bedside_copy(status: str) -> str:
    return {
        "biofilm-supported": "Extract the line",
        "biofilm-not-supported": "Salvage the line",
        "missing-data": "Draw a peripheral set",
    }.get(status, status)


def bedside_tone(status: str) -> str:
    return {
        "biofilm-supported": "danger",
        "biofilm-not-supported": "ok",
        "missing-data": "warn",
    }.get(status, "muted")
