import re
import json
import logging
from src.groq_service import GroqService

logger = logging.getLogger(__name__)

class MockShellGenerator:
    def __init__(self, tlf_list: list):
        self.tlf_list = tlf_list
        self.groq_service = GroqService()

    def generate_templates(self, selected_tables=None) -> list:
        templates = []

        for tlf in self.tlf_list:
            try:
                tlf = dict(tlf)
                tlf_type = str(tlf.get("type", "Table")).strip().capitalize()
                category = str(tlf.get("category", "Generic")).strip()
                number = str(tlf.get("number", "")).strip()
                title = str(tlf.get("title", "Untitled")).strip()

                if selected_tables is not None:
                    identifier = f"{tlf_type} {number}: {title}"
                    if identifier not in selected_tables:
                        continue

                treatment_arms = tlf.get("treatment_arms", []) or ["Placebo", "Active Treatment", "Total"]
                analysis_set = tlf.get("analysis_set", "All Subjects")

                # If Groq is configured, generate professional mock designs dynamically
                if self.groq_service.has_api_key():
                    logger.info(f"Generating dynamic layout shells via Groq for: {tlf_type} {number}")
                    
                    system_prompt = (
                        "You are an expert Biostatistician designer for clinical trial submissions (ICH E3 / CDISC guidelines).\n"
                        "Given clinical metadata, design a realistic pharma mock-up table/listing structure.\n"
                        "You must return a valid JSON object with exactly three keys:\n"
                        "1. 'headers': A list of strings representing appropriate columns for the table or listing.\n"
                        "2. 'rows': A list of lists containing realistic example placeholder cell values.\n"
                        "3. 'footnotes': A comprehensive string containing appropriate clinical footnotes separated by newlines."
                    )
                    
                    user_input = (
                        f"Type: {tlf_type}\n"
                        f"Number: {number}\n"
                        f"Title: {title}\n"
                        f"Category: {category}\n"
                        f"Arms: {', '.join(treatment_arms)}\n"
                        f"Population: {analysis_set}"
                    )

                    response = self.groq_service.analyze_text(system_prompt, user_input, response_format_json=True)
                    try:
                        layout_data = json.loads(response)
                        tlf["headers"] = layout_data.get("headers", [])
                        tlf["rows"] = layout_data.get("rows", [])
                        tlf["footnotes"] = layout_data.get("footnotes", "")
                    except Exception as parse_err:
                        logger.warning(f"Failed parsing Groq response for {number}, using rule-based generator: {parse_err}")
                        self._apply_rules_to_tlf(tlf, tlf_type, category, title, treatment_arms, analysis_set)
                else:
                    # Execute rule-based backup layout generation
                    self._apply_rules_to_tlf(tlf, tlf_type, category, title, treatment_arms, analysis_set)

                # Shared Technical Output Metadata Fields
                tlf["notes_section"] = f"Note: Standard calculations and percentages are built based on populations inside the {analysis_set}."
                
                # Determine source dataset dynamically
                if "demograph" in title.lower() or category.lower() == "demographics":
                    tlf["source_dataset"] = "ADSL"
                elif "adverse" in title.lower() or category.lower() == "adverse events":
                    tlf["source_dataset"] = "ADAE"
                else:
                    tlf["source_dataset"] = "ADSL" if tlf_type == "Table" else "ADxx"

                prog_id = re.sub(r"[^a-zA-Z0-9]", "_", number.lower()) if number else "gen"
                prefix = "t" if tlf_type.lower() == "table" else "l"
                tlf["validated_source_code_path"] = f"/project/stats/programs/{prefix}_{prog_id}.sas"

                tlf["company"] = "Global Pharma Inc."
                tlf["protocol"] = "PROTOCOL-XYZ-123"

                templates.append(tlf)

            except Exception as e:
                logger.error(f"Skipping row iteration due to format mismatch: {e}")
                continue

        return templates

    def _apply_rules_to_tlf(self, tlf, tlf_type, category, title, treatment_arms, analysis_set):
        """Rule-based layout backup generator."""
        if tlf_type.lower() == "table":
            headers = ["System Organ Class / Preferred Term" if "adverse" in title.lower() else "Characteristic"]
            for arm in treatment_arms:
                headers.append(f"{arm}\n(N=xx)\nn (%)")
            
            if "adverse" in title.lower():
                rows = [
                    ("Subjects with at least one TEAE", "xx (xx.x%)", "xx (xx.x%)", "xx (xx.x%)", "xx (xx.x%)"),
                    ("CARDIAC DISORDERS", "xx (xx.x%)", "xx (xx.x%)", "xx (xx.x%)", "xx (xx.x%)"),
                    ("  Atrial Fibrillation", "xx (xx.x%)", "xx (xx.x%)", "xx (xx.x%)", "xx (xx.x%)"),
                ]
            else:
                rows = [
                    ("Age (Years)", "", "", "", ""),
                    ("  Mean (SD)", "xx.x (xx.xx)", "xx.x (xx.xx)", "xx.x (xx.xx)", "xx.x (xx.xx)"),
                    ("  Median", "xx.x", "xx.x", "xx.x", "xx.x"),
                    ("Sex [n (%)]", "", "", "", ""),
                    ("  Male", "xx (xx.x%)", "xx (xx.x%)", "xx (xx.x%)", "xx (xx.x%)"),
                    ("  Female", "xx (xx.x%)", "xx (xx.x%)", "xx (xx.x%)", "xx (xx.x%)"),
                ]
            tlf["headers"] = headers
            tlf["rows"] = rows
        else:  # Listings
            headers = ["Subject ID", "Treatment Arm", "Preferred Term", "System Organ Class", "Severity", "Serious (Y/N)"]
            rows = [
                ("SUBJ-001", "Placebo", "Atrial Fibrillation", "Cardiac Disorders", "Mild", "N"),
                ("SUBJ-002", "Active Treatment", "Atrial Fibrillation", "Cardiac Disorders", "Severe", "Y"),
            ]
            tlf["headers"] = headers
            tlf["rows"] = rows

        tlf["footnotes"] = self._generate_dynamic_footnotes(category, title, tlf_type)

    def _generate_dynamic_footnotes(self, category: str, title: str, tlf_type: str) -> str:
        """Generates domain-specific clinical footnotes based on individual table properties."""
        title_lower = title.lower()
        fn_lines = []
        
        # 1. Base rule for Adverse Events
        if category == "Adverse Events" or "adverse" in title_lower or "ae" in title_lower:
            fn_lines.append("[1] Adverse events (AEs) are coded using the Medical Dictionary for Regulatory Activities (MedDRA) version 26.0.")
            fn_lines.append("[2] Treatment-Emergent Adverse Events (TEAEs) are defined as events that start or worsen on or after the first dose of study drug.")
            
            if "serious" in title_lower or "sae" in title_lower:
                fn_lines.append("[3] Serious Adverse Events are defined according to international regulatory (ICH) reporting criteria.")
            elif "severity" in title_lower or "intensity" in title_lower:
                fn_lines.append("[3] AE intensity is graded by investigators as Mild, Moderate, or Severe.")
            elif "relationship" in title_lower or "related" in title_lower:
                fn_lines.append("[3] Relationship to study treatment is classified by investigators as Related or Not Related.")
            else:
                fn_lines.append("[3] n = Number of unique subjects reporting at least one occurrence of the event; [e] = Total cumulative event count.")
                
        # 2. Base rule for Demographics and Baseline Characteristics
        elif category == "Demographics" or "demographic" in title_lower or "baseline" in title_lower:
            fn_lines.append("[1] Percentages are calculated based on the total number of subjects (N) within the specified treatment column.")
            fn_lines.append("[2] Summary statistics include Mean, Standard Deviation (SD), Median, Minimum, and Maximum for continuous variables.")
            if "bmi" in title_lower or "weight" in title_lower:
                fn_lines.append("[3] Body Mass Index (BMI) is calculated as weight in kilograms divided by height in meters squared (kg/m²).")

        # 3. Rules for Subject Dispositions
        elif "disposition" in title_lower or "status" in title_lower:
            fn_lines.append("[1] Percentages are based on the number of randomized subjects in each treatment arm.")
            fn_lines.append("[2] Primary reasons for discontinuation are derived from individual subject case report forms (CRFs).")

        # 4. Standard fallback rules for general Tables/Listings
        else:
            if tlf_type.lower() == "listing":
                fn_lines.append("[1] Subject identifiers are systematically anonymized to comply with global data transparency guidelines.")
                fn_lines.append("[2] Listings are sorted chronologically by subject identifier and event date.")
            else:
                fn_lines.append("[1] n = Number of subjects meeting the criteria; percentages (%) are based on the column headers (N).")
                fn_lines.append("[2] Data values are sourced from standard clinical database snapshot extracts.")

        return "\n".join(fn_lines)