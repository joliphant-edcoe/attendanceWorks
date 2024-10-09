from Attendance import AttendanceDATT
from AttendanceSupp import AttendanceTruancySupp
from AttendanceExcel import AttendanceExcelGenerator
from Heatmap import AttendanceHeatMap
import pickle

# from AttendanceCharts import AttendanceChartsExcel


# student_file = "000_20240109120624_AWSTU_2324.csv"

# pollock pines files
current_stu_datafile = "000_20240909112140_AWSTU 2425.csv"
prior_yr_datafile = "000_20240909124703_AWSTU 2324.csv"
two_yr_prior_datafile = "000_20240909124802_AWSTU 2223.csv"


# lake thoe files
current_stu_datafile =  "000_20240909125838_AWSTU_2425.csv"
prior_yr_datafile =     "000_20240906015225_AWSTU_2324.csv"
two_yr_prior_datafile = "000_20240906014839_AWSTU_2223.csv"



# county files
# current_stu_datafile = "oneFiletoRuleThemAll/all_county/allCountyAttendanceWorks 2425.csv"
# prior_yr_datafile = "oneFiletoRuleThemAll/all_county/allCountyAttendanceWorks 2324.csv"
# two_yr_prior_datafile = "oneFiletoRuleThemAll/all_county/allCountyAttendanceWorks 2223.csv"



adatt = AttendanceDATT(
    current_stu_datafile, prior_yr_datafile, two_yr_prior_datafile, school_type="TK-12",district_level=False
)
# adatt = AttendanceDATT(
#     current_stu_datafile, prior_yr_datafile, two_yr_prior_datafile, school_type="TK-8"
# )
# adatt.read_data_and_run_all_reports()
adatt.read_data()
adatt.tweak_student()
adatt.report_by_grade()
adatt.report_by_school()
adatt.report_by_race()
adatt.report_by_gender()
adatt.report_by_race_gender()
adatt.report_by_race_grade()
adatt.report_by_sp_el_or_lunch(["IEP", "IEP Status"])
adatt.report_by_sp_el_or_lunch(["EngLearner", "EL Status"])
adatt.report_by_sp_el_or_lunch(["FreeAndReduced", "Free/Reduced Lunch Status"])
adatt.report_by_zipcode()
adatt.report_all_students()
adatt.suspensions_by_school()
adatt.report_by_district()

# print(adatt.bygrade)
# print(adatt.bygrade_prior)
# print(adatt.bygrade_two_yr_prior)
# print(adatt.bygrade3yrs)
# print(adatt.byrace)
# print(adatt.bygender)
# print(adatt.byracegender)
# print(adatt.byracegrade)
# print(adatt.byEngLearner)
# print(adatt.byIEP)
# print(adatt.byFreeReduced)
# print(adatt.byzipcode)
# print(adatt.all_students)
# print(adatt.by_suspension_school)
# print(adatt.byschool)
# print(adatt.bydistrict)

truancy = AttendanceTruancySupp(current_stu_datafile, school_type="TK-12")
# truancy = AttendanceTruancySupp(current_stu_datafile, school_type="TK-8")
# truancy.read_data_and_run_all_reports()
truancy.read_data()
truancy.tweak_student()
truancy.report_all_students()
truancy.report_absence_types()
truancy.report_absence_by_school()
truancy.report_absence_by_gender()
truancy.report_absence_by_grade()
truancy.report_absence_by_race()
truancy.report_absence_by_race_gender()
truancy.report_part1_notified()
truancy.report_part2_notified()
truancy.report_part3_notified()
truancy.report_part1_grade_notified()
truancy.report_part2_grade_notified()
truancy.report_part3_grade_notified()
truancy.report_part1_school_notified()
truancy.report_part2_school_notified()
truancy.report_part3_school_notified()

# print(truancy.absence_by_school)
# truancy.clean_student_data.to_csv('lt_all_students.csv')
# print(truancy.absence_types)
# print(truancy.all_students.to_csv('pp_all_students.csv'))
# print(truancy.absence_by_gender)
# print(truancy.absence_by_grade)
# print(truancy.absence_by_race)
# print(truancy.absence_by_racegender)
# print(truancy.absence_by_racegender_not)
# print(truancy.part1_notifications)
# print(truancy.part2_notifications)
# print(truancy.part1_grade_notifications)
# print(truancy.part2_grade_notifications)
# print(truancy.part3_grade_notifications)
# print(truancy.part1_school_notifications)
# print(truancy.part2_school_notifications)
# print(truancy.part3_school_notifications)





# charts = AttendanceChartsExcel(adatt)
# charts.by_gender_charts()
# charts.by_race_charts()
# charts.by_sp_needs_charts()
# charts.by_eng_learners_charts()
# charts.by_lunch_status_charts()
# charts.by_zipcode_charts()

excelwrite = AttendanceExcelGenerator(
    adatt, truancy, "test_output.xlsx", school_type="TK-12"
)
excelwrite.append_data_to_templates()



heat = AttendanceHeatMap('pioneerATTtable.xlsx')
heat.read_process_data()
print(heat.clean_absences_by_date)
