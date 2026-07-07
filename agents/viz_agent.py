# # viz_agent.py
# import matplotlib.pyplot as plt
# import pandas as pd
# import seaborn as sns
# from pathlib import Path
# import textwrap


# class VizAgent:
#     def __init__(self):
#         sns.set_theme(style="whitegrid")  # global seaborn style

#     def _wrap_labels(self, labels, width=30):
#         """Wrap long labels to multiple lines to avoid overlap in plots."""
#         return [textwrap.fill(str(l), width=width) for l in labels]

#     def create_charts(self, summary: dict, dataframes: dict, chart_plan: dict | None = None) -> dict:
#         """
#         Render charts per the chart_plan using raw dataframes.
#         Supported types: bar, pie, hist, box, heatmap, stacked_bar.
#         Returns {sheet: [ { "path": <image_path>, "description": <text> } ] }.
#         """
#         charts: dict[str, list[dict]] = {}
#         CHARTS_DIR = (Path(__file__).resolve().parent.parent / "outputs" / "charts")
#         CHARTS_DIR.mkdir(parents=True, exist_ok=True)

#         sheets = summary.get("sheets") or summary
#         for sheet, info in sheets.items():
#             df = dataframes.get(sheet)
#             if df is None or df.empty:
#                 continue

#             chart_entries = []
#             plan = (chart_plan or {}).get(sheet, [])

#             for i, spec in enumerate(plan):
#                 t = spec.get("type")
#                 title = spec.get("title", t or "")
#                 description = ""
#                 # pick fig size/dpi
#                 if t == "hist":
#                     fig, ax = plt.subplots(figsize=(8, 5), dpi=200, constrained_layout=True)
#                 else:
#                     fig, ax = plt.subplots(figsize=(7, 5), dpi=200, constrained_layout=True)

#                 try:
#                     if t == "bar":
#                         col = spec.get("col")
#                         if col in df.columns:
#                             top_n = int(spec.get("top_n") or 10)
#                             vc = df[col].astype(str).value_counts().head(top_n)
#                             labels = self._wrap_labels(vc.index, width=24)
#                             sns.barplot(x=vc.index, y=vc.values, palette="Set2", ax=ax)
#                             ax.set_xticks(range(len(labels)))
#                             ax.set_xticklabels(labels, rotation=35, ha='right')
#                             ax.set_title(title)
#                             ax.set_xlabel(col)
#                             ax.set_ylabel("Count")
#                             description = f"Bar chart of {col}: top {top_n} categories by frequency."

#                     elif t == "pie":
#                         col = spec.get("col")
#                         if col in df.columns:
#                             top_n = int(spec.get("top_n") or 6)
#                             vc = df[col].astype(str).value_counts().head(top_n)
#                             labels = self._wrap_labels(vc.index, width=24)
#                             ax.pie(vc.values, labels=labels, autopct="%1.0f%%", startangle=90)
#                             ax.axis('equal')
#                             ax.set_title(title)
#                             description = f"Pie chart of {col}: showing proportion of top {top_n} categories."

#                     elif t == "hist":
#                         col = spec.get("col")
#                         if col in df.columns:
#                             bins = int(spec.get("bins", 20))
#                             sns.histplot(df[col].dropna(), bins=bins, kde=True, ax=ax)
#                             ax.set_title(title)
#                             ax.set_xlabel(col)
#                             ax.set_ylabel("Count")
#                             description = f"Histogram of {col}: distribution with {bins} bins."

#                     elif t == "box":
#                         col = spec.get("col")
#                         if col in df.columns:
#                             sns.boxplot(y=df[col].dropna(), color="lightgreen", ax=ax)
#                             ax.set_title(title)
#                             ax.set_ylabel(col)
#                             description = f"Box plot of {col}: highlights median and outliers."

#                     elif t == "heatmap":
#                         corr = df.corr(numeric_only=True)
#                         if not corr.empty:
#                             sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax, vmin=-1, vmax=1)
#                             ax.set_title(title)
#                             description = "Heatmap of correlations among numeric columns."
#                         else:
#                             plt.close(fig)
#                             continue

#                     elif t == "stacked_bar":
#                         col1, col2 = spec.get("cols", [None, None])
#                         if col1 in df.columns and col2 in df.columns:
#                             ctab = pd.crosstab(df[col1].astype(str), df[col2].astype(str))
#                             ctab.plot(kind="bar", stacked=True, ax=ax, colormap="tab20")
#                             labels = self._wrap_labels(ctab.index, width=24)
#                             ax.set_xticks(range(len(labels)))
#                             ax.set_xticklabels(labels, rotation=35, ha='right')
#                             ax.set_title(title)
#                             description = f"Stacked bar chart of {col1} vs {col2}: shows distribution across categories."

#                     else:
#                         plt.close(fig)
#                         continue

#                     # final layout
#                     fig.tight_layout(pad=1.0)
#                     p = CHARTS_DIR / f"{sheet}_{i}_{t}.png"
#                     fig.savefig(p, bbox_inches='tight', dpi=200)
#                     plt.close(fig)

#                     chart_entries.append({
#                         "path": str(p.resolve()),
#                         "description": description or f"{title} ({t}) chart."
#                     })

#                 except Exception:
#                     try:
#                         plt.close(fig)
#                     except Exception:
#                         pass
#                     continue

#             charts[sheet] = chart_entries

#         return charts




# # viz_agent.py
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# import pandas as pd
# import seaborn as sns
# from pathlib import Path
# import textwrap


# class VizAgent:
#     def __init__(self):
#         sns.set_theme(style="whitegrid")

#     def _wrap_labels(self, labels, width=30):
#         """Wrap long labels to avoid overlap."""
#         return [textwrap.fill(str(l), width=width) for l in labels]

#     def _fig(self, wide=False):
#         """Return a consistently sized figure."""
#         w = 10 if wide else 7
#         return plt.subplots(figsize=(w, 5), dpi=200, constrained_layout=True)

#     def create_charts(
#         self,
#         summary: dict,
#         dataframes: dict,
#         chart_plan: dict | None = None,
#     ) -> dict:
#         """
#         Render charts per the chart_plan using raw dataframes.
#         Supported: bar, pie, hist, box, heatmap, scatter, line, stacked_bar.
#         Returns {sheet: [{"path": <str>, "description": <str>}]}.
#         """
#         charts: dict[str, list[dict]] = {}
#         CHARTS_DIR = (
#             Path(__file__).resolve().parent.parent / "outputs" / "charts"
#         )
#         CHARTS_DIR.mkdir(parents=True, exist_ok=True)

#         sheets = summary.get("sheets") or summary

#         for sheet, info in sheets.items():
#             df = dataframes.get(sheet)
#             if df is None or df.empty:
#                 charts[sheet] = []
#                 continue

#             # ── parse datetime cols so line charts work ──────────────────
#             for col in info.get("datetime_cols", []):
#                 if col in df.columns:
#                     try:
#                         df[col] = pd.to_datetime(df[col], errors="coerce")
#                     except Exception:
#                         pass

#             chart_entries = []
#             plan = (chart_plan or {}).get(sheet, [])

#             for i, spec in enumerate(plan):
#                 t     = spec.get("type", "")
#                 title = spec.get("title", t or "Chart")
#                 col   = spec.get("col")        # may be None for heatmap/scatter/line
#                 col_x = spec.get("col_x")
#                 col_y = spec.get("col_y")
#                 description = ""
#                 fig = None

#                 try:
#                     # ── BAR ─────────────────────────────────────────────────
#                     if t == "bar":
#                         if not col or col not in df.columns:
#                             continue
#                         fig, ax = self._fig()
#                         top_n   = int(spec.get("top_n") or 10)
#                         vc      = df[col].astype(str).value_counts().head(top_n)
#                         labels  = self._wrap_labels(vc.index, width=20)
#                         sns.barplot(x=vc.index, y=vc.values, palette="Set2", ax=ax)
#                         ax.set_xticks(range(len(labels)))
#                         ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8)
#                         ax.set_title(title)
#                         ax.set_xlabel(col)
#                         ax.set_ylabel("Count")
#                         description = (
#                             f"Bar chart of '{col}': top {top_n} categories by frequency. "
#                             f"Most common: '{vc.index[0]}' ({vc.values[0]:,} occurrences)."
#                         )

#                     # ── PIE ─────────────────────────────────────────────────
#                     elif t == "pie":
#                         if not col or col not in df.columns:
#                             continue
#                         fig, ax = self._fig()
#                         top_n  = int(spec.get("top_n") or 6)
#                         vc     = df[col].astype(str).value_counts().head(top_n)
#                         labels = self._wrap_labels(vc.index, width=20)
#                         ax.pie(
#                             vc.values,
#                             labels=labels,
#                             autopct="%1.1f%%",
#                             startangle=90,
#                             colors=sns.color_palette("Set2", len(vc)),
#                         )
#                         ax.axis("equal")
#                         ax.set_title(title)
#                         description = (
#                             f"Pie chart of '{col}': top {top_n} categories. "
#                             f"'{vc.index[0]}' leads with {vc.values[0]/vc.values.sum()*100:.1f}%."
#                         )

#                     # ── HIST ─────────────────────────────────────────────────
#                     elif t == "hist":
#                         if not col or col not in df.columns:
#                             continue
#                         fig, ax = self._fig(wide=True)
#                         bins    = int(spec.get("bins") or 20)
#                         data    = pd.to_numeric(df[col], errors="coerce").dropna()
#                         sns.histplot(data, bins=bins, kde=True, ax=ax, color="#1a237e")
#                         ax.axvline(data.mean(), color="red",    linestyle="--",
#                                    linewidth=1.2, label=f"Mean: {data.mean():.2f}")
#                         ax.axvline(data.median(), color="orange", linestyle="--",
#                                    linewidth=1.2, label=f"Median: {data.median():.2f}")
#                         ax.legend(fontsize=8)
#                         ax.set_title(title)
#                         ax.set_xlabel(col)
#                         ax.set_ylabel("Count")
#                         description = (
#                             f"Histogram of '{col}' ({bins} bins). "
#                             f"Mean: {data.mean():.2f}, Median: {data.median():.2f}, "
#                             f"Std: {data.std():.2f}."
#                         )

#                     # ── BOX ──────────────────────────────────────────────────
#                     elif t == "box":
#                         if not col or col not in df.columns:
#                             continue
#                         fig, ax = self._fig()
#                         data    = pd.to_numeric(df[col], errors="coerce").dropna()
#                         sns.boxplot(y=data, color="lightgreen", ax=ax)
#                         ax.set_title(title)
#                         ax.set_ylabel(col)
#                         q1  = data.quantile(0.25)
#                         q3  = data.quantile(0.75)
#                         iqr = q3 - q1
#                         n_out = int(((data < q1 - 1.5*iqr) | (data > q3 + 1.5*iqr)).sum())
#                         description = (
#                             f"Box plot of '{col}'. "
#                             f"Median: {data.median():.2f}, IQR: {iqr:.2f}, "
#                             f"Outliers detected: {n_out}."
#                         )

#                     # ── HEATMAP ──────────────────────────────────────────────
#                     elif t == "heatmap":
#                         num_df = df.select_dtypes(include="number")
#                         if num_df.empty or num_df.shape[1] < 2:
#                             continue
#                         corr = num_df.corr()
#                         fig, ax = plt.subplots(
#                             figsize=(max(7, corr.shape[1] * 0.8),
#                                      max(5, corr.shape[0] * 0.7)),
#                             dpi=200,
#                             constrained_layout=True,
#                         )
#                         sns.heatmap(
#                             corr, annot=True, fmt=".2f",
#                             cmap="coolwarm", ax=ax,
#                             vmin=-1, vmax=1,
#                             linewidths=0.5,
#                             annot_kws={"size": 8},
#                         )
#                         ax.set_title(title)
#                         ax.tick_params(axis="x", rotation=45, labelsize=8)
#                         ax.tick_params(axis="y", rotation=0,  labelsize=8)
#                         description = (
#                             f"Correlation heatmap of {num_df.shape[1]} numeric columns. "
#                             f"Values range from -1 (perfect negative) to +1 (perfect positive)."
#                         )

#                     # ── SCATTER ──────────────────────────────────────────────
#                     elif t == "scatter":
#                         if not col_x or not col_y:
#                             continue
#                         if col_x not in df.columns or col_y not in df.columns:
#                             continue
#                         fig, ax = self._fig(wide=True)
#                         x = pd.to_numeric(df[col_x], errors="coerce")
#                         y = pd.to_numeric(df[col_y], errors="coerce")
#                         mask = x.notna() & y.notna()
#                         ax.scatter(
#                             x[mask], y[mask],
#                             alpha=0.5, s=20,
#                             color="#1a237e", edgecolors="none",
#                         )
#                         # trend line
#                         if mask.sum() > 1:
#                             import numpy as np
#                             z = np.polyfit(x[mask], y[mask], 1)
#                             p = np.poly1d(z)
#                             x_sorted = x[mask].sort_values()
#                             ax.plot(
#                                 x_sorted, p(x_sorted),
#                                 color="red", linewidth=1.2,
#                                 linestyle="--", label="Trend",
#                             )
#                             ax.legend(fontsize=8)
#                         corr_val = x[mask].corr(y[mask])
#                         ax.set_title(title)
#                         ax.set_xlabel(col_x)
#                         ax.set_ylabel(col_y)
#                         description = (
#                             f"Scatter plot of '{col_x}' vs '{col_y}'. "
#                             f"Correlation: {corr_val:.2f}. "
#                             f"Points plotted: {mask.sum():,}."
#                         )

#                     # ── LINE ─────────────────────────────────────────────────
#                     elif t == "line":
#                         if not col_x or not col_y:
#                             continue
#                         if col_x not in df.columns or col_y not in df.columns:
#                             continue
#                         fig, ax = self._fig(wide=True)
#                         plot_df = df[[col_x, col_y]].copy()
#                         plot_df[col_x] = pd.to_datetime(
#                             plot_df[col_x], errors="coerce"
#                         )
#                         plot_df[col_y] = pd.to_numeric(
#                             plot_df[col_y], errors="coerce"
#                         )
#                         plot_df = (
#                             plot_df.dropna()
#                             .sort_values(col_x)
#                         )
#                         if plot_df.empty:
#                             if fig:
#                                 plt.close(fig)
#                             continue
#                         ax.plot(
#                             plot_df[col_x], plot_df[col_y],
#                             color="#1a237e", linewidth=1.5,
#                         )
#                         ax.fill_between(
#                             plot_df[col_x], plot_df[col_y],
#                             alpha=0.1, color="#1a237e",
#                         )
#                         ax.xaxis.set_major_formatter(
#                             mdates.AutoDateFormatter(mdates.AutoDateLocator())
#                         )
#                         plt.setp(ax.xaxis.get_majorticklabels(),
#                                  rotation=35, ha="right", fontsize=8)
#                         ax.set_title(title)
#                         ax.set_xlabel(col_x)
#                         ax.set_ylabel(col_y)
#                         description = (
#                             f"Line chart of '{col_y}' over '{col_x}'. "
#                             f"Date range: {plot_df[col_x].min().date()} "
#                             f"to {plot_df[col_x].max().date()}. "
#                             f"Points: {len(plot_df):,}."
#                         )

#                     # ── STACKED BAR ──────────────────────────────────────────
#                     elif t == "stacked_bar":
#                         cols = spec.get("cols", [])
#                         if len(cols) < 2:
#                             continue
#                         col1, col2 = cols[0], cols[1]
#                         if col1 not in df.columns or col2 not in df.columns:
#                             continue
#                         fig, ax = self._fig(wide=True)
#                         ctab   = pd.crosstab(
#                             df[col1].astype(str),
#                             df[col2].astype(str),
#                         )
#                         ctab.plot(kind="bar", stacked=True, ax=ax, colormap="tab20")
#                         labels = self._wrap_labels(ctab.index, width=20)
#                         ax.set_xticks(range(len(labels)))
#                         ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8)
#                         ax.set_title(title)
#                         ax.set_xlabel(col1)
#                         ax.set_ylabel("Count")
#                         ax.legend(
#                             title=col2, fontsize=7,
#                             bbox_to_anchor=(1.01, 1), loc="upper left",
#                         )
#                         description = (
#                             f"Stacked bar of '{col1}' vs '{col2}': "
#                             f"shows category distribution across {ctab.shape[0]} groups."
#                         )

#                     else:
#                         # unknown chart type — skip cleanly
#                         continue

#                     # ── save ─────────────────────────────────────────────────
#                     if fig is not None:
#                         p = CHARTS_DIR / f"{sheet}_{i}_{t}.png"
#                         fig.savefig(str(p), bbox_inches="tight", dpi=200)
#                         plt.close(fig)
#                         chart_entries.append({
#                             "path": str(p.resolve()),
#                             "description": description or f"{title} ({t}).",
#                         })

#                 except Exception as exc:
#                     print(f"[VizAgent] chart failed — sheet={sheet} type={t} col={col}: {exc}")
#                     if fig is not None:
#                         try:
#                             plt.close(fig)
#                         except Exception:
#                             pass
#                     continue

#             charts[sheet] = chart_entries

#         return charts




# viz_agent.py
import matplotlib
matplotlib.use("Agg")  # MUST be before any other matplotlib import — fixes GUI thread warning

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path
import textwrap


class VizAgent:
    def __init__(self):
        sns.set_theme(style="whitegrid")

    # ------------------------------------------------------------------ #
    # helpers                                                              #
    # ------------------------------------------------------------------ #

    def _wrap_labels(self, labels, width=20):
        return [textwrap.fill(str(l), width=width) for l in labels]

    def _make_fig(self, w=7):
        """Create a figure using the Agg backend — safe from any thread."""
        return plt.subplots(figsize=(w, 5), dpi=150, constrained_layout=True)

    def _to_numeric_series(self, df: pd.DataFrame, col: str):
        """
        Try to return a clean numeric Series for `col`.
        Returns None if the column does not exist, cannot be coerced to
        numbers, or has fewer than 5 valid values — so callers can safely
        skip non-numeric columns without crashing.
        """
        if col not in df.columns:
            return None
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(s) < 5:
            return None
        return s

    def _save(self, fig, path: Path) -> None:
        fig.savefig(path, bbox_inches="tight", dpi=150)
        plt.close(fig)

    # ------------------------------------------------------------------ #
    # main entry                                                           #
    # ------------------------------------------------------------------ #

    def create_charts(
        self,
        summary: dict,
        dataframes: dict,
        chart_plan: dict | None = None,
    ) -> dict:
        """
        Render charts per the chart_plan using raw dataframes.
        Supported types: bar, pie, hist, box, heatmap, scatter, stacked_bar.
        Returns {sheet: [ { "path": <image_path>, "description": <text> } ] }.
        All chart types guard against missing columns, non-numeric data, and
        empty results so the method is safe for any unknown dataset.
        """
        charts: dict[str, list[dict]] = {}
        CHARTS_DIR = (
            Path(__file__).resolve().parent.parent / "outputs" / "charts"
        )
        CHARTS_DIR.mkdir(parents=True, exist_ok=True)

        sheets = summary.get("sheets") or summary

        for sheet, info in sheets.items():
            df = dataframes.get(sheet)
            if df is None or df.empty:
                continue

            chart_entries = []
            plan = (chart_plan or {}).get(sheet, [])

            for i, spec in enumerate(plan):
                t = spec.get("type", "")
                title = spec.get("title", t)
                path = CHARTS_DIR / f"{sheet}_{i}_{t}.png"
                description = ""

                try:
                    # ── bar ──────────────────────────────────────────────
                    if t == "bar":
                        col = spec.get("col")
                        if col not in df.columns:
                            continue
                        top_n = int(spec.get("top_n") or 10)
                        vc = df[col].astype(str).value_counts().head(top_n)
                        if vc.empty:
                            continue
                        fig, ax = self._make_fig(
                            w=max(7, min(top_n * 0.8, 14))
                        )
                        labels = self._wrap_labels(vc.index, width=20)
                        sns.barplot(
                            x=vc.index,
                            y=vc.values,
                            hue=vc.index,
                            palette="Set2",
                            legend=False,
                            ax=ax,
                        )
                        ax.set_xticks(range(len(labels)))
                        ax.set_xticklabels(
                            labels, rotation=35, ha="right", fontsize=8
                        )
                        ax.set_title(title)
                        ax.set_xlabel(col)
                        ax.set_ylabel("Count")
                        description = (
                            f"Bar chart of '{col}': top {top_n} categories "
                            f"by frequency. Most common: '{vc.index[0]}' "
                            f"({vc.values[0]} occurrences)."
                        )
                        self._save(fig, path)

                    # ── pie ──────────────────────────────────────────────
                    elif t == "pie":
                        col = spec.get("col")
                        if col not in df.columns:
                            continue
                        top_n = int(spec.get("top_n") or 6)
                        vc = df[col].astype(str).value_counts().head(top_n)
                        if vc.empty:
                            continue
                        fig, ax = self._make_fig()
                        labels = self._wrap_labels(vc.index, width=20)
                        ax.pie(
                            vc.values,
                            labels=labels,
                            autopct="%1.1f%%",
                            startangle=90,
                            colors=sns.color_palette("Set2", len(vc)),
                        )
                        ax.axis("equal")
                        ax.set_title(title)
                        pct_lead = vc.values[0] / vc.values.sum() * 100
                        description = (
                            f"Pie chart of '{col}': top {top_n} categories. "
                            f"'{vc.index[0]}' leads with {pct_lead:.1f}%."
                        )
                        self._save(fig, path)

                    # ── hist ─────────────────────────────────────────────
                    elif t == "hist":
                        col = spec.get("col")
                        s = self._to_numeric_series(df, col)
                        if s is None:
                            continue
                        bins = int(spec.get("bins", 20))
                        fig, ax = self._make_fig(w=8)
                        sns.histplot(s, bins=bins, kde=True, ax=ax,
                                     color="steelblue")
                        ax.axvline(
                            s.mean(), color="red", linestyle="--",
                            linewidth=1,
                            label=f"Mean: {s.mean():.2f}",
                        )
                        ax.axvline(
                            s.median(), color="orange", linestyle="--",
                            linewidth=1,
                            label=f"Median: {s.median():.2f}",
                        )
                        ax.legend(fontsize=8)
                        ax.set_title(title)
                        ax.set_xlabel(col)
                        ax.set_ylabel("Count")
                        description = (
                            f"Histogram of '{col}' ({bins} bins). "
                            f"Mean: {s.mean():.2f}, "
                            f"Median: {s.median():.2f}, "
                            f"Std: {s.std():.2f}."
                        )
                        self._save(fig, path)

                    # ── box ──────────────────────────────────────────────
                    elif t == "box":
                        col = spec.get("col")
                        s = self._to_numeric_series(df, col)
                        if s is None:
                            continue
                        q1, q3 = s.quantile(0.25), s.quantile(0.75)
                        iqr = q3 - q1
                        outliers = s[
                            (s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)
                        ]
                        fig, ax = self._make_fig()
                        sns.boxplot(y=s, color="lightgreen", ax=ax)
                        ax.set_title(title)
                        ax.set_ylabel(col)
                        description = (
                            f"Box plot of '{col}'. "
                            f"Median: {s.median():.2f}, "
                            f"IQR: {iqr:.2f}, "
                            f"Outliers detected: {len(outliers)}."
                        )
                        self._save(fig, path)

                    # ── heatmap ──────────────────────────────────────────
                    elif t == "heatmap":
                        numeric_df = df.select_dtypes(include="number")
                        if numeric_df.shape[1] < 2:
                            continue
                        corr = numeric_df.corr()
                        if corr.empty:
                            continue
                        fig, ax = self._make_fig(
                            w=max(7, corr.shape[1])
                        )
                        sns.heatmap(
                            corr,
                            annot=True,
                            cmap="coolwarm",
                            ax=ax,
                            vmin=-1,
                            vmax=1,
                            fmt=".2f",
                            annot_kws={"size": 8},
                        )
                        ax.set_title(title)
                        description = (
                            "Correlation heatmap of numeric columns."
                        )
                        self._save(fig, path)

                    # ── scatter ──────────────────────────────────────────
                    elif t == "scatter":
                        col_x = spec.get("col_x") or spec.get("col")
                        col_y = spec.get("col_y")
                        if not col_x or not col_y:
                            continue
                        sx = self._to_numeric_series(df, col_x)
                        sy = self._to_numeric_series(df, col_y)
                        if sx is None or sy is None:
                            continue
                        aligned = pd.concat(
                            [sx.rename("x"), sy.rename("y")], axis=1
                        ).dropna()
                        if len(aligned) < 5:
                            continue
                        corr_val = aligned["x"].corr(aligned["y"])
                        fig, ax = self._make_fig()
                        ax.scatter(
                            aligned["x"], aligned["y"],
                            alpha=0.6, color="steelblue", s=30,
                        )
                        ax.set_xlabel(col_x)
                        ax.set_ylabel(col_y)
                        ax.set_title(title)
                        description = (
                            f"Scatter plot of '{col_x}' vs '{col_y}'. "
                            f"Correlation: {corr_val:.2f}. "
                            f"Points plotted: {len(aligned)}."
                        )
                        self._save(fig, path)

                    # ── stacked_bar ──────────────────────────────────────
                    elif t == "stacked_bar":
                        cols = spec.get("cols", [None, None])
                        col1, col2 = (cols + [None, None])[:2]
                        if not col1 or not col2:
                            continue
                        if col1 not in df.columns or col2 not in df.columns:
                            continue
                        ctab = pd.crosstab(
                            df[col1].astype(str), df[col2].astype(str)
                        )
                        if ctab.empty:
                            continue
                        fig, ax = self._make_fig(
                            w=max(8, len(ctab) * 0.8)
                        )
                        ctab.plot(
                            kind="bar", stacked=True,
                            ax=ax, colormap="tab20",
                        )
                        labels = self._wrap_labels(ctab.index, width=20)
                        ax.set_xticks(range(len(labels)))
                        ax.set_xticklabels(
                            labels, rotation=35, ha="right", fontsize=8
                        )
                        ax.set_title(title)
                        ax.legend(fontsize=7, loc="upper right")
                        description = (
                            f"Stacked bar chart of '{col1}' vs '{col2}'."
                        )
                        self._save(fig, path)

                    else:
                        # unknown chart type from LLM — skip gracefully
                        continue

                    chart_entries.append({
                        "path": str(path.resolve()),
                        "description": description or f"{title} ({t}).",
                    })

                except Exception as e:
                    print(
                        f"[VizAgent] chart skipped "
                        f"({sheet} / {t} / {spec.get('col', '')}): {e}"
                    )
                    try:
                        plt.close("all")
                    except Exception:
                        pass
                    continue

            charts[sheet] = chart_entries

        return charts