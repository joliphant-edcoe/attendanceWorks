from Attendance import AttendanceDATT
from AttendanceSupp import AttendanceTruancySupp
from AttendanceExcel import AttendanceExcelGenerator
from Heatmap import AttendanceHeatMap
import pickle
import os
import datetime



BASE_PATH = "oneFiletoRuleThemAll_oct24/"
YEAR_CODE1 = '2425'
YEAR_CODE2 = '2324'
YEAR_CODE3 = '2223'
CUTOFF_DATE = datetime.datetime(2024,10,4)
FILENAME_DATE = 'Oct24'


districts = os.listdir(BASE_PATH)
districts

district_type = [
    "TK-12",  # all_county
    "TK-12",  # blackoak
    "TK-8",  # camino
    "TK-12",  # charter
    "TK-12",  # sped
    "HS",  # el dorado
    "TK-8",  # gold oak
    "TK-8",  # gold trail
    "TK-12",  # lake tahoe
    "TK-8",  # latrobe
    "TK-8",  # motherlode
    "TK-8",  # pioneer
    "TK-8",  # placerville
    "TK-8",  # pollock
    "TK-8",  # rescue
    "TK-8",  # silver
]


all_data = dict()

for i, d in enumerate(districts):
    path = os.path.join(BASE_PATH, d)
    files = os.listdir(path)

    att_file = [s for s in files if "atttable" in s.lower()]
    if att_file:
        att_data_file = os.path.join(path, att_file[0])
    else:
        att_data_file = ""

    current = [s for s in files if YEAR_CODE1 in s][0]
    last = [s for s in files if YEAR_CODE2 in s][0]
    last2 = [s for s in files if YEAR_CODE3 in s][0]


    current_stu_datafile = os.path.join(path, current)
    prior_yr_datafile = os.path.join(path, last)
    two_yr_prior_datafile = os.path.join(path, last2)

    print(d)
    print(current_stu_datafile)
    print(prior_yr_datafile)
    print(two_yr_prior_datafile)
    print(att_data_file)

    if d == "all_county":
        district_level = True
    else:
        district_level = False

    print(f"{district_level=}")
    print()

    adatt = AttendanceDATT(
        current_stu_datafile,
        prior_yr_datafile,
        two_yr_prior_datafile,
        school_type=district_type[i],
        district_level=district_level,
    )
    adatt.read_data_and_run_all_reports()

    truancy = AttendanceTruancySupp(current_stu_datafile, school_type=district_type[i])
    truancy.read_data_and_run_all_reports()

    heatmap = AttendanceHeatMap(att_datafile=att_data_file,cutoff_date=CUTOFF_DATE)
    heatmap.read_process_data()

    excelwrite = AttendanceExcelGenerator(
        adatt,
        truancy,
        f"auto_excel_files/24-25 Cal DATT AW - ({d} {FILENAME_DATE}).xlsx",
        f"auto_excel_files/24-25 Cal DATT Truancy - ({d} {FILENAME_DATE}).xlsx",
        school_type=district_type[i],
    )
    excelwrite.append_data_to_templates()

    all_data[d] = {
        **adatt.return_data_dict(),
        **truancy.return_data_dict(),
        **heatmap.return_data_dict(),
    }

with open(f"all_data_{FILENAME_DATE}.pickle", "wb") as f:
    pickle.dump(all_data, f)
