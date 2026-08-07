import logging
import re
import json
from src.groq_service import GroqService

logger = logging.getLogger(__name__)


class Extractor:
    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        self.groq_service = GroqService()

    def extract_tlfs(self) -> list:
        if not self.raw_text:
            return []

        # Try to use Groq if API key is configured
        if self.groq_service.has_api_key():
            logger.info("Executing cloud-based LLM extraction via Groq...")
            extracted = self._extract_via_groq()
            if extracted:
                return extracted
            logger.warning("Groq extraction failed or returned empty. Falling back to local rule-based extractor.")

        # Fallback to local rule-based parsing engine
        logger.info("Executing advanced local text classification & title scrubbing engine...")
        return self._extract_via_rules()

    def _extract_via_groq(self) -> list:
        try:
            system_prompt = (
                "You are an expert clinical data science assistant. Analyze the raw text extracted from a Statistical Analysis Plan (SAP) "
                "and identify all tables, figures, or listings (TLFs) scheduled for generation. "
                "You must return a valid JSON object with a single key 'tlfs' mapping to an array of objects. "
                "Each object in the array must strictly have these fields:\n"
                "- 'type': 'Table' or 'Listing'\n"
                "- 'number': The section or table sequence number (e.g., '14.1.2.1')\n"
                "- 'title': Cleaned, sentence-cased title of the table/listing (strip off leading dots/hyphens)\n"
                "- 'category': 'Demographics', 'Adverse Events', 'Disposition', or 'Generic'\n"
                "- 'treatment_arms': A list of treatment groups (e.g. ['Placebo', 'Active Tx Low', 'Active Tx High', 'Total'])\n"
                "- 'analysis_set': The population to analyze (e.g., 'Safety Population', 'All Randomized Subjects')"
            )

            # Limit context window safely
            truncated_text = self.raw_text[:25000]
            response = self.groq_service.analyze_text(
                system_prompt=system_prompt,
                user_content=truncated_text,
                response_format_json=True
            )

            if response:
                parsed_data = json.loads(response)
                results = parsed_data.get("tlfs", [])
                
                # Separation Pass: Group all Tables first, followed by all Listings
                tables_list = [item for item in results if item.get("type") == "Table"]
                listings_list = [item for item in results if item.get("type") == "Listing"]
                return tables_list + listings_list

        except Exception as e:
            logger.error(f"Error extracting via Groq API: {e}")
        return []

    def _extract_via_rules(self) -> list:
        results = []
        seen_titles = set()

        lines = self.raw_text.split("\n")
        demo_count = 1
        ae_count = 1

        for line in lines:
            cleaned = line.strip()
            if len(cleaned) < 6 or len(cleaned) > 500:
                continue
                
            cleaned_lower = cleaned.lower()
            if any(k in cleaned_lower for k in ["page", "continued", "will be provided", "confidential", "protocol snapshot"]):
                continue

            category = "Filter Out"
            
            # Identify Domain Focus Rules
            if any(k in cleaned_lower for k in ["demograph", "baseline characteristic", "subject characteristics", "age group", "ethnicity"]):
                if "listing" in cleaned_lower:
                    category = "Demographics Listing"
                else:
                    category = "Demographics"
                num_prefix = f"14.1.2.{demo_count}"
                demo_count += 1
            elif any(k in cleaned_lower for k in ["adverse event", "teae", "treatment-emergent", "serious adverse", "sae", "ae summary", "special interest", "listing"]):
                if "listing" in cleaned_lower:
                    category = "Adverse Events Listing"
                else:
                    category = "Adverse Events"
                num_prefix = f"14.3.1.{ae_count}"
                ae_count += 1

            if category == "Filter Out":
                continue

            # Extract Number using matching loops
            num_match = re.search(r'(?:table|listing)\s+([\d\.\-_]+)', cleaned_lower)
            if num_match:
                number = num_match.group(1).strip(".")
            else:
                number = num_prefix

            # Strip table/listing identifiers out to extract pure titles cleanly
            title = re.sub(r'^(?:table|listing)\s+[\d\.\-_]+\s*[:\-–—]?\s*', '', cleaned, flags=re.IGNORECASE).strip()
            
            # Specific Hyphen & Bracket Scrubbing Pass
            for _ in range(3):
                title = re.sub(r'^[:\-–—\.\s\s*,\)\}\]]+', '', title).strip()
                title = re.sub(r'^[^\w]*\s*[\)\}\]]\s*,?\s*', '', title).strip()
                title = re.sub(r'^\([^)]*\)[\s,\.\-_:\+]*', '', title).strip()
                title = re.sub(r'^\d+\s*(?:ng/mL|mg|g|ml|μg)?\s*[:\-–—\.]*\s*', '', title).strip()

            title = re.sub(r'^[:\-–—\.\s*,\)\}\]]+', '', title).strip()
            title = re.sub(r'[\s\.]+\d+\s*$', '', title)
            title = re.sub(r'\\.{2,}', '', title).strip()
            title = re.sub(r'\s+', ' ', title)

            # Enforce proper capitalized sentence-case formatting
            if title and title[0].islower():
                title = title[0].upper() + title[1:]

            if not title or title.lower() in seen_titles:
                continue
            seen_titles.add(title.lower())

            treatment_arms = ["Placebo", "Active Tx Low", "Active Tx High", "Total"]

            is_listing = "listing" in category.lower() or "listing" in cleaned_lower
            tlf_type = "Listing" if is_listing else "Table"

            results.append({
                "type": tlf_type,
                "number": number,
                "title": title,
                "category": category,
                "treatment_arms": treatment_arms,
                "analysis_set": "Safety Population" if "adverse" in category.lower() else "All Randomized Subjects"
            })

        if not results:
            results = [
                {
                    "type": "Table", "number": "14.1.2.1", 
                    "title": "Summary of Demographics and Baseline Characteristics", 
                    "category": "Demographics", "treatment_arms": ["Placebo", "Active Treatment", "Total"], "analysis_set": "All Randomized Subjects"
                },
                {
                    "type": "Table", "number": "14.3.1.1", 
                    "title": "Overview of Treatment-Emergent Adverse Events (TEAEs)", 
                    "category": "Adverse Events", "treatment_arms": ["Placebo", "Active Treatment", "Total"], "analysis_set": "Safety Population"
                }
            ]

        # Separation Pass: Group all Tables first, followed by all Listings
        tables_list = [item for item in results if item["type"] == "Table"]
        listings_list = [item for item in results if item["type"] == "Listing"]
        
        return tables_list + listings_list