# # insight_agent.py
# from typing import Dict, Any, List
# import json
# from json import JSONDecodeError

# from llm_client import get_llm_client


# class InsightAgent:
#     def __init__(self):
#         self.client, self.model_name, self.provider = get_llm_client()

#     def _safe_completion(self, messages, max_tokens=500, temperature=0.7, retries=6, backoff_base=2):
#         """Use HTTP wrapper client.create_chat() with retries + backoff. Returns model text."""
#         last_exc = None
#         for attempt in range(retries):
#             try:
#                 j = self.client.create_chat(messages=messages, max_tokens=max_tokens, temperature=temperature)
#                 return j["choices"][0]["message"]["content"].strip()
#             except Exception as e:
#                 last_exc = e
#                 wait = min(backoff_base ** attempt, 30)
#                 print(f"[InsightAgent] error (attempt {attempt+1}/{retries}): {e}. retry in {wait}s...")
#                 import time; time.sleep(wait)
#                 continue
#         raise RuntimeError(f"_safe_completion failed after {retries} attempts. Last error: {last_exc}")

#     @staticmethod
#     def _sheet_names(summary: Dict[str, Any]) -> List[str]:
#         if "sheet_names" in summary:
#             return list(summary["sheet_names"])
#         base = summary.get("sheets") or summary
#         return [k for k in base.keys() if not str(k).startswith("_")]

#     @staticmethod
#     def _sheet_info(summary: Dict[str, Any], sheet: str) -> Dict[str, Any]:
#         return (summary.get("sheets") or summary).get(sheet, {})

#     def _prompt_for_sheet(self, info: Dict[str, Any]) -> str:
#         rows, cols = info.get("shape", (0, 0))
#         num_cols = info.get("numeric_cols", [])
#         cat_cols = info.get("categorical_cols", [])
#         dt_cols = info.get("datetime_cols", [])
        
#         # ── keep sample rows but cap columns at 12 ──────────────────
#         sample_rows = info.get("sample_rows", [])[:15]  # 15 rows max
#         if sample_rows:
#             all_keys = list(sample_rows[0].keys())
#             keep_keys = all_keys[:12]          # max 12 cols in sample
#             sample_rows = [
#                 {k: row[k] for k in keep_keys if k in row}
#                 for row in sample_rows
#             ]

#         # ── send only strong correlations ───────────────────────────
#         corr = info.get("corr", {})            # already filtered >= 0.3

#         # ── send outlier counts only, not bounds ────────────────────
#         outlier_summary = {
#             col: data["count"]
#             for col, data in info.get("outliers", {}).items()
#             if data["count"] > 0          # only cols that have outliers
#         }

#         # ── skewness — only notably skewed cols (|skew| > 1) ────────
#         skew_notable = {
#             col: val
#             for col, val in info.get("skewness", {}).items()
#             if abs(val) > 1
#         }

#         # ── datetime summary ─────────────────────────────────────────
#         dt_ranges = info.get("datetime_ranges", {})

#         # ── data quality ─────────────────────────────────────────────
#         dq = info.get("data_quality_notes", {})

#         return f"""
#         You are a senior data analyst. Use the dataset summary to produce grounded, concise insights.

#         DATA ANCHORS
#         - shape: {rows} rows x {cols} cols
#         - numeric_cols: {num_cols}
#         - categorical_cols: {cat_cols}
#         - datetime_cols: {dt_cols}
#         - duplicate_rows: {dq.get("duplicate_rows", 0)}
#         - overall_missing_pct: {dq.get("overall_missing_pct", 0)}%

#         OUTLIERS (IQR method, count of outlier rows per column):
#         {json.dumps(outlier_summary, indent=2)}

#         NOTABLE SKEWNESS (|skew| > 1):
#         {json.dumps(skew_notable, indent=2)}

#         STRONG CORRELATIONS (|r| >= 0.3):
#         {json.dumps(corr, indent=2)}

#         DATETIME RANGES:
#         {json.dumps(dt_ranges, indent=2)}

#         SAMPLE ROWS (first 15 rows, first 12 cols):
#         {json.dumps(sample_rows, indent=2)}

#         WRITE:
#         Generate 14-15 concise bullet-point insights.
#         Each bullet must:
#         - Reference actual column names
#         - Include concrete values where possible
#         - Format: "- **Heading**: short explanation with numbers"

#         Cover themes:
#         1. Distribution & Outliers
#         2. Missing Data & Duplicates
#         3. Correlations
#         4. Category Dominance
#         5. Time Trends (if datetime columns exist)
#         """.strip()

#     def generate_insights(self, summary: Dict[str, Any]) -> Dict[str, str]:
#         """Per-sheet analytical insights."""
#         out: Dict[str, str] = {}
#         for sheet in self._sheet_names(summary):
#             info = self._sheet_info(summary, sheet)
#             prompt = self._prompt_for_sheet(info)
#             try:
#                 text = self._safe_completion(
#                     messages=[
#                         {"role": "system", "content": "You are a helpful, precise data analyst."},
#                         {"role": "user", "content": prompt},
#                     ],
#                     max_tokens=700,
#                     temperature=0.7,
#                 )
#                 out[sheet] = (text or "").strip()
#             except Exception as e:
#                 out[sheet] = f"Insight generation failed: {e}"
#         return out

#     def generate_business_insights(self, summary: Dict[str, Any]) -> Dict[str, str]:
#         """Narrative-style actionable insights per sheet with dataset context."""
#         out: Dict[str, str] = {}
#         for sheet in self._sheet_names(summary):
#             info = self._sheet_info(summary, sheet)
#             rows, cols = info.get("shape", (0, 0))
#             num_cols = info.get("numeric_cols", [])
#             cat_cols = info.get("categorical_cols", [])
#             dt_cols = info.get("datetime_cols", [])
#             sample_rows = info.get("sample_rows", [])[:10]

#             prompt = f"""
#                 You are a senior business strategist. Based on the dataset profile and sample rows,
#                 generate 5-6 narrative-style business insights. Each insight should be actionable and tied to the data.

#                 DATASET PROFILE:
#                 - shape: {rows} rows x {cols} cols
#                 - numeric_cols: {num_cols}
#                 - categorical_cols: {cat_cols}
#                 - datetime_cols: {dt_cols}

#                 SAMPLE ROWS (first 10):
#                 {json.dumps(sample_rows, indent=2)}

#                 WRITE:
#                 Business Insights:
#                 - Insight 1
#                 - Insight 2
#                 ...
#                 - Insight 9
#                 """.strip()

#             try:
#                 text = self._safe_completion(
#                     messages=[
#                         {"role": "system", "content": "You are a helpful, precise business analyst."},
#                         {"role": "user", "content": prompt},
#                     ],
#                     max_tokens=600,
#                     temperature=0.7,
#                 )
#                 out[sheet] = (text or "").strip()
#             except Exception as e:
#                 out[sheet] = f"Business insight generation failed: {e}"
#         return out

#     def generate_exec_summary(self, summary: Dict[str, Any]) -> str:
#         """High-level executive summary across all sheets."""
#         meta = summary.get("metadata", {})
#         sheet_names = self._sheet_names(summary)
#         prompt = f"""
#         You are a senior executive analyst. Provide a high-level summary of the dataset.

#         DATASET METADATA:
#         - File name: {meta.get("file_name")}
#         - Sheet count: {meta.get("sheet_count")}
#         - Sheets: {sheet_names}

#         WRITE:
#         Generate 4-5 concise bullet points that summarize the dataset overall.
#         Each bullet should highlight:
#         - Overall size and scope
#         - Key column types (numeric, categorical, datetime)
#         - General data quality observations
#         - Any broad trends or patterns
#         """.strip()
#         try:
#             text = self._safe_completion(
#                 messages=[
#                     {"role": "system", "content": "You are a helpful executive data analyst."},
#                     {"role": "user", "content": prompt},
#                 ],
#                 max_tokens=400,
#                 temperature=0.6,
#             )
#             return (text or "").strip()
#         except Exception as e:
#             return f"Executive summary generation failed: {e}"

#     def generate_chart_plan(self, summary: dict) -> dict:
#         """Chart plan JSON per sheet."""
#         sheets = (summary.get("sheets") or summary)
#         brief = {s: {
#             "numeric": sheets[s].get("numeric_cols", [])[:6],
#             "categorical": sheets[s].get("categorical_cols", [])[:6],
#             "has_corr": bool(sheets[s].get("corr")),
#             "sample_rows": sheets[s].get("sample_rows", [])[:5]
#         } for s in sheets.keys()}

#         prompt = f"""
#         Return ONLY valid JSON. Do not include explanations.

#         Objective:
#         For each sheet, propose  meaningful 8 charts highlighting key patterns.

#         Chart Types:
#         - "hist": numeric distributions
#         - "box": numeric outliers
#         - "bar": categorical distributions
#         - "pie": category proportions
#         - "heatmap": correlations (if moderate or strong)

#         Output JSON Schema:
#         {{ "<sheet_name>": [ {{ "type": "...", "col": "...", "bins": <int>, "top_n": <int>, "title": "..." }} ] }}

#         Constraints:
#         - Use only columns present
#         - Avoid duplicates
#         - Titles must be human-readable

#         Data:
#         {json.dumps(brief, indent=2)}
#         """.strip()
#         try:
#             text = self._safe_completion(
#                 messages=[
#                     {"role": "system", "content": "You are a helpful chart planner. Return only JSON."},
#                     {"role": "user", "content": prompt},
#                 ],
#                 max_tokens=800,
#                 temperature=0.7,
#             )
#             plan = json.loads(text)
#             return plan
#         except JSONDecodeError as je:
#             raise RuntimeError(f"Chart plan JSON parse error: {je}\nRaw model output:\n{text[:2000]}")
#         except Exception as e:
#             raise RuntimeError(f"Chart plan generation failed: {e}")



# # insight_agent.py
# from typing import Dict, Any, List
# import json
# from json import JSONDecodeError

# from llm_client import get_llm_client


# class InsightAgent:
#     def __init__(self):
#         self.client, self.model_name, self.provider = get_llm_client()

#     def _safe_completion(self, messages, max_tokens=500, temperature=0.3, retries=6, backoff_base=2):
#         """Use HTTP wrapper client.create_chat() with retries + backoff. Returns model text."""
#         last_exc = None
#         for attempt in range(retries):
#             try:
#                 j = self.client.create_chat(
#                     messages=messages,
#                     max_tokens=max_tokens,
#                     temperature=temperature
#                 )
#                 return j["choices"][0]["message"]["content"].strip()
#             except Exception as e:
#                 last_exc = e
#                 wait = min(backoff_base ** attempt, 30)
#                 print(f"[InsightAgent] error (attempt {attempt+1}/{retries}): {e}. retry in {wait}s...")
#                 import time; time.sleep(wait)
#                 continue
#         raise RuntimeError(f"_safe_completion failed after {retries} attempts. Last error: {last_exc}")

#     @staticmethod
#     def _sheet_names(summary: Dict[str, Any]) -> List[str]:
#         if "sheet_names" in summary:
#             return list(summary["sheet_names"])
#         base = summary.get("sheets") or summary
#         return [k for k in base.keys() if not str(k).startswith("_")]

#     @staticmethod
#     def _sheet_info(summary: Dict[str, Any], sheet: str) -> Dict[str, Any]:
#         return (summary.get("sheets") or summary).get(sheet, {})

#     # ────────────────────────────────────────────────────────────────
#     # Prompt builder — selective, token-aware
#     # ────────────────────────────────────────────────────────────────
#     def _build_context(self, info: Dict[str, Any]) -> str:
#         """Build a compact, information-dense context block for any prompt."""
#         rows, cols = info.get("shape", (0, 0))
#         num_cols   = info.get("numeric_cols", [])
#         cat_cols   = info.get("categorical_cols", [])
#         dt_cols    = info.get("datetime_cols", [])
#         dq         = info.get("data_quality_notes", {})

#         # Sample rows — cap at 15 rows, 12 cols
#         sample_rows = info.get("sample_rows", [])[:15]
#         if sample_rows:
#             keep_keys   = list(sample_rows[0].keys())[:12]
#             sample_rows = [{k: r[k] for k in keep_keys if k in r} for r in sample_rows]

#         # Correlations — already filtered >= 0.3
#         corr = info.get("corr", {})

#         # Outliers — only cols with actual outliers
#         outlier_summary = {
#             col: d["count"]
#             for col, d in info.get("outliers", {}).items()
#             if d.get("count", 0) > 0
#         }

#         # Skewness — only notable (|skew| > 1)
#         skew_notable = {
#             col: val
#             for col, val in info.get("skewness", {}).items()
#             if abs(val) > 1
#         }

#         # Top categories — first 8 cols only to save tokens
#         top_cats = dict(list(info.get("top_categories", {}).items())[:8])

#         # Numeric describe — mean/std/min/max only, skip percentiles
#         num_desc_raw = info.get("numeric_describe", {})
#         num_desc_compact = {
#             col: {
#                 k: v for k, v in stats.items()
#                 if k in ("mean", "std", "min", "max", "count")
#             }
#             for col, stats in num_desc_raw.items()
#         }

#         dt_ranges = info.get("datetime_ranges", {})

#         return f"""
# DATASET PROFILE
# - Shape      : {rows} rows × {cols} cols
# - Numeric    : {num_cols}
# - Categorical: {cat_cols}
# - Datetime   : {dt_cols}
# - Missing    : {dq.get("overall_missing_pct", 0)}% overall
# - Duplicates : {dq.get("duplicate_rows", 0)} rows

# NUMERIC STATS (mean / std / min / max):
# {json.dumps(num_desc_compact, indent=2)}

# OUTLIERS (IQR method — count of outlier rows):
# {json.dumps(outlier_summary, indent=2) if outlier_summary else "None detected"}

# NOTABLE SKEWNESS (|skew| > 1):
# {json.dumps(skew_notable, indent=2) if skew_notable else "None"}

# STRONG CORRELATIONS (|r| >= 0.3):
# {json.dumps(corr, indent=2) if corr else "None"}

# TOP CATEGORIES (top 5 per col):
# {json.dumps(top_cats, indent=2)}

# DATETIME RANGES:
# {json.dumps(dt_ranges, indent=2) if dt_ranges else "None"}

# SAMPLE ROWS (first 15 rows, first 12 cols):
# {json.dumps(sample_rows, indent=2)}
# """.strip()

#     # ────────────────────────────────────────────────────────────────
#     # 1. Data Insights
#     # ────────────────────────────────────────────────────────────────
#     def generate_insights(self, summary: Dict[str, Any]) -> Dict[str, str]:
#         """Per-sheet analytical insights grounded in actual data."""
#         out: Dict[str, str] = {}
#         for sheet in self._sheet_names(summary):
#             info    = self._sheet_info(summary, sheet)
#             context = self._build_context(info)

#             prompt = f"""
# You are a senior data analyst. Analyze the dataset profile below and generate
# exactly 15 bullet-point insights grounded strictly in the numbers provided.
# Do NOT invent values not present in the data.

# {context}

# OUTPUT FORMAT — exactly 15 bullets, each on its own line:
# - **<Short Heading>**: <1-2 sentence finding with actual column names and numbers>

# COVER ALL of these themes (at least one bullet each):
# 1. Dataset size and scope
# 2. Missing data — which columns, how much
# 3. Duplicate rows — impact on analysis
# 4. Numeric distributions — mean, std, min, max for key columns
# 5. Outliers — which columns, how many rows affected
# 6. Skewness — which columns are heavily skewed and what it implies
# 7. Correlations — which pairs, direction, strength
# 8. Category dominance — which category leads and by how much
# 9. Rare categories — categories with very few occurrences
# 10. Time trends — date range, span, any gaps (only if datetime cols exist)
# 11. Data quality — overall assessment
# 12. Column with most missing data
# 13. Most varied numeric column (highest std relative to mean)
# 14. Strongest correlation finding
# 15. One actionable data cleaning recommendation
# """.strip()

#             try:
#                 text = self._safe_completion(
#                     messages=[
#                         {"role": "system", "content": "You are a precise data analyst. Only reference values present in the data provided. Never hallucinate numbers."},
#                         {"role": "user", "content": prompt},
#                     ],
#                     max_tokens=900,
#                     temperature=0.3,
#                 )
#                 out[sheet] = (text or "").strip()
#             except Exception as e:
#                 out[sheet] = f"Insight generation failed: {e}"
#         return out

#     # ────────────────────────────────────────────────────────────────
#     # 2. Business Insights
#     # ────────────────────────────────────────────────────────────────
#     def generate_business_insights(self, summary: Dict[str, Any]) -> Dict[str, str]:
#         """Actionable business insights grounded in data patterns."""
#         out: Dict[str, str] = {}
#         for sheet in self._sheet_names(summary):
#             info    = self._sheet_info(summary, sheet)
#             context = self._build_context(info)

#             prompt = f"""
# You are a senior business strategist with strong data literacy.
# Using the dataset profile below, generate exactly 6 business insights.
# Each insight must be actionable, reference specific columns and values,
# and explain the business implication clearly.

# {context}

# OUTPUT FORMAT — exactly 6 bullets:
# - **<Business Theme>**: <2-3 sentence insight explaining the pattern,
#   its business implication, and one recommended action>

# THEMES TO COVER:
# 1. Revenue / volume driver — which category or segment dominates
# 2. Risk or anomaly — outliers or skewed distributions that need attention
# 3. Data reliability — missing data or duplicates affecting decisions
# 4. Correlation opportunity — two variables that move together and what to exploit
# 5. Underperforming segment — smallest category and what it signals
# 6. Time-based opportunity — trend or seasonality if datetime data exists,
#    otherwise a segmentation opportunity from categorical data
# """.strip()

#             try:
#                 text = self._safe_completion(
#                     messages=[
#                         {"role": "system", "content": "You are a precise business analyst. Ground every insight in the data provided. Never invent numbers."},
#                         {"role": "user", "content": prompt},
#                     ],
#                     max_tokens=700,
#                     temperature=0.3,
#                 )
#                 out[sheet] = (text or "").strip()
#             except Exception as e:
#                 out[sheet] = f"Business insight generation failed: {e}"
#         return out

#     # ────────────────────────────────────────────────────────────────
#     # 3. Executive Summary
#     # ────────────────────────────────────────────────────────────────
#     def generate_exec_summary(self, summary: Dict[str, Any]) -> str:
#         """High-level executive summary with actual data statistics."""
#         meta        = summary.get("metadata", {})
#         sheet_names = self._sheet_names(summary)

#         # Build a compact per-sheet stat block
#         sheet_stats = {}
#         for sheet in sheet_names:
#             info = self._sheet_info(summary, sheet)
#             rows, cols = info.get("shape", (0, 0))
#             dq = info.get("data_quality_notes", {})
#             sheet_stats[sheet] = {
#                 "rows": rows,
#                 "cols": cols,
#                 "numeric_cols": len(info.get("numeric_cols", [])),
#                 "categorical_cols": len(info.get("categorical_cols", [])),
#                 "datetime_cols": len(info.get("datetime_cols", [])),
#                 "missing_pct": dq.get("overall_missing_pct", 0),
#                 "duplicates": dq.get("duplicate_rows", 0),
#                 "outlier_cols": [
#                     col for col, d in info.get("outliers", {}).items()
#                     if d.get("count", 0) > 0
#                 ],
#                 "datetime_ranges": info.get("datetime_ranges", {}),
#             }

#         prompt = f"""
# You are a senior executive analyst preparing a one-page summary for leadership.
# Using the dataset statistics below, write exactly 5 bullet points.
# Every bullet must reference actual numbers from the data.

# FILE: {meta.get("file_name")}
# SHEETS: {sheet_names}

# PER-SHEET STATISTICS:
# {json.dumps(sheet_stats, indent=2)}

# OUTPUT FORMAT — exactly 5 bullets:
# - **<Topic>**: <1-2 sentences with specific numbers>

# COVER:
# 1. Overall dataset size — total rows, cols, sheets
# 2. Data completeness — missing % and duplicate count across sheets
# 3. Key numeric scope — number of measurable variables and any outlier flags
# 4. Categorical breadth — number of categorical dimensions available
# 5. Time coverage — date range and span if datetime exists,
#    otherwise highlight the most important structural observation
# """.strip()

#         try:
#             text = self._safe_completion(
#                 messages=[
#                     {"role": "system", "content": "You are a concise executive analyst. Use only numbers from the data provided."},
#                     {"role": "user", "content": prompt},
#                 ],
#                 max_tokens=400,
#                 temperature=0.2,
#             )
#             return (text or "").strip()
#         except Exception as e:
#             return f"Executive summary generation failed: {e}"

#     # ────────────────────────────────────────────────────────────────
#     # 4. Chart Plan
#     # ────────────────────────────────────────────────────────────────
#     def generate_chart_plan(self, summary: dict) -> dict:
#         """
#         Smart chart plan — uses outlier, skewness, correlation, and
#         datetime data to pick the most revealing chart for each column.
#         """
#         sheets = summary.get("sheets") or summary

#         brief = {}
#         for s, info in sheets.items():
#             num_cols  = info.get("numeric_cols", [])
#             cat_cols  = info.get("categorical_cols", [])
#             dt_cols   = info.get("datetime_cols", [])
#             outliers  = {
#                 col: d["count"]
#                 for col, d in info.get("outliers", {}).items()
#                 if d.get("count", 0) > 0
#             }
#             skewed = {
#                 col: val
#                 for col, val in info.get("skewness", {}).items()
#                 if abs(val) > 1
#             }
#             corr = info.get("corr", {})
#             dt_ranges = info.get("datetime_ranges", {})
#             top_cats  = info.get("top_categories", {})

#             brief[s] = {
#                 "numeric_cols"     : num_cols[:8],
#                 "categorical_cols" : cat_cols[:6],
#                 "datetime_cols"    : dt_cols,
#                 "outlier_cols"     : list(outliers.keys()),
#                 "skewed_cols"      : list(skewed.keys()),
#                 "has_correlation"  : bool(corr),
#                 "corr_pairs"       : [
#                     [col, list(pairs.keys())[0]]
#                     for col, pairs in corr.items()
#                     if pairs
#                 ][:3],
#                 "has_datetime"     : bool(dt_cols),
#                 "top_cat_cols"     : list(top_cats.keys())[:4],
#                 "sample_rows"      : info.get("sample_rows", [])[:3],
#             }

#         prompt = f"""
# You are a data visualization expert. Return ONLY valid JSON — no explanation, no markdown.

# For each sheet, create a chart plan with 8-10 charts that best reveal
# the dataset's patterns, outliers, distributions, and relationships.

# SMART RULES:
# - For columns in outlier_cols → use "box" chart (shows outliers clearly)
# - For columns in skewed_cols  → use "hist" with more bins (shows skew)
# - If has_correlation is true  → use "heatmap" for the correlation matrix
# - For corr_pairs              → use "scatter" for each pair
# - For categorical cols        → use "bar" for high-cardinality, "pie" for low (<=6 unique)
# - If has_datetime is true     → use "line" chart with datetime on x-axis
# - Always include one "heatmap" if any numeric cols exist

# CHART TYPES AVAILABLE:
# - "hist"    : numeric distribution  → needs: col, bins
# - "box"     : outliers & spread     → needs: col
# - "bar"     : category counts       → needs: col, top_n
# - "pie"     : category proportions  → needs: col, top_n (use only if <=6 categories)
# - "heatmap" : correlation matrix    → no col needed
# - "scatter" : relationship between 2 numeric cols → needs: col_x, col_y
# - "line"    : trend over time       → needs: col_x (datetime), col_y (numeric)

# OUTPUT SCHEMA:
# {{
#   "<sheet_name>": [
#     {{
#       "type"   : "<chart_type>",
#       "col"    : "<column_name>",
#       "col_x"  : "<x_column>",
#       "col_y"  : "<y_column>",
#       "bins"   : <int>,
#       "top_n"  : <int>,
#       "title"  : "<human readable title>"
#     }}
#   ]
# }}

# CONSTRAINTS:
# - Use only columns that exist in the data
# - No duplicate chart+column combinations
# - Titles must be descriptive and human-readable
# - For heatmap, scatter, line: set "col" to null

# DATA:
# {json.dumps(brief, indent=2)}
# """.strip()

#         try:
#             text = self._safe_completion(
#                 messages=[
#                     {"role": "system", "content": "You are a chart planning expert. Return only valid JSON. No markdown, no explanation."},
#                     {"role": "user", "content": prompt},
#                 ],
#                 max_tokens=1000,
#                 temperature=0.2,
#             )
#             # strip markdown fences if model adds them
#             clean = text.strip()
#             if clean.startswith("```"):
#                 clean = clean.split("```")[1]
#                 if clean.startswith("json"):
#                     clean = clean[4:]
#             plan = json.loads(clean.strip())
#             return plan
#         except JSONDecodeError as je:
#             raise RuntimeError(f"Chart plan JSON parse error: {je}\nRaw output:\n{text[:2000]}")
#         except Exception as e:
#             raise RuntimeError(f"Chart plan generation failed: {e}")




# insight_agent.py
from typing import Dict, Any, List
import json
from json import JSONDecodeError

from llm_client import get_llm_client


class InsightAgent:
    def __init__(self):
        self.client, self.model_name, self.provider = get_llm_client()

    def _safe_completion(
        self,
        messages,
        max_tokens=500,
        temperature=0.7,
        retries=3,
        backoff_base=2,
    ):
        last_exc = None
        for attempt in range(retries):
            try:
                j = self.client.create_chat(
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                return j["choices"][0]["message"]["content"].strip()
            except Exception as e:
                last_exc = e
                import time
                wait = min(backoff_base ** attempt, 30)
                print(
                    f"[InsightAgent] error (attempt {attempt+1}/{retries}): "
                    f"{e}. retry in {wait}s..."
                )
                time.sleep(wait)
        raise RuntimeError(
            f"_safe_completion failed after {retries} attempts. "
            f"Last error: {last_exc}"
        )

    @staticmethod
    def _sheet_names(summary: Dict[str, Any]) -> List[str]:
        base = summary.get("sheets") or summary
        return [
            k for k in base.keys()
            # skip internal keys and empty sheets
            if not str(k).startswith("_")
            and not base[k].get("_empty", False)
        ]

    @staticmethod
    def _sheet_info(summary: Dict[str, Any], sheet: str) -> Dict[str, Any]:
        return (summary.get("sheets") or summary).get(sheet, {})

    def _prompt_for_sheet(self, sheet: str, info: Dict[str, Any]) -> str:
        rows, cols = info.get("shape", (0, 0))
        num_cols = info.get("numeric_cols", [])
        cat_cols = info.get("categorical_cols", [])
        dt_cols = info.get("datetime_cols", [])
        top_cats = info.get("top_categories", {})
        num_desc = info.get("numeric_describe", {})
        missing = info.get("missing_by_col", {})
        outliers = info.get("outliers", {})
        skewness = info.get("skewness", {})
        dq = info.get("data_quality_notes", {})
        sample_rows = info.get("sample_rows", [])[:10]

        # only include top_cats for first 8 columns to keep prompt short
        top_cats_trimmed = dict(list(top_cats.items())[:8])

        return f"""
You are a senior data analyst. Generate exactly 14 bullet-point insights
based ONLY on the actual data provided below. Do NOT invent statistics.
If a section has no data, skip it.

SHEET: {sheet}
- shape: {rows} rows x {cols} cols
- numeric_cols (truly numeric): {num_cols}
- categorical_cols: {cat_cols}
- datetime_cols: {dt_cols}
- missing_by_col: {json.dumps(missing)}
- duplicate_rows: {dq.get('duplicate_rows', 0)}
- numeric_describe: {json.dumps(num_desc)}
- skewness: {json.dumps(skewness)}
- outliers: {json.dumps(outliers)}
- top_categories (first 8 cols): {json.dumps(top_cats_trimmed)}

SAMPLE ROWS (first 10):
{json.dumps(sample_rows, indent=2)}

FORMAT — each bullet:
- **Heading**: 1-2 line explanation referencing actual column names and
  real values from the data above. Never invent numbers.

COVER (only sections with actual data):
1. Dataset size and scope
2. Missing data — which columns, how much
3. Duplicate rows — impact on analysis
4. Numeric distributions — mean, std, min, max for key columns
5. Outliers — which columns, how many rows affected
6. Skewness — which columns are heavily skewed and what it implies
7. Correlations — which pairs, direction, strength
8. Category dominance — which category leads and by how much
9. Rare categories — categories with very few occurrences
10. Data quality — overall assessment
11. Column with most missing data
12. Most varied numeric column (highest std relative to mean)
13. Strongest correlation finding
14. One actionable data cleaning recommendation
        """.strip()

    def generate_insights(self, summary: Dict[str, Any]) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for sheet in self._sheet_names(summary):
            info = self._sheet_info(summary, sheet)
            prompt = self._prompt_for_sheet(sheet, info)
            try:
                text = self._safe_completion(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a precise data analyst. "
                                       "Only use facts from the data provided. "
                                       "Never hallucinate statistics.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=700,
                    temperature=0.3,  # lower = more factual, less creative
                )
                out[sheet] = (text or "").strip()
            except Exception as e:
                out[sheet] = f"Insight generation failed: {e}"
        return out

    def generate_business_insights(
        self, summary: Dict[str, Any]
    ) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for sheet in self._sheet_names(summary):
            info = self._sheet_info(summary, sheet)
            rows, cols = info.get("shape", (0, 0))
            num_cols = info.get("numeric_cols", [])
            cat_cols = info.get("categorical_cols", [])
            top_cats = info.get("top_categories", {})
            sample_rows = info.get("sample_rows", [])[:10]

            prompt = f"""
You are a senior business strategist. Based ONLY on the data below,
generate 5-6 narrative business insights. Each must be actionable and
tied to actual values in the data. Do NOT invent statistics.

SHEET: {sheet}
- shape: {rows} rows x {cols} cols
- numeric_cols: {num_cols}
- categorical_cols: {cat_cols}
- top_categories: {json.dumps(dict(list(top_cats.items())[:8]))}

SAMPLE ROWS (first 10):
{json.dumps(sample_rows, indent=2)}

FORMAT:
- Insight 1: ...
- Insight 2: ...
...
            """.strip()

            try:
                text = self._safe_completion(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a precise business analyst. "
                                       "Only reference facts from the data. "
                                       "Never hallucinate.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=600,
                    temperature=0.3,
                )
                out[sheet] = (text or "").strip()
            except Exception as e:
                out[sheet] = f"Business insight generation failed: {e}"
        return out

    def generate_exec_summary(self, summary: Dict[str, Any]) -> str:
        meta = summary.get("metadata", {})
        sheet_names = self._sheet_names(summary)

        # build a compact per-sheet profile to anchor the summary
        sheet_profiles = []
        for sheet in sheet_names:
            info = self._sheet_info(summary, sheet)
            rows, cols = info.get("shape", (0, 0))
            n_num = len(info.get("numeric_cols", []))
            n_cat = len(info.get("categorical_cols", []))
            n_dt = len(info.get("datetime_cols", []))
            dq = info.get("data_quality_notes", {})
            sheet_profiles.append(
                f"  - {sheet}: {rows}×{cols}, "
                f"numeric={n_num}, categorical={n_cat}, datetime={n_dt}, "
                f"missing={dq.get('overall_missing_pct', 0)}%, "
                f"duplicates={dq.get('duplicate_rows', 0)}"
            )

        prompt = f"""
You are a senior executive analyst. Write 4-5 bullet points summarizing
this dataset based ONLY on the facts below. Do NOT invent numbers.

FILE: {meta.get('file_name')}
TOTAL SHEETS: {meta.get('sheet_count')}
NON-EMPTY SHEETS: {sheet_names}

PER-SHEET PROFILES:
{chr(10).join(sheet_profiles)}

Each bullet should cover one of:
- Overall size and scope
- Key column types present
- Data quality observations
- Broad patterns visible in the data
        """.strip()

        try:
            text = self._safe_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise executive analyst. "
                                   "Only use the facts provided.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=400,
                temperature=0.3,
            )
            return (text or "").strip()
        except Exception as e:
            return f"Executive summary generation failed: {e}"

    def generate_chart_plan(self, summary: dict) -> dict:
        sheets = summary.get("sheets") or summary

        # only include non-empty sheets in the brief
        brief = {}
        for s, info in sheets.items():
            if info.get("_empty"):
                continue
            brief[s] = {
                "numeric": info.get("numeric_cols", [])[:6],
                "categorical": info.get("categorical_cols", [])[:6],
                "has_corr": bool(info.get("corr")),
                "sample_rows": info.get("sample_rows", [])[:3],
            }

        if not brief:
            return {}

        prompt = f"""
Return ONLY valid JSON — no explanation, no markdown, no backticks.

For each sheet propose up to 6 meaningful charts.

Chart types allowed:
- "bar": categorical column frequency (needs "col", "top_n")
- "pie": categorical proportions (needs "col", "top_n")
- "hist": truly numeric column distribution (needs "col", "bins")
- "box": truly numeric column outliers (needs "col")
- "heatmap": correlations — only if has_corr is true
- "scatter": two truly numeric columns (needs "col_x", "col_y")

IMPORTANT:
- Only use "hist", "box", "scatter" for columns listed under "numeric"
- Only use "bar", "pie" for columns listed under "categorical"
- Only include "heatmap" if has_corr is true
- Use only columns that actually exist in the data
- Titles must be human-readable

Output schema:
{{
  "<sheet_name>": [
    {{"type": "bar", "col": "Religion", "top_n": 5, "title": "Religion Distribution"}},
    {{"type": "pie", "col": "martal status", "top_n": 4, "title": "Marital Status Breakdown"}}
  ]
}}

Data:
{json.dumps(brief, indent=2)}
        """.strip()

        try:
            text = self._safe_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "Return only valid JSON. No markdown, "
                                   "no backticks, no explanation.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=600,
                temperature=0.1,  # very low — we need strict JSON
            )

            # strip any accidental markdown fences the model adds
            clean = text.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            clean = clean.strip()

            return json.loads(clean)

        except JSONDecodeError as je:
            raise RuntimeError(
                f"Chart plan JSON parse error: {je}\n"
                f"Raw model output:\n{text[:2000]}"
            )
        except Exception as e:
            raise RuntimeError(f"Chart plan generation failed: {e}")