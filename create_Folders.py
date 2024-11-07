import os
import pandas as pd

base_path = "oneFiletoRuleThemAll_nov24"
subfolders_level1 = [
    "black_oak_mine_unified",
    "camino_unified",
    "EDCOE_charter",
    "EDCOE_sped",
    "el_dorado_union_high",
    "gold_oak_union_elementary",
    "gold_trail_union_elementary",
    "lake_tahoe_unified",
    "latrobe",
    "mother_lode_union_elementary",
    "pioneer_union_elementary",
    "placerville_union_elementary",
    "pollock_pines_elementary",
    "rescue_union_elementary",
    "silver_fork_elementary",
]

list_df = []


def line_fixer(row):
    print(f"this row has {len(row)} elements")
    print(f"{row=}")
    fixedrow = row[:2] + [" ".join(row[2:4])] + row[4:]
    print(f"{fixedrow}")
    return fixedrow
    # return None  # to skip


for sub in subfolders_level1:
    path = os.path.join(base_path, sub)
    files = os.listdir(path)
    for f in files:
        name, ext = os.path.splitext(f)

        if ext == '.xlsx':
            continue
        components = name.split("_")
        if len(components[-1]) == 4:
            year = components[-1]
        else:
            year = components[-1].split()[-1]

        print(f, year, sub)
        if year == "2425":
            df = pd.read_csv(
                os.path.join(os.path.join(base_path, sub), f),
                encoding="cp437",
                dtype={"ZipCode": "str"},
                on_bad_lines=line_fixer,
                engine="python",
            )
            df = df.assign(district=sub, year=year)
            list_df.append(df)
        # print(len(df.columns))

mondo = pd.concat(list_df)
print(mondo)
mondo.to_csv(os.path.join(os.path.join(base_path,'all_county'),"allCountyAttendanceWorks_2425.csv"), index=False)
