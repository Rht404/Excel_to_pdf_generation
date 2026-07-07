# from pathlib import Path
# import pandas as pd

# BASE_DIR = Path(__file__).resolve().parent.parent
# OUTPUTS_DIR = BASE_DIR / "outputs"
# OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# def safe_describe(df: pd.DataFrame) -> pd.DataFrame:
#     """Return describe safely even when datetime columns exist."""
#     try:
#         return df.describe(include="all", datetime_is_numeric=True)
#     except TypeError:
#         non_dt = df.select_dtypes(exclude=["datetime", "datetime64[ns]", "datetimetz"])
#         return non_dt.describe(include="all")

# class DataAgent:
#     def process(self, file_path: str) -> dict:
#         """Reads Excel, summarizes each sheet, and returns structured output with raw data + metadata."""
#         xls = pd.ExcelFile(file_path)
#         sheets_summary = {}
#         dataframes = {}

#         # Dataset-level metadata
#         dataset_metadata = {
#             "file_name": Path(file_path).name,
#             "sheet_count": len(xls.sheet_names),
#         }

#         for sheet in xls.sheet_names:
#             df = pd.read_excel(xls, sheet_name=sheet)
#             dataframes[sheet] = df  # keep raw DataFrame

#             numeric_cols = [
#                 c for c in df.select_dtypes(include="number").columns
#                 if not str(c).lower().endswith(("id", "_id"))
#             ]
#             categorical_cols = df.select_dtypes(exclude=["number", "datetime"]).columns.tolist()
#             datetime_cols = df.select_dtypes(include=["datetime", "datetime64[ns]", "datetimetz"]).columns.tolist()

#             missing_pct = (df.isna().mean() * 100).round(1).to_dict()

#             corr = {}
#             if numeric_cols:
#                 corr_df = df[numeric_cols].corr(numeric_only=True).round(2)
#                 keep = numeric_cols[:12]
#                 corr = corr_df.loc[keep, keep].to_dict()

#             top_categories = {}
#             for c in categorical_cols[:6]:
#                 vc = df[c].astype(str).value_counts(dropna=True).head(5)
#                 top_categories[c] = [(k, int(v)) for k, v in vc.items()]

#             num_desc = df[numeric_cols].describe().round(2).to_dict() if numeric_cols else {}

#             preview_cols = df.columns[:8].tolist()
#             sample_rows = (
#                 df[preview_cols].head(20).astype(object).fillna("").astype(str).to_dict(orient="records")
#             )

#             # Column definitions (types + unique counts)
#             col_defs = {}
#             for col in df.columns:
#                 col_defs[col] = {
#                     "dtype": str(df[col].dtype),
#                     "unique_count": int(df[col].nunique(dropna=True)),
#                 }

#             # Notes on data quality
#             total_missing_pct = round(df.isna().mean().mean() * 100, 1)

#             sheets_summary[sheet] = {
#                 "shape": df.shape,
#                 "columns": list(df.columns),
#                 "numeric_cols": numeric_cols,
#                 "categorical_cols": categorical_cols,
#                 "datetime_cols": datetime_cols,
#                 "missing_by_col": missing_pct,
#                 "top_categories": top_categories,
#                 "numeric_describe": num_desc,
#                 "corr": corr,
#                 "sample_rows": sample_rows,
#                 "column_definitions": col_defs,
#                 "data_quality_notes": {
#                     "overall_missing_pct": total_missing_pct
#                 },
#             }

#         return {
#             "sheets": sheets_summary,
#             "sheet_names": list(sheets_summary.keys()),
#             "dataframes": dataframes,
#             "metadata": dataset_metadata,
#         }



# from pathlib import Path
# import pandas as pd

# BASE_DIR = Path(__file__).resolve().parent.parent
# OUTPUTS_DIR = BASE_DIR / "outputs"
# OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


# def safe_describe(df: pd.DataFrame) -> pd.DataFrame:
#     """Return describe safely even when datetime columns exist."""
#     try:
#         return df.describe(include="all", datetime_is_numeric=True)
#     except TypeError:
#         non_dt = df.select_dtypes(exclude=["datetime", "datetime64[ns]", "datetimetz"])
#         return non_dt.describe(include="all")


# class DataAgent:
#     def process(self, file_path: str) -> dict:
#         """Reads Excel, summarizes each sheet, and returns structured output with raw data + metadata."""
#         xls = pd.ExcelFile(file_path)
#         sheets_summary = {}
#         dataframes = {}

#         # Dataset-level metadata
#         dataset_metadata = {
#             "file_name": Path(file_path).name,
#             "sheet_count": len(xls.sheet_names),
#         }

#         for sheet in xls.sheet_names:
#             df = pd.read_excel(xls, sheet_name=sheet)
#             dataframes[sheet] = df  # keep raw DataFrame

#             # ── column type buckets ──────────────────────────────────────────
#             numeric_cols = [
#                 c for c in df.select_dtypes(include="number").columns
#                 if not str(c).lower().endswith(("id", "_id"))
#             ]
#             categorical_cols = df.select_dtypes(
#                 exclude=["number", "datetime"]
#             ).columns.tolist()
#             datetime_cols = df.select_dtypes(
#                 include=["datetime", "datetime64[ns]", "datetimetz"]
#             ).columns.tolist()

#             # ── missing values ───────────────────────────────────────────────
#             missing_pct = (df.isna().mean() * 100).round(1).to_dict()
#             total_missing_pct = round(df.isna().mean().mean() * 100, 1)

#             # ── duplicate rows ───────────────────────────────────────────────
#             duplicate_count = int(df.duplicated().sum())

#             # ── correlation — all numeric cols, filter weak pairs ────────────
#             corr = {}
#             if numeric_cols:
#                 corr_df = df[numeric_cols].corr(numeric_only=True).round(2)
#                 corr_filtered = {}
#                 for col in corr_df.columns:
#                     corr_filtered[col] = {
#                         other: val
#                         for other, val in corr_df[col].items()
#                         if other != col and abs(val) >= 0.3
#                     }
#                 corr = corr_filtered

#             # ── top categories — ALL categorical cols ────────────────────────
#             top_categories = {}
#             for c in categorical_cols:
#                 vc = df[c].astype(str).value_counts(dropna=True).head(5)
#                 top_categories[c] = [(k, int(v)) for k, v in vc.items()]

#             # ── numeric stats ────────────────────────────────────────────────
#             num_desc = (
#                 df[numeric_cols].describe().round(2).to_dict()
#                 if numeric_cols else {}
#             )

#             # ── skewness & kurtosis ──────────────────────────────────────────
#             skewness = (
#                 df[numeric_cols].skew().round(2).to_dict()
#                 if numeric_cols else {}
#             )
#             kurtosis = (
#                 df[numeric_cols].kurt().round(2).to_dict()
#                 if numeric_cols else {}
#             )

#             # ── outliers (IQR method) ────────────────────────────────────────
#             outliers = {}
#             for c in numeric_cols:
#                 q1 = df[c].quantile(0.25)
#                 q3 = df[c].quantile(0.75)
#                 iqr = q3 - q1
#                 lower = q1 - 1.5 * iqr
#                 upper = q3 + 1.5 * iqr
#                 outlier_count = int(((df[c] < lower) | (df[c] > upper)).sum())
#                 outliers[c] = {
#                     "count": outlier_count,
#                     "lower_bound": round(float(lower), 2),
#                     "upper_bound": round(float(upper), 2),
#                 }

#             # ── datetime ranges ──────────────────────────────────────────────
#             dt_ranges = {}
#             for c in datetime_cols:
#                 try:
#                     dt_ranges[c] = {
#                         "min": str(df[c].min()),
#                         "max": str(df[c].max()),
#                         "range_days": int((df[c].max() - df[c].min()).days),
#                         "null_count": int(df[c].isna().sum()),
#                     }
#                 except Exception:
#                     dt_ranges[c] = {}

#             # ── sample rows — ALL columns, first 20 rows ─────────────────────
#             sample_rows = (
#                 df.head(20).astype(object).fillna("").astype(str).to_dict(orient="records")
#             )

#             # ── column definitions ───────────────────────────────────────────
#             col_defs = {}
#             for col in df.columns:
#                 col_defs[col] = {
#                     "dtype": str(df[col].dtype),
#                     "unique_count": int(df[col].nunique(dropna=True)),
#                 }

#             # ── assemble sheet summary ───────────────────────────────────────
#             sheets_summary[sheet] = {
#                 "shape": df.shape,
#                 "columns": list(df.columns),
#                 "numeric_cols": numeric_cols,
#                 "categorical_cols": categorical_cols,
#                 "datetime_cols": datetime_cols,
#                 "missing_by_col": missing_pct,
#                 "top_categories": top_categories,
#                 "numeric_describe": num_desc,
#                 "skewness": skewness,
#                 "kurtosis": kurtosis,
#                 "outliers": outliers,
#                 "corr": corr,
#                 "datetime_ranges": dt_ranges,
#                 "sample_rows": sample_rows,
#                 "column_definitions": col_defs,
#                 "data_quality_notes": {
#                     "overall_missing_pct": total_missing_pct,
#                     "duplicate_rows": duplicate_count,
#                 },
#             }

#         return {
#             "sheets": sheets_summary,
#             "sheet_names": list(sheets_summary.keys()),
#             "dataframes": dataframes,
#             "metadata": dataset_metadata,
#         }



from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def safe_describe(df: pd.DataFrame) -> pd.DataFrame:
    try:
        return df.describe(include="all", datetime_is_numeric=True)
    except TypeError:
        non_dt = df.select_dtypes(exclude=["datetime", "datetime64[ns]", "datetimetz"])
        return non_dt.describe(include="all")


def _is_truly_numeric(series: pd.Series, min_valid: int = 5) -> bool:
    """
    Returns True only if the column has at least `min_valid` values
    that can actually be coerced to a number.
    This prevents text-category columns like 'age' = '20-30' from
    being listed as numeric_cols and confusing the LLM.
    """
    coerced = pd.to_numeric(series, errors="coerce")
    return coerced.notna().sum() >= min_valid


class DataAgent:
    def process(self, file_path: str) -> dict:
        xls = pd.ExcelFile(file_path)
        sheets_summary = {}
        dataframes = {}

        dataset_metadata = {
            "file_name": Path(file_path).name,
            "sheet_count": len(xls.sheet_names),
        }

        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)

            # ── drop unnamed index columns (pandas artifact) ─────────────────
            unnamed_cols = [
                c for c in df.columns
                if str(c).startswith("Unnamed:")
            ]
            df = df.drop(columns=unnamed_cols)

            # ── skip truly empty sheets ──────────────────────────────────────
            if df.empty or df.shape[0] == 0:
                sheets_summary[sheet] = {"_empty": True}
                continue

            dataframes[sheet] = df

            # ── column type buckets ──────────────────────────────────────────
            # Only mark a column as numeric if it truly holds numbers
            numeric_cols = [
                c for c in df.columns
                if not str(c).lower().endswith(("id", "_id"))
                and _is_truly_numeric(df[c])
            ]
            categorical_cols = [
                c for c in df.select_dtypes(
                    exclude=["number", "datetime"]
                ).columns.tolist()
                # also include columns that look numeric by dtype but are
                # actually text-category (the ones we excluded above)
                if c not in numeric_cols
            ] + [
                c for c in df.select_dtypes(include="number").columns
                if c not in numeric_cols
            ]
            # deduplicate while preserving order
            seen = set()
            categorical_cols = [
                c for c in categorical_cols
                if not (c in seen or seen.add(c))
            ]
            datetime_cols = df.select_dtypes(
                include=["datetime", "datetime64[ns]", "datetimetz"]
            ).columns.tolist()

            # ── missing values ───────────────────────────────────────────────
            missing_pct = (df.isna().mean() * 100).round(1).to_dict()
            total_missing_pct = round(df.isna().mean().mean() * 100, 1)

            # ── duplicate rows ───────────────────────────────────────────────
            duplicate_count = int(df.duplicated().sum())

            # ── correlation — only truly numeric cols ────────────────────────
            corr = {}
            if numeric_cols:
                corr_df = df[numeric_cols].corr(numeric_only=True).round(2)
                for col in corr_df.columns:
                    corr[col] = {
                        other: val
                        for other, val in corr_df[col].items()
                        if other != col and abs(val) >= 0.3
                    }

            # ── top categories ───────────────────────────────────────────────
            top_categories = {}
            for c in categorical_cols:
                vc = df[c].astype(str).value_counts(dropna=True).head(5)
                top_categories[c] = [(k, int(v)) for k, v in vc.items()]

            # ── numeric stats ────────────────────────────────────────────────
            num_desc = (
                df[numeric_cols].describe().round(2).to_dict()
                if numeric_cols else {}
            )

            # ── skewness & kurtosis ──────────────────────────────────────────
            skewness = (
                df[numeric_cols].skew().round(2).to_dict()
                if numeric_cols else {}
            )
            kurtosis = (
                df[numeric_cols].kurt().round(2).to_dict()
                if numeric_cols else {}
            )

            # ── outliers (IQR method) ────────────────────────────────────────
            outliers = {}
            for c in numeric_cols:
                q1 = df[c].quantile(0.25)
                q3 = df[c].quantile(0.75)
                iqr = q3 - q1
                lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                outliers[c] = {
                    "count": int(((df[c] < lower) | (df[c] > upper)).sum()),
                    "lower_bound": round(float(lower), 2),
                    "upper_bound": round(float(upper), 2),
                }

            # ── datetime ranges ──────────────────────────────────────────────
            dt_ranges = {}
            for c in datetime_cols:
                try:
                    dt_ranges[c] = {
                        "min": str(df[c].min()),
                        "max": str(df[c].max()),
                        "range_days": int((df[c].max() - df[c].min()).days),
                        "null_count": int(df[c].isna().sum()),
                    }
                except Exception:
                    dt_ranges[c] = {}

            # ── sample rows — all columns, first 20 rows ─────────────────────
            sample_rows = (
                df.head(20)
                .astype(object)
                .fillna("")
                .astype(str)
                .to_dict(orient="records")
            )

            # ── column definitions ───────────────────────────────────────────
            col_defs = {}
            for col in df.columns:
                col_defs[col] = {
                    "dtype": str(df[col].dtype),
                    "unique_count": int(df[col].nunique(dropna=True)),
                }

            sheets_summary[sheet] = {
                "shape": df.shape,
                "columns": list(df.columns),
                "numeric_cols": numeric_cols,
                "categorical_cols": categorical_cols,
                "datetime_cols": datetime_cols,
                "missing_by_col": missing_pct,
                "top_categories": top_categories,
                "numeric_describe": num_desc,
                "skewness": skewness,
                "kurtosis": kurtosis,
                "outliers": outliers,
                "corr": corr,
                "datetime_ranges": dt_ranges,
                "sample_rows": sample_rows,
                "column_definitions": col_defs,
                "data_quality_notes": {
                    "overall_missing_pct": total_missing_pct,
                    "duplicate_rows": duplicate_count,
                },
            }

        return {
            "sheets": sheets_summary,
            "sheet_names": list(sheets_summary.keys()),
            "dataframes": dataframes,
            "metadata": dataset_metadata,
        }