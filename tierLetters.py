import os
import pandas as pd
from collections import defaultdict

# LIST STU INV STU.NM STU.ID STU.SC INV.SN INV.CD INV.DT IF STU.SC = 51 OR STU.SC = 100 OR STU.SC = 150 AND INV.DT > 07/01/2024

# only need to do this for the current year file
def get_students_tier_intervention(filename):
    # For now, we will just indicate YES/NO for received excessive absent letter
    # in future, we could specify how many letters and what tier...
    mapping_dict = defaultdict(lambda: "Unknown INV code order")
    mapping_dict["2-10-1"] = "Tier 1, then removed"
    mapping_dict["2-12-3"] = "Tier 1 -> 2"
    mapping_dict["1-1-1"] = "Tier 1"
    mapping_dict["3-120-3"] = "Tier 1 -> 2, then removed"
    mapping_dict["3-123-6"] = "Tier 1 -> 2 -> 3"
    mapping_dict["2-01-1"] = "removed, then Tier 1?"

    df = pd.read_excel(filename)
    return (
        df.sort_values("Date", ascending=True)
        .query('Code.isin(["0","1","2","3"])')
        .assign(intCode=lambda df_: df_.Code.astype(int))
        .groupby("Student ID")
        .agg(
            codeCount=("Code", "count"),
            codeConcat=("Code", "sum"),
            codeSum=("intCode", "sum"),
        )
        .assign(
            INVcode=lambda df_: df_.codeCount.astype("str")
            + "-"
            + df_.codeConcat.astype("str")
            + "-"
            + df_.codeSum.astype("str")
        )
        .assign(INVLetters=lambda df_: df_.INVcode.map(mapping_dict))
        # .INVLetters.value_counts()
        # .query('INVcode == "3-123-6"')
        .codeCount.astype(bool)
        .map({True: "YES", False: "NO"})
        .reset_index()
        .rename(columns={"Student ID": "ID", "codeCount": "ExcessiveAbsentLetters"})
    )


def merge_with_attendanceWorks(aw_df, tier_df):
    return (
        aw_df.iloc[:, :-1]
        .merge(tier_df, on="ID", how="left")
        .assign(
            ExcessiveAbsentLetters=lambda df_: df_.ExcessiveAbsentLetters.fillna("NO")
        )
    )


if __name__ == "__main__":
    filepath = os.path.join(
        os.path.join("oneFiletoRuleThemAll_oct24", "EDCOE_charter"),
        "tiered_intervention.xlsx",
    )
    print(get_students_tier_intervention(filepath))

    # df = pd.read_excel(filepath)
    # code2 = df.query('Code.isin(["3"])')
    # print(code2)
    # code1 = df.query('Code.isin(["1"])')

    # merged = code1.merge(code2, on="Student ID", how="outer", indicator=True)
    # # print(merged[merged["_merge"] == "left_only"])
