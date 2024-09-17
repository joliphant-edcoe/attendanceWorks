import pandas as pd


class AttendanceDATT:
    def __init__(
        self,
        current_stu_datafile,
        prior_yr_datafile=None,
        two_yr_prior_datafile=None,
        school_type="TK-12",
        date_range=None,
    ):
        self.current_stu_datafile = current_stu_datafile
        self.prior_yr_datafile = prior_yr_datafile
        self.two_yr_prior_datafile = two_yr_prior_datafile
        self.school_type = school_type
        self.date_range = date_range
        zips_db = pd.read_csv(
            "US.txt",
            sep="\t",
            names=[
                "countryCode",
                "postalCode",
                "placeName",
                "b",
                "c",
                "d",
                "e",
                "f",
                "a",
                "ge",
                "grg",
                "asd",
            ],
            dtype={"postalCode": "str"},
        )
        self.zips_dict = dict(zip(zips_db.postalCode, zips_db.placeName))
        self.standard_columns = {
            "percentFreeReduced": "PERCENT of Students Receiving Free/Reduced Lunch",
            "AverageDailyAttendance": "Average Daily Attendance (ADA)",
            "severe chronic": "NUMBER severe chronic absence",
            "percentSevere": "PERCENT severe chronic absence",
            "moderate chronic": "NUMBER moderate chronic absence",
            "percentModerate": "PERCENT moderate chronic absence",
            "allChronic": "NUMBER ALL chronic absence (severe + moderate)",
            "percentChronic": "PERCENT ALL chronic absence (severe + moderate)",
            "at risk": "NUMBER at-risk attendance",
            "percentAtRisk": "PERCENT at-risk attendance",
            "satisfactory": "NUMBER satisfactory attendance",
            "percentSatisfactory": "PERCENT satisfactory attendance",
            "total": "Total Students",
            "totalStudents": "Total Students",
            "studentsLeastOne": "NUMBER of students with at least one suspension",
            "percentLeastOne": "PERCENT of total students with at least one suspension",
            "studentsLeastTwo": "NUMBER of students with two or more suspensions",
            "percentLeastTwo": "PERCENT of total students with two or more suspension",
            "totalIncidents": "Total number of incidents of suspension",
            "totalChronicStudents": "NUMBER ALL chronic absence (severe + moderate)",
            "chronicStudentsLeastOne": "NUMBER ALL chronic absence with at least one suspension",
            "percentChronicLeastOne": "PERCENT ALL chronic absense with at least one suspension",
            "chronicStudentsLeastTwo": "NUMBER ALL chronic absense with two or more suspensions",
            "percentChronicLeastTwo": "PERCENT ALL chronic absense with two or more suspensions",
            "notChronicStudents": "NUMBER NOT CHRONICALLY ABSENT (at-risk + satisfactory)",
            "notStudentsLeastOne": "NUMBER NOT chronically absent with at least one suspension",
            "percentNotChronicLeastOne": "PERCENT NOT chronically absent with at least one suspension",
            "notStudentsLeastTwo": "NUMBER NOT chronically absent with two or more suspensions",
            "percentNotChronicLeastTwo": "PERCENT NOT chronically absent with two or more suspensions",
        }

    def read_data(self):
        self.current_stu_data = pd.read_csv(
            self.current_stu_datafile,
            dtype={
                "Grade": "str",
                "ZipCode": "str",
            },
            encoding="cp437",
        )
        if self.prior_yr_datafile:
            self.prior_yr_data = pd.read_csv(
                self.prior_yr_datafile,
                encoding="cp437",
            )
        if self.two_yr_prior_datafile:
            self.two_yr_prior_data = pd.read_csv(
                self.two_yr_prior_datafile,
                encoding="cp437",
            )

    def tweak_student(self):
        self.clean_student_data = self.tweak_student_df(self.current_stu_data)
        self.clean_prior_yr_data = self.tweak_student_df(self.prior_yr_data)
        self.clean_two_yr_prior_data = self.tweak_student_df(self.two_yr_prior_data)

    def tweak_student_df(self, df):

        yesno_type = pd.CategoricalDtype(
            categories=[
                "YES",
                "NO",
            ],
            ordered=True,
        )

        category_type = pd.CategoricalDtype(
            categories=[
                "severe chronic",
                "moderate chronic",
                "at risk",
                "satisfactory",
            ],
            ordered=True,
        )

        gender_type = pd.CategoricalDtype(
            categories=["M", "F"],
            ordered=True,
        )

        race_type = pd.CategoricalDtype(
            categories=[
                "HISPANIC/LATINO",
                "AFRICAN AMER",
                "WHITE",
                "ASIAN",
                "PAC ISL",
                "AMER IND/ALASK",
                "MULTI-RACE",
                "UNKNOWN",
            ],
            ordered=True,
        )

        # default is TK-12
        grade_list = [
            "TK",
            "K",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
        ]
        if self.school_type == "TK-8":
            grade_list = grade_list[:10]
        elif self.school_type == "HS":
            grade_list = grade_list[10:]

        grade_type = pd.CategoricalDtype(
            categories=grade_list,
            ordered=True,
        )

        def categorize_absentee(val):
            if val < 0.05:
                return "satisfactory"
            elif val < 0.1:
                return "at risk"
            elif val < 0.2:
                return "moderate chronic"
            else:
                return "severe chronic"

        return (
            df.assign(
                TotalDaysAbsent=df.ExcusedAbsences
                + df.UnexcusedAbsences
                + df.DaysSuspended
            )
            .assign(
                AbsentPercentage=lambda df_: df_.TotalDaysAbsent
                / (df_.TotalDaysAbsent + df_.DaysPresent),
                Category=lambda df_: df_.AbsentPercentage.apply(categorize_absentee),
            )
            .astype(
                {
                    "Category": category_type,
                    "Grade": grade_type,
                    "Race": race_type,
                    "Gender": gender_type,
                    "IEP": yesno_type,
                    "EngLearner": yesno_type,
                    "FreeAndReduced": yesno_type,
                }
            )
        )

    def report_by_grade(self):
        self.bygrade = self.report_by_grade_yr(self.clean_student_data)
        self.bygrade_prior = self.report_by_grade_yr(self.clean_prior_yr_data)
        self.bygrade_two_yr_prior = self.report_by_grade_yr(
            self.clean_two_yr_prior_data
        )
        self.bygrade3yrs = pd.concat(
            [self.bygrade, self.bygrade_prior, self.bygrade_two_yr_prior]
        )

    def report_by_grade_yr(self, df):
        bygrade = (
            df.groupby(["Grade", "Category"], observed=False)
            .ID.count()
            .unstack()
            .assign(total=lambda df_: df_.sum(1))
        )
        total_row = bygrade.sum(0).to_frame().rename(columns={0: "totals"}).T
        bygrade = pd.concat([bygrade, total_row])
        bygrade = (
            bygrade.assign(
                allChronic=lambda df_: df_["moderate chronic"] + df_["severe chronic"],
                percentSevere=lambda df_: df_["severe chronic"].div(df_.total),
                percentModerate=lambda df_: df_["moderate chronic"].div(df_.total),
                percentChronic=lambda df_: df_["allChronic"].div(df_.total),
                percentAtRisk=lambda df_: df_["at risk"].div(df_.total),
                percentSatisfactory=lambda df_: df_["satisfactory"].div(df_.total),
            )
            .rename_axis("Grade")
            .loc[
                :,
                [
                    "severe chronic",
                    "percentSevere",
                    "moderate chronic",
                    "percentModerate",
                    "allChronic",
                    "percentChronic",
                    "at risk",
                    "percentAtRisk",
                    "satisfactory",
                    "percentSatisfactory",
                    "total",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        bygrade.columns.name = ""
        return bygrade

    def report_by_school(self):
        # calculcate ADA
        schoolADA = (
            self.clean_student_data.groupby(["SchoolName"])
            .agg({"DaysPresent": "sum", "TotalDaysAbsent": "sum", "ID": "count"})
            .assign(
                AverageDailyAttendance=lambda df_: df_.DaysPresent
                / (df_.DaysPresent + df_.TotalDaysAbsent)
            )
            .rename(columns={"ID": "TotalStudents", "DaysPresent": "TotalDaysPresent"})
        )

        # calculate free reduced lunch
        FreeReduced = (
            self.clean_student_data.query('FreeAndReduced == "YES"')
            .groupby("SchoolName")
            .ID.count()
        )
        schoolADA = schoolADA.assign(NumberFreeReduced=FreeReduced).assign(
            percentFreeReduced=lambda df_: df_.NumberFreeReduced / df_.TotalStudents
        )

        # group attendance rates by school
        self.byschool = (
            self.clean_student_data.groupby(["SchoolName", "Category"], observed=False)
            .ID.count()
            .unstack()
            .assign(total=lambda df_: df_.sum(1))
        )
        self.byschool = pd.concat([self.byschool, schoolADA], axis=1)
        self.byschool = (
            self.byschool.assign(
                allChronic=lambda df_: df_["moderate chronic"] + df_["severe chronic"],
                percentSevere=lambda df_: df_["severe chronic"].div(df_.total),
                percentModerate=lambda df_: df_["moderate chronic"].div(df_.total),
                percentChronic=lambda df_: df_["allChronic"].div(df_.total),
                percentAtRisk=lambda df_: df_["at risk"].div(df_.total),
                percentSatisfactory=lambda df_: df_["satisfactory"].div(df_.total),
            )
            .rename_axis("School")
            .loc[
                :,
                [
                    "percentFreeReduced",
                    "AverageDailyAttendance",
                    "severe chronic",
                    "percentSevere",
                    "moderate chronic",
                    "percentModerate",
                    "allChronic",
                    "percentChronic",
                    "at risk",
                    "percentAtRisk",
                    "satisfactory",
                    "percentSatisfactory",
                    "total",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        self.byschool.columns.name = ""

    def report_by_race(self):
        # group attendance rates by race
        self.byrace = (
            self.clean_student_data.groupby(["Race", "Category"], observed=False)
            .ID.count()
            .unstack()
            .assign(total=lambda df_: df_.sum(1))
        )
        total_row = self.byrace.sum(0).to_frame().rename(columns={0: "totals"}).T
        self.byrace = pd.concat([self.byrace, total_row])
        self.byrace = (
            self.byrace.assign(
                allChronic=lambda df_: df_["moderate chronic"] + df_["severe chronic"],
                percentSevere=lambda df_: df_["severe chronic"].div(df_.total),
                percentModerate=lambda df_: df_["moderate chronic"].div(df_.total),
                percentChronic=lambda df_: df_["allChronic"].div(df_.total),
                percentAtRisk=lambda df_: df_["at risk"].div(df_.total),
                percentSatisfactory=lambda df_: df_["satisfactory"].div(df_.total),
            )
            .rename_axis("Race/Ethnicity")
            .loc[
                :,
                [
                    "severe chronic",
                    "percentSevere",
                    "moderate chronic",
                    "percentModerate",
                    "allChronic",
                    "percentChronic",
                    "at risk",
                    "percentAtRisk",
                    "satisfactory",
                    "percentSatisfactory",
                    "total",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        self.byrace.columns.name = ""

    def report_by_gender(self):
        # group attendance rates by gender
        self.bygender = (
            self.clean_student_data.groupby(["Gender", "Category"], observed=False)
            .ID.count()
            .unstack()
            .assign(total=lambda df_: df_.sum(1))
        )
        total_row = self.bygender.sum(0).to_frame().rename(columns={0: "totals"}).T
        self.bygender = pd.concat([self.bygender, total_row])
        self.bygender = (
            self.bygender.assign(
                allChronic=lambda df_: df_["moderate chronic"] + df_["severe chronic"],
                percentSevere=lambda df_: df_["severe chronic"].div(df_.total),
                percentModerate=lambda df_: df_["moderate chronic"].div(df_.total),
                percentChronic=lambda df_: df_["allChronic"].div(df_.total),
                percentAtRisk=lambda df_: df_["at risk"].div(df_.total),
                percentSatisfactory=lambda df_: df_["satisfactory"].div(df_.total),
            )
            .rename_axis("Gender")
            .loc[
                :,
                [
                    "severe chronic",
                    "percentSevere",
                    "moderate chronic",
                    "percentModerate",
                    "allChronic",
                    "percentChronic",
                    "at risk",
                    "percentAtRisk",
                    "satisfactory",
                    "percentSatisfactory",
                    "total",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        self.bygender.columns.name = ""

    def report_by_race_gender(self):
        # group attendance rates by race AND gender
        self.byracegender = (
            self.clean_student_data.groupby(
                ["Race", "Gender", "Category"], observed=False
            )
            .ID.count()
            .unstack()
            .assign(total=lambda df_: df_.sum(1))
        )
        total_row = self.byracegender.groupby(level=1, observed=False).sum()  #
        total_row = pd.concat({"Total": total_row})
        self.byracegender = pd.concat([self.byracegender, total_row])

        self.byracegender = (
            self.byracegender.assign(
                allChronic=lambda df_: df_["moderate chronic"] + df_["severe chronic"],
                percentSevere=lambda df_: df_["severe chronic"].div(df_.total),
                percentModerate=lambda df_: df_["moderate chronic"].div(df_.total),
                percentChronic=lambda df_: df_["allChronic"].div(df_.total),
                percentAtRisk=lambda df_: df_["at risk"].div(df_.total),
                percentSatisfactory=lambda df_: df_["satisfactory"].div(df_.total),
            )
            .rename_axis(["Race/Ethnicity", "Gender"])
            .loc[
                :,
                [
                    "severe chronic",
                    "percentSevere",
                    "moderate chronic",
                    "percentModerate",
                    "allChronic",
                    "percentChronic",
                    "at risk",
                    "percentAtRisk",
                    "satisfactory",
                    "percentSatisfactory",
                    "total",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        self.byracegender.columns.name = ""

    def report_by_race_grade(self):
        # group attendance rates by race AND grade
        self.byracegrade = (
            self.clean_student_data.groupby(
                ["Race", "Grade", "Category"], observed=False
            )
            .ID.count()
            .unstack()
            .assign(total=lambda df_: df_.sum(1))
        )
        total_row = self.byracegrade.groupby(level=1, observed=False).sum()  #
        total_row = pd.concat({"Total": total_row})
        self.byracegrade = pd.concat([self.byracegrade, total_row])

        self.byracegrade = (
            self.byracegrade.assign(
                allChronic=lambda df_: df_["moderate chronic"] + df_["severe chronic"],
                percentSevere=lambda df_: df_["severe chronic"].div(df_.total),
                percentModerate=lambda df_: df_["moderate chronic"].div(df_.total),
                percentChronic=lambda df_: df_["allChronic"].div(df_.total),
                percentAtRisk=lambda df_: df_["at risk"].div(df_.total),
                percentSatisfactory=lambda df_: df_["satisfactory"].div(df_.total),
            )
            .rename_axis(["Race/Ethnicity", "Grade"])
            .loc[
                :,
                [
                    "severe chronic",
                    "percentSevere",
                    "moderate chronic",
                    "percentModerate",
                    "allChronic",
                    "percentChronic",
                    "at risk",
                    "percentAtRisk",
                    "satisfactory",
                    "percentSatisfactory",
                    "total",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        self.byracegrade.columns.name = ""

    def report_by_sp_el_or_lunch(self, student_category):
        # student_category = ['IEP','IEP Status']   #[df_name,excel_name]
        # group attendance rates by IEP, EL, OR Lunch status
        if student_category[0] == "IEP":
            self.byIEP = self.sp_el_or_lunch(student_category)
        elif student_category[0] == "EngLearner":
            self.byEngLearner = self.sp_el_or_lunch(student_category)
        elif student_category[0] == "FreeAndReduced":
            self.byFreeReduced = self.sp_el_or_lunch(student_category)

    def sp_el_or_lunch(self, student_category):
        by_category = (
            self.clean_student_data.groupby(
                [student_category[0], "Category"], observed=False
            )
            .ID.count()
            .unstack()
            .assign(total=lambda df_: df_.sum(1))
        )
        total_row = by_category.sum(0).to_frame().rename(columns={0: "totals"}).T
        by_category = pd.concat([by_category, total_row])

        by_category = (
            by_category.assign(
                allChronic=lambda df_: df_["moderate chronic"] + df_["severe chronic"],
                percentSevere=lambda df_: df_["severe chronic"].div(df_.total),
                percentModerate=lambda df_: df_["moderate chronic"].div(df_.total),
                percentChronic=lambda df_: df_["allChronic"].div(df_.total),
                percentAtRisk=lambda df_: df_["at risk"].div(df_.total),
                percentSatisfactory=lambda df_: df_["satisfactory"].div(df_.total),
            )
            .rename_axis(student_category[1])
            .loc[
                :,
                [
                    "severe chronic",
                    "percentSevere",
                    "moderate chronic",
                    "percentModerate",
                    "allChronic",
                    "percentChronic",
                    "at risk",
                    "percentAtRisk",
                    "satisfactory",
                    "percentSatisfactory",
                    "total",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        by_category.columns.name = ""
        return by_category

    def report_by_zipcode(self):
        # group attendance rates by zipcode
        self.byzipcode = (
            self.clean_student_data.groupby(["ZipCode", "Category"], observed=False)
            .ID.count()
            .unstack()
            .assign(total=lambda df_: df_.sum(1))
            .sort_values("total", ascending=False)
            .assign(
                cummulativ=lambda df_: df_.total.cumsum(0),
                cummalativpct=lambda df_: df_.cummulativ.div(df_.total.sum(0)),
                within98=lambda df_: df_.cummalativpct < 0.99,
            )
        )
        mainzips = self.byzipcode.query("within98 == True").iloc[:, :5]
        otherzips = (
            self.byzipcode.query("within98 == False")
            .iloc[:, :5]
            .sum()
            .to_frame()
            .rename(columns={0: "Other"})
            .T
        )
        self.byzipcode = pd.concat([mainzips, otherzips])
        total_row = self.byzipcode.sum(0).to_frame().rename(columns={0: "totals"}).T
        self.byzipcode = pd.concat([self.byzipcode, total_row])
        self.byzipcode = (
            self.byzipcode.assign(
                allChronic=lambda df_: df_["moderate chronic"] + df_["severe chronic"],
                percentSevere=lambda df_: df_["severe chronic"].div(df_.total),
                percentModerate=lambda df_: df_["moderate chronic"].div(df_.total),
                percentChronic=lambda df_: df_["allChronic"].div(df_.total),
                percentAtRisk=lambda df_: df_["at risk"].div(df_.total),
                percentSatisfactory=lambda df_: df_["satisfactory"].div(df_.total),
            )
            .rename_axis("Zip Code")
            .reset_index()
            .assign(
                placeName=lambda df_: df_["Zip Code"].map(self.zips_dict).fillna("--")
            )
            .set_index("Zip Code")
            .loc[
                :,
                [
                    "placeName",
                    "severe chronic",
                    "percentSevere",
                    "moderate chronic",
                    "percentModerate",
                    "allChronic",
                    "percentChronic",
                    "at risk",
                    "percentAtRisk",
                    "satisfactory",
                    "percentSatisfactory",
                    "total",
                ],
            ]
            .rename(columns=self.standard_columns)
            .rename(columns={"placeName": "Zip Code Description"})
        )
        self.byzipcode.columns.name = ""

    def report_all_students(self):
        self.all_students = (
            self.clean_student_data.query('Category != "satisfactory"')
            .sort_values(["Category", "SchoolName"])
            .loc[
                :,
                ["FirstName", "MiddleName", "LastName", "ID", "SchoolName", "Category"],
            ]
        )

    def suspensions_by_school(self):
        suspensions = (
            self.clean_student_data.groupby("SchoolName", observed=False)
            .agg(
                totalStudents=("ID", "count"),
                studentsLeastOne=("IncidentsOfSuspension", lambda x: (x >= 1).sum()),
                studentsLeastTwo=("IncidentsOfSuspension", lambda x: (x >= 2).sum()),
                totalIncidents=("IncidentsOfSuspension", "sum"),
            )
            .assign(
                percentLeastOne=lambda df_: df_.studentsLeastOne.div(df_.totalStudents),
                percentLeastTwo=lambda df_: df_.studentsLeastTwo.div(df_.totalStudents),
            )
        )

        chronic_suspensions = (
            self.clean_student_data.query(
                'Category == "severe chronic" | Category == "moderate chronic"'
            )
            .groupby("SchoolName", observed=False)
            .agg(
                totalChronicStudents=("ID", "count"),
                chronicStudentsLeastOne=(
                    "IncidentsOfSuspension",
                    lambda x: (x >= 1).sum(),
                ),
                chronicStudentsLeastTwo=(
                    "IncidentsOfSuspension",
                    lambda x: (x >= 2).sum(),
                ),
            )
            .assign(
                percentChronicLeastOne=lambda df_: df_.chronicStudentsLeastOne.div(
                    df_.totalChronicStudents
                ),
                percentChronicLeastTwo=lambda df_: df_.chronicStudentsLeastTwo.div(
                    df_.totalChronicStudents
                ),
            )
        )

        not_suspensions = (
            self.clean_student_data.query(
                'Category == "at risk" | Category == "satisfactory"'
            )
            .groupby("SchoolName", observed=False)
            .agg(
                notChronicStudents=("ID", "count"),
                notStudentsLeastOne=("IncidentsOfSuspension", lambda x: (x >= 1).sum()),
                notStudentsLeastTwo=("IncidentsOfSuspension", lambda x: (x >= 2).sum()),
            )
            .assign(
                percentNotChronicLeastOne=lambda df_: df_.notStudentsLeastOne.div(
                    df_.notChronicStudents
                ),
                percentNotChronicLeastTwo=lambda df_: df_.notStudentsLeastTwo.div(
                    df_.notChronicStudents
                ),
            )
        )
        self.by_suspension_school = pd.concat(
            [suspensions, chronic_suspensions, not_suspensions], axis=1
        )

        self.by_suspension_school = (
            self.by_suspension_school.fillna(0)
            .rename_axis("School Name")
            .assign(
                totalChronicStudents=lambda df_: df_.totalChronicStudents.astype("int"),
                chronicStudentsLeastOne=lambda df_: df_.chronicStudentsLeastOne.astype(
                    "int"
                ),
                chronicStudentsLeastTwo=lambda df_: df_.chronicStudentsLeastTwo.astype(
                    "int"
                ),
            )
            .loc[
                :,
                [
                    "totalStudents",
                    "studentsLeastOne",
                    "percentLeastOne",
                    "studentsLeastTwo",
                    "percentLeastTwo",
                    "totalIncidents",
                    "totalChronicStudents",
                    "chronicStudentsLeastOne",
                    "percentChronicLeastOne",
                    "chronicStudentsLeastTwo",
                    "percentChronicLeastTwo",
                    "notChronicStudents",
                    "notStudentsLeastOne",
                    "percentNotChronicLeastOne",
                    "notStudentsLeastTwo",
                    "percentNotChronicLeastTwo",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        self.by_suspension_school.columns.name = ""
