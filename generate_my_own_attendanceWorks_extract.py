import pandas as pd

# attendanceWorks extract
# LIST STU CSE LOC FRE STU.FN STU.MN STU.LN STU.ID STU.SC LOC.NM STU.GR STU.GN
# STU.ETH STU.RC1 STU.RC2 STU.RC3 STU.RC4 STU.RC5 STU.RZC CSE.PT STU.LF
# FRE.CD FRE.ESD


# https://support.aeries.com/support/solutions/articles/14000076561-attendance-works-processing-the-extracts

# sql version
"""
SELECT TOP 100000 
        STU.FN AS [First Name], 
        [STU].[MN] AS [Middle Name], 
        STU.LN AS [Last Name], 
        [STU].[ID] AS [Student ID], 
        [STU].[SC] AS [School], 
        [LOC].[NM] AS [School name], 
        [STU].[GR] AS [Grade], 
        [STU].[GN] AS [Gender], 
        [STU].[ETH] AS [EthCd], 
        [STU].[RC1] AS [Race1], 
        [STU].[RC2] AS [Race2], 
        [STU].[RC3] AS [Race3], 
        [STU].[RC4] AS [Race4], 
        [STU].[RC5] AS [Race5], 
        [STU].[RZC] AS [Res Zip], 
        [CSE].[PT] AS [Plan Type], 
        [STU].[LF] AS [LangFlu], 
        [FRE].[CD] AS [Assignment], 
        CONVERT(VARCHAR(10),[FRE].[ESD],101) AS [Elg Start Dt] 

FROM (SELECT [FRE].* FROM [FRE] WHERE DEL = 0) [FRE] 
    RIGHT JOIN (
        (SELECT [LOC].* FROM [LOC] WHERE DEL = 0) [LOC] 
        RIGHT JOIN (
            (SELECT [STU].* FROM STU WHERE DEL = 0) [STU] 
            LEFT JOIN (SELECT [CSE].* FROM [CSE] WHERE DEL = 0) [CSE] 
            ON [STU].[ID] = [CSE].[ID]
                   ) 
        ON [LOC].[CD] = [STU].[SC]
                ) 
    ON [STU].[ID] = [FRE].[ID] 
WHERE (NOT STU.TG > ' ') 
ORDER BY [STU].[LN], [STU].[FN];
"""

# can't access CSE LOC or FRE for most districts..
# LIST STU STU.FN STU.MN STU.LN STU.ID STU.SC STU.GR STU.GN STU.ETH STU.RC1 
# STU.RC2 STU.RC3 STU.RC4 STU.RC5 STU.RZC STU.LF 

df = pd.read_excel(
    "attendanceWorks_mock.xlsx",
    dtype={
        "Race1": "str",
        "Race2": "str",
        "Race3": "str",
        "Race4": "str",
        "Race5": "str",
    },
)
print(df)


# Determination of Federal Ethnicity
# Disproportionality determination is partially based on the determination of federal race/ethnicity
# categories.
#   -If the Hispanic indicator is “Yes”, the federal ethnicity is Hispanic regardless of the race/s selected.
#   -If the Hispanic indicator is left blank or “No” is selected and the student has only one race selected, 
#    the federal ethnicity is equal to the race selected.
#   -If the Hispanic indicator is left blank or “No” is selected and the student has more than one race selected:
#       *And ALL selected races are any of the Asian subcategories, the federal ethnicity is equal to Asian
#          +201 Chinese
#          +202 Japanese
#          +203 Korean
#          +204 Vietnamese
#          +205 Asian Indian
#          +206 Laotian
#          +207 Cambodian
#          +208 Hmong
#          +299 Other Asian
#          +400 Filipino
#       *And ALL selected races are any of the Native Hawaiian or Pacific Islander subcategories, the federal 
#        ethnicity is equal to Native Hawaiian or Pacific Islander:
#          +301 Hawaiian
#          +302 Guamanian
#          +303 Samoan
#          +304 Tahitian
#          +399 Other Pacific Islander
#        *And more than one race category is selected and at least one of the race categories is not in the Asian 
#         or Native Hawaiian or Pacific Islander categories, then the federal is equal to “Multiple Ethnicities”
#    -If the Hispanic indicator is left blank or “No” is selected and the Race Category Missing Indicator is “Yes” 
#     (student has no race/s selected), the federal ethnicity is “Multiple Ethnicities”.



def tweak_student(df):
    def assign_race(row):
        if row.EthCd == "Y":
            return "HISPANIC/LATINO"
        races = [
            row.Race1,
            row.Race2,
            row.Race3,
            row.Race4,
            row.Race5,
        ]
        clean_races = list(
            set(
                [
                    x
                    for x in races
                    if str(x) != "nan" and str(x) != "ZZZ" and str(x) != "999"
                ]
            )
        )
        if not clean_races:
            return "UNKNOWN"
        if len(clean_races) > 1:  ## here is where it is not accurate anymore. see notes above.
            return "MULTI-RACE"
        race_codes = {
            "700": "WHITE",
            "100": "AMER IND/ALASK",
            "201": "ASIAN",
            "202": "ASIAN",
            "203": "ASIAN",
            "204": "ASIAN",
            "205": "ASIAN",
            "206": "ASIAN",
            "207": "ASIAN",
            "208": "ASIAN",
            "299": "ASIAN",
            "301": "PAC ISL",
            "303": "PAC ISL",
            "399": "PAC ISL",
            "400": "PAC ISL",
            "600": "AFRICAN AMER",
        }
        code = race_codes.get(clean_races[0])
        if code:
            return code
        else:
            input(f"this student doesnt fit {race_codes=}, {clean_races}")
            return "OTHER"

    check_cols = df.columns.tolist()
    check_cols.remove("Assignment")
    check_cols.remove("Elg Start Dt")
    return (
        df.query("Grade >= -1 & Grade <= 12")
        .assign(
            Grade=lambda df_: df_.Grade.map(
                {
                    -1: "TK",
                    0: "K",
                    1: 1,
                    2: 2,
                    3: 3,
                    4: 4,
                    5: 5,
                    6: 6,
                    7: 7,
                    8: 8,
                    9: 9,
                    10: 10,
                    11: 11,
                    12: 12,
                    -2: "PS2",
                    14: "AD",
                    16: "IN",
                    17: "PS",
                }
            ),
            Race=lambda df_: df_.apply(assign_race, axis=1),
            IEP=lambda df_: df_["Plan Type"]
            .fillna("NO")
            .map({150: "YES", 1: "YES", 100: "YES", "NO": "NO"}),
            EngLearner=lambda df_: df_.LangFlu.map(
                {"1": "NO", "2": "NO", "3": "YES", "4": "NO", "5": "NO"}
            ),
            FreeAndReduced=lambda df_: df_.Assignment.fillna("NO").map(
                {"F": "YES", "R": "YES", "NO": "NO", "N": "NO"}
            ),
        )
        .drop_duplicates()
        .sort_values("Elg Start Dt", ascending=False)
        .drop_duplicates(subset=check_cols, keep="first")
        .sort_values("Student ID")
        .drop(columns=["School"])
        .rename(
            columns={
                "First Name": "FirstName",
                "Middle Name": "MiddleName",
                "Last Name": "LastName",
                "Student ID": "ID",
                "School name": "School",
                "Res Zip": "ZipCode",
            }
        )
        .loc[
            :,
            [
                "FirstName",
                "MiddleName",
                "LastName",
                "ID",
                "School",
                "Grade",
                "Gender",
                "Race",
                "ZipCode",
                "IEP",
                "EngLearner",
                "FreeAndReduced",
            ],
        ]
    )


print(df[df.duplicated(subset=["Student ID"], keep=False)])


clean = tweak_student(df)
print(clean)

print(clean[clean.duplicated(subset=["ID"], keep=False)])
