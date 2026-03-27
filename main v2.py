# Statistics Netherlands (CBS) publishes its StatLine tables through a public OData API,
# which returns data in a structured, machine‑readable format (JSON/XML).
# CBS explicitly supports Python users by providing the cbsodata package,
# which is a thin, documented client around this API.

# Using this method means:
# You are not manually downloading files
# Anyone can re-run your code and get the same data
# That’s why this approach is considered fully reproducible and reviewer‑friendly.

# Every CBS table has a stable identifier.

import pandas as pd
import cbsodata
import matplotlib.pyplot as plt
import numpy as np

TABLE_ID = "86217NED"

# Columns you already confirmed exist in the data
COL_TECH = "Technologiegebied"
COL_PERIOD = "Perioden"
COL_EPO_APPS = "Patentaanvragen_2"   # EPO patent applications
COL_OCNL_APPS = "Patentaanvragen_6"  # OCNL patent applications


def _detect_code_column(meta_df: pd.DataFrame) -> str:
    """
    CBS metadata tables can name the code column differently depending on endpoint/version.
    Common candidates: Identifier, Key, ID.
    """
    for c in ["Identifier", "Key", "ID", "Id"]:
        if c in meta_df.columns:
            return c
    raise KeyError(f"Could not find a code column in meta table. Columns: {meta_df.columns.tolist()}")


def main():
    # 1) Load data
    df = pd.DataFrame(cbsodata.get_data(TABLE_ID))

    # 2) Load meta tables
    tech_meta = pd.DataFrame(cbsodata.get_meta(TABLE_ID, COL_TECH))
    period_meta = pd.DataFrame(cbsodata.get_meta(TABLE_ID, COL_PERIOD))

    # 3) Detect the correct join key column in meta
    tech_code_col = _detect_code_column(tech_meta)
    period_code_col = _detect_code_column(period_meta)

    # 4) Merge readable labels (Title) onto the data
    #    (keep only key + Title to avoid accidental column collisions)
    if "Title" not in tech_meta.columns:
        raise KeyError(f"'Title' not found in tech_meta. Columns: {tech_meta.columns.tolist()}")
    if "Title" not in period_meta.columns:
        raise KeyError(f"'Title' not found in period_meta. Columns: {period_meta.columns.tolist()}")

    df = df.merge(
        tech_meta[[tech_code_col, "Title"]].rename(columns={tech_code_col: COL_TECH, "Title": "TechLabel"}),
        on=COL_TECH,
        how="left"
    )
    df = df.merge(
        period_meta[[period_code_col, "Title"]].rename(columns={period_code_col: COL_PERIOD, "Title": "PeriodLabel"}),
        on=COL_PERIOD,
        how="left"
    )

    df["TechLabel"] = df["TechLabel"].fillna(df[COL_TECH].astype(str))
    df["PeriodLabel"] = df["PeriodLabel"].fillna(df[COL_PERIOD].astype(str))

    # 5) Convert numeric measures
    df[COL_EPO_APPS] = pd.to_numeric(df[COL_EPO_APPS], errors="coerce")
    df[COL_OCNL_APPS] = pd.to_numeric(df[COL_OCNL_APPS], errors="coerce")

    # 6) Pick latest year from PeriodLabel (CBS table is yearly; labels may include * or **)
    df["Year"] = df["PeriodLabel"].astype(str).str.extract(r"(\d{4})").astype(float)
    latest_year = int(df["Year"].max())
    d = df[df["Year"] == latest_year].copy()

    # 7) Exclude aggregate "Totaal technologiegebieden" row
    d = d[~d["TechLabel"].str.contains("Totaal", case=False, na=False)]

    # 8) Compute EPO share (%)
    d["TotalApps"] = d[COL_EPO_APPS] + d[COL_OCNL_APPS]
    d = d[d["TotalApps"] > 0].copy()
    d["EPO_share_pct"] = (d[COL_EPO_APPS] / d["TotalApps"]) * 100

    # 9) Optional: keep chart readable by selecting top N technology areas by total volume
    TOP_N = 25
    d = d.sort_values("TotalApps", ascending=False).head(TOP_N)

    # 10) Sort for display (low to high EPO share)
    d = d.sort_values("EPO_share_pct", ascending=True)

    # 11) Plot horizontal bar chart (EPO share)  ✅ UPDATED: add 80% line
    plt.figure(figsize=(10, 8))
    plt.barh(d["TechLabel"], d["EPO_share_pct"])

    plt.axvline(50, linestyle="--", linewidth=1)  # reference at 50%
    plt.axvline(80, linestyle=":", linewidth=1)   # reference at 80% (strongly international)

    plt.title(f"EPO share of patent applications by CPC technology area (Netherlands, {latest_year})")
    plt.xlabel("EPO share of applications (%)")
    plt.xlim(0, 100)

    plt.tight_layout()
    plt.savefig("epo_share_by_cpc_latest_year.png", dpi=200)
    plt.show()

    # --- SECOND CHART (ranked): Absolute patent applications (EPO vs OCNL) ---

    # Rank sectors by absolute volume (EPO + OCNL), descending
    d_abs = d.copy()
    d_abs["TotalApps"] = d_abs[COL_EPO_APPS] + d_abs[COL_OCNL_APPS]
    d_abs = d_abs.sort_values("TotalApps", ascending=False)

    # Prepare positions for grouped horizontal bars
    y = np.arange(len(d_abs))
    h = 0.4

    plt.figure(figsize=(10, 8))

    # Plot OCNL and EPO as grouped horizontal bars
    plt.barh(y - h / 2, d_abs[COL_OCNL_APPS], height=h, label="OCNL patent applications")
    plt.barh(y + h / 2, d_abs[COL_EPO_APPS], height=h, label="EPO patent applications")

    plt.yticks(y, d_abs["TechLabel"])
    plt.xlabel("Number of patent applications")
    plt.title(f"Absolute patent applications by CPC technology area (ranked by total volume, {latest_year})")
    plt.legend()

    # Make the ranking read "top-down" visually (largest at top)
    plt.gca().invert_yaxis()

    plt.tight_layout()
    plt.savefig("absolute_patent_applications_epo_vs_ocnl_ranked_latest_year.png", dpi=200)
    plt.show()

    # 12) Helpful printed nuggets for your slide insight
    most_international = d.iloc[-1]
    most_domestic = d.iloc[0]
    print(f"Latest year used: {latest_year}")
    print(f"Highest EPO share (international-leaning): {most_international['TechLabel']} "
          f"({most_international['EPO_share_pct']:.1f}%)")
    print(f"Lowest EPO share (domestic-leaning): {most_domestic['TechLabel']} "
          f"({most_domestic['EPO_share_pct']:.1f}%)")


if __name__ == "__main__":
    main()