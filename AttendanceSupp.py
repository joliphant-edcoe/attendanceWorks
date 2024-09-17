import pandas as pd


class AttendanceTruancySupp:
    def __init__(
        self,
        current_stu_datafile,
        school_type="TK-12",
        date_range=None,
    ):
        self.current_stu_datafile = current_stu_datafile
        self.school_type = school_type
        self.date_range = date_range
        self.standard_columns = {
            "NumStudents": "Num Students",
            "ExcusedAbsences": "NUMBER of Excused Absences",
            "percentExcused": "PERCENT of Absences Excused",
            "UnexcusedAbsences": "NUMBER of Unexcused Absences",
            "percentUnexcused": "PERCENT of Absences Unexcused",
            "DaysSuspended": "NUMBER of Days Suspended",
            "percentSuspension": "PERCENT of Absences due to Suspension",
            "TotalDaysAbsent": "Total Number of Absences",
            "totalEnrollment": "Total Enrollment (TK-12)",
            "chronicAbsent": "Number Chronically Absent",
            "percentChronic": "Percent of School Chronically Absent",
            "NoNotifications": "No Notifications",
            "percentNoNotification": "No Notifications PERCENT",
            "ExcessiveAbsenceLetter": "Excessive Absence Letter (only)",
            "percentExcessive": "Excessive Absence Letter (only) PERCENT",
            "NoticeofTruancy": "Notice of Truancy (only)",
            "percentNotice": "Notice of Truancy (only) PERCENT",
            "BOTHLetterANDNotice": "BOTH: Excessive Absence Letter AND Notice of Truancy",
            "percentBoth": "BOTH: Excessive Absence Letter AND Notice of Truancy PERCENT",
            "ZeroNOTs": "Zero NOTs",
            "percentZeroNOT": "PERCENT Zero NOTs",
            "OneNOT": "One Notices",
            "percentOneNOT": "PERCENT One NOT",
            "TwoNOT": "Two Notices",
            "percentTwoNOT": "PERCENT Two Notices",
            "ThreeMoreNOT": "Three or More Notices",
            "percentThreeMoreNOT": "PERCENT Three or More",
            "PctOfGrade": "Pct of Grade",
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

    def tweak_student(self):
        df = self.current_stu_data

        yesno_type = pd.CategoricalDtype(
            categories=[
                "YES",
                "NO",
            ],
            ordered=True,
        )

        Chronic_type = pd.CategoricalDtype(
            categories=["Chronically Absent", "Not Chronically Absent"],
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

        self.clean_student_data = (
            df.assign(
                TotalDaysAbsent=df.ExcusedAbsences
                + df.UnexcusedAbsences
                + df.DaysSuspended
            )
            .assign(
                AbsentPercentage=lambda df_: df_.TotalDaysAbsent
                / (df_.TotalDaysAbsent + df_.DaysPresent),
                Category=lambda df_: df_.AbsentPercentage.apply(categorize_absentee),
                ChronicAbsentee=lambda df_: df_.Category.isin(
                    ["moderate chronic", "severe chronic"]
                ).map({True: "Chronically Absent", False: "Not Chronically Absent"}),
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
                    "ChronicAbsentee": Chronic_type,
                }
            )
        )

    def report_all_students(self):

        # print(self.clean_student_data)
        # print(self.clean_student_data.columns)

        self.all_students = (
            self.clean_student_data.query('Category != "satisfactory"')
            .sort_values(["Category", "SchoolName", "IncidentsOfSuspension"])
            .loc[
                :,
                [
                    "FirstName",
                    "MiddleName",
                    "LastName",
                    "ID",
                    "SchoolName",
                    "Category",
                    "TotalDaysAbsent",
                    "ExcusedAbsences",
                    "UnexcusedAbsences",
                    "DaysSuspended",
                    "IncidentsOfSuspension",
                    "TruancyLetterNotification",
                    "ExcessiveAbsentLetters",
                ],
            ]
        )

    def report_absence_types(self):

        chronic_absent = (
            self.clean_student_data.query(
                'Category == "moderate chronic" | Category == "severe chronic"'
            )
            .agg(
                {
                    "ID": "count",
                    "ExcusedAbsences": "sum",
                    "UnexcusedAbsences": "sum",
                    "DaysSuspended": "sum",
                    "TotalDaysAbsent": "sum",
                }
            )
            .rename("Chronically Absent Students")
        )

        not_chronic_absent = (
            self.clean_student_data.query(
                'Category == "at risk" | Category == "satisfactory"'
            )
            .agg(
                {
                    "ID": "count",
                    "ExcusedAbsences": "sum",
                    "UnexcusedAbsences": "sum",
                    "DaysSuspended": "sum",
                    "TotalDaysAbsent": "sum",
                }
            )
            .rename("Non-chronically Absent Students")
        )

        self.absence_types = pd.concat(
            [chronic_absent, not_chronic_absent], axis=1
        ).T.rename(columns={"ID": "NumStudents"})

        total_row = (
            self.absence_types.sum(0).to_frame().rename(columns={0: "All Students"}).T
        )
        self.absence_types = (
            pd.concat([self.absence_types, total_row])
            .assign(
                TotalDaysAbsent=lambda df_: df_.TotalDaysAbsent + df_.DaysSuspended,
                percentExcused=lambda df_: df_.ExcusedAbsences / df_.TotalDaysAbsent,
                percentUnexcused=lambda df_: df_.UnexcusedAbsences
                / df_.TotalDaysAbsent,
                percentSuspension=lambda df_: df_.DaysSuspended / df_.TotalDaysAbsent,
            )
            .rename_axis("Student Category")
            .loc[
                :,
                [
                    "NumStudents",
                    "ExcusedAbsences",
                    "percentExcused",
                    "UnexcusedAbsences",
                    "percentUnexcused",
                    "DaysSuspended",
                    "percentSuspension",
                    "TotalDaysAbsent",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        self.absence_types.columns.name = ''

    def report_absence_by_school(self):

        def count_chronic(series):
            return series.isin(["moderate chronic", "severe chronic"]).sum()

        self.absence_by_school = (
            self.clean_student_data.groupby("SchoolName")
            .agg(
                totalEnrollment=("ID", "count"),
                chronicAbsent=(
                    "Category",
                    count_chronic,
                ),
                ExcusedAbsences=("ExcusedAbsences", "sum"),
                UnexcusedAbsences=("UnexcusedAbsences", "sum"),
                DaysSuspended=("DaysSuspended", "sum"),
                TotalDaysAbsent=("TotalDaysAbsent", "sum"),
            )
            .assign(
                TotalDaysAbsent=lambda df_: df_.TotalDaysAbsent + df_.DaysSuspended,
                percentChronic=lambda df_: df_.chronicAbsent / df_.totalEnrollment,
                percentExcused=lambda df_: df_.ExcusedAbsences / df_.TotalDaysAbsent,
                percentUnexcused=lambda df_: df_.UnexcusedAbsences
                / df_.TotalDaysAbsent,
                percentSuspension=lambda df_: df_.DaysSuspended / df_.TotalDaysAbsent,
            )
            .rename_axis("School Name")
            .loc[
                :,
                [
                    "totalEnrollment",
                    "chronicAbsent",
                    "percentChronic",
                    "ExcusedAbsences",
                    "percentExcused",
                    "UnexcusedAbsences",
                    "percentUnexcused",
                    "DaysSuspended",
                    "percentSuspension",
                    "TotalDaysAbsent",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        self.absence_by_school.columns.name = ''


    def report_absence_by_gender(self):

        self.absence_by_gender = self.clean_student_data.groupby(
            ["ChronicAbsentee", "Gender"], observed=False
        ).agg(
            totalEnrollment=("ID", "count"),
            ExcusedAbsences=("ExcusedAbsences", "sum"),
            UnexcusedAbsences=("UnexcusedAbsences", "sum"),
            DaysSuspended=("DaysSuspended", "sum"),
            TotalDaysAbsent=("TotalDaysAbsent", "sum"),
        )
        total_row = self.absence_by_gender.groupby(level=1, observed=False).sum(0)  #
        total_row = pd.concat({"All Students": total_row})
        self.absence_by_gender = (
            pd.concat([self.absence_by_gender, total_row])
            .assign(
                percentExcused=lambda df_: df_.ExcusedAbsences / df_.TotalDaysAbsent,
                percentUnexcused=lambda df_: df_.UnexcusedAbsences
                / df_.TotalDaysAbsent,
                percentSuspension=lambda df_: df_.DaysSuspended / df_.TotalDaysAbsent,
            )
            .rename_axis(["Student Category", "Gender"])
            .loc[
                :,
                [
                    "totalEnrollment",
                    "ExcusedAbsences",
                    "percentExcused",
                    "UnexcusedAbsences",
                    "percentUnexcused",
                    "DaysSuspended",
                    "percentSuspension",
                    "TotalDaysAbsent",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        self.absence_by_gender.columns.name=''

    def report_absence_by_grade(self):

        self.absence_by_grade = self.clean_student_data.groupby(
            ["ChronicAbsentee", "Grade"], observed=False
        ).agg(
            totalEnrollment=("ID", "count"),
            ExcusedAbsences=("ExcusedAbsences", "sum"),
            UnexcusedAbsences=("UnexcusedAbsences", "sum"),
            DaysSuspended=("DaysSuspended", "sum"),
            TotalDaysAbsent=("TotalDaysAbsent", "sum"),
        )
        total_row = self.absence_by_grade.groupby(level=1, observed=False).sum(0)  #
        total_row = pd.concat({"All Students": total_row})
        self.absence_by_grade = (
            pd.concat([self.absence_by_grade, total_row])
            .assign(
                percentExcused=lambda df_: df_.ExcusedAbsences / df_.TotalDaysAbsent,
                percentUnexcused=lambda df_: df_.UnexcusedAbsences
                / df_.TotalDaysAbsent,
                percentSuspension=lambda df_: df_.DaysSuspended / df_.TotalDaysAbsent,
            )
            .rename_axis(["Student Category", "Grade"])
            .loc[
                :,
                [
                    "totalEnrollment",
                    "ExcusedAbsences",
                    "percentExcused",
                    "UnexcusedAbsences",
                    "percentUnexcused",
                    "DaysSuspended",
                    "percentSuspension",
                    "TotalDaysAbsent",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        self.absence_by_grade.columns.name = ''

    def report_absence_by_race(self):

        self.absence_by_race = self.clean_student_data.groupby(
            ["ChronicAbsentee", "Race"], observed=False
        ).agg(
            totalEnrollment=("ID", "count"),
            ExcusedAbsences=("ExcusedAbsences", "sum"),
            UnexcusedAbsences=("UnexcusedAbsences", "sum"),
            DaysSuspended=("DaysSuspended", "sum"),
            TotalDaysAbsent=("TotalDaysAbsent", "sum"),
        )
        total_row = self.absence_by_race.groupby(level=1, observed=False).sum(0)  #
        total_row = pd.concat({"All Students": total_row})
        self.absence_by_race = (
            pd.concat([self.absence_by_race, total_row])
            .assign(
                percentExcused=lambda df_: df_.ExcusedAbsences / df_.TotalDaysAbsent,
                percentUnexcused=lambda df_: df_.UnexcusedAbsences
                / df_.TotalDaysAbsent,
                percentSuspension=lambda df_: df_.DaysSuspended / df_.TotalDaysAbsent,
            )
            .rename_axis(["Student Category", "Race/Ethnicity"])
            .loc[
                :,
                [
                    "totalEnrollment",
                    "ExcusedAbsences",
                    "percentExcused",
                    "UnexcusedAbsences",
                    "percentUnexcused",
                    "DaysSuspended",
                    "percentSuspension",
                    "TotalDaysAbsent",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        self.absence_by_race.columns.name=''

    def report_absence_by_race_gender(self):

        # chronic absent
        self.absence_by_racegender = (
            self.clean_student_data.query('ChronicAbsentee == "Chronically Absent"')
            .groupby(["Race", "Gender"], observed=False)
            .agg(
                NumStudents=("ID", "count"),
                ExcusedAbsences=("ExcusedAbsences", "sum"),
                UnexcusedAbsences=("UnexcusedAbsences", "sum"),
                DaysSuspended=("DaysSuspended", "sum"),
                TotalDaysAbsent=("TotalDaysAbsent", "sum"),
            )
        )
        total_row = self.absence_by_racegender.groupby(level=1, observed=False).sum(
            0
        )  #
        total_row = pd.concat({"All Students": total_row})
        self.absence_by_racegender = (
            pd.concat([self.absence_by_racegender, total_row])
            .assign(
                percentExcused=lambda df_: df_.ExcusedAbsences / df_.TotalDaysAbsent,
                percentUnexcused=lambda df_: df_.UnexcusedAbsences
                / df_.TotalDaysAbsent,
                percentSuspension=lambda df_: df_.DaysSuspended / df_.TotalDaysAbsent,
            )
            .rename_axis(["Race/Ethnicity", "Gender"])
            .loc[
                :,
                [
                    "NumStudents",
                    "ExcusedAbsences",
                    "percentExcused",
                    "UnexcusedAbsences",
                    "percentUnexcused",
                    "DaysSuspended",
                    "percentSuspension",
                    "TotalDaysAbsent",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        self.absence_by_racegender.columns.name = ''

        # not chronic absent
        self.absence_by_racegender_not = (
            self.clean_student_data.query('ChronicAbsentee == "Not Chronically Absent"')
            .groupby(["Race", "Gender"], observed=False)
            .agg(
                NumStudents=("ID", "count"),
                ExcusedAbsences=("ExcusedAbsences", "sum"),
                UnexcusedAbsences=("UnexcusedAbsences", "sum"),
                DaysSuspended=("DaysSuspended", "sum"),
                TotalDaysAbsent=("TotalDaysAbsent", "sum"),
            )
        )
        total_row = self.absence_by_racegender_not.groupby(level=1, observed=False).sum(
            0
        )  #
        total_row = pd.concat({"All Students": total_row})
        self.absence_by_racegender_not = (
            pd.concat([self.absence_by_racegender_not, total_row])
            .assign(
                percentExcused=lambda df_: df_.ExcusedAbsences / df_.TotalDaysAbsent,
                percentUnexcused=lambda df_: df_.UnexcusedAbsences
                / df_.TotalDaysAbsent,
                percentSuspension=lambda df_: df_.DaysSuspended / df_.TotalDaysAbsent,
            )
            .rename_axis(["Race/Ethnicity", "Gender"])
            .loc[
                :,
                [
                    "NumStudents",
                    "ExcusedAbsences",
                    "percentExcused",
                    "UnexcusedAbsences",
                    "percentUnexcused",
                    "DaysSuspended",
                    "percentSuspension",
                    "TotalDaysAbsent",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        self.absence_by_racegender_not.columns.name = ''

    def report_part1_notified(self):

        def categorize_notifications(group):
            return pd.Series(
                [
                    len(group),
                    len(
                        group.query(
                            'ExcessiveAbsentLetters == "NO" & TruancyLetterNotification == 0'
                        )
                    ),
                    len(
                        group.query(
                            'ExcessiveAbsentLetters == "YES" & TruancyLetterNotification == 0'
                        )
                    ),
                    len(
                        group.query(
                            'ExcessiveAbsentLetters == "NO" & TruancyLetterNotification > 0'
                        )
                    ),
                    len(
                        group.query(
                            'ExcessiveAbsentLetters == "YES" & TruancyLetterNotification > 0'
                        )
                    ),
                ],
                index=[
                    "NumStudents",
                    "NoNotifications",
                    "ExcessiveAbsenceLetter",
                    "NoticeofTruancy",
                    "BOTHLetterANDNotice",
                ],
            )

        self.part1_notifications = self.clean_student_data.groupby(
            "ChronicAbsentee", observed=False
        ).apply(categorize_notifications)

        total_row = (
            self.part1_notifications.sum(0)
            .to_frame()
            .rename(columns={0: "All Students"})
            .T
        )
        self.part1_notifications = (
            pd.concat([self.part1_notifications, total_row])
            .assign(
                percentNoNotification=lambda df_: df_.NoNotifications / df_.NumStudents,
                percentExcessive=lambda df_: df_.ExcessiveAbsenceLetter
                / df_.NumStudents,
                percentNotice=lambda df_: df_.NoticeofTruancy / df_.NumStudents,
                percentBoth=lambda df_: df_.BOTHLetterANDNotice / df_.NumStudents,
            )
            .rename_axis(["Student Category"])
            .loc[
                :,
                [
                    "NumStudents",
                    "NoNotifications",
                    "percentNoNotification",
                    "ExcessiveAbsenceLetter",
                    "percentExcessive",
                    "NoticeofTruancy",
                    "percentNotice",
                    "BOTHLetterANDNotice",
                    "percentBoth",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        self.part1_notifications.columns.name = ''

    def report_part2_notified(self):

        def categorize_notifications(group):
            return pd.Series(
                [
                    len(group.query("TruancyLetterNotification == 0")),
                    len(group.query("TruancyLetterNotification == 1")),
                    len(group.query("TruancyLetterNotification == 2")),
                    len(group.query("TruancyLetterNotification >= 3")),
                    len(group),
                ],
                index=[
                    "ZeroNOTs",
                    "OneNOT",
                    "TwoNOT",
                    "ThreeMoreNOT",
                    "NumStudents",
                ],
            )

        self.part2_notifications = self.clean_student_data.groupby(
            "ChronicAbsentee", observed=False
        ).apply(categorize_notifications)

        total_row = (
            self.part2_notifications.sum(0)
            .to_frame()
            .rename(columns={0: "All Students"})
            .T
        )
        self.part2_notifications = (
            pd.concat([self.part2_notifications, total_row])
            .assign(
                percentZeroNOT=lambda df_: df_.ZeroNOTs / df_.NumStudents,
                percentOneNOT=lambda df_: df_.OneNOT / df_.NumStudents,
                percentTwoNOT=lambda df_: df_.TwoNOT / df_.NumStudents,
                percentThreeMoreNOT=lambda df_: df_.ThreeMoreNOT / df_.NumStudents,
            )
            .rename_axis(["Student Category"])
            .loc[
                :,
                [
                    "ZeroNOTs",
                    "percentZeroNOT",
                    "OneNOT",
                    "percentOneNOT",
                    "TwoNOT",
                    "percentTwoNOT",
                    "ThreeMoreNOT",
                    "percentThreeMoreNOT",
                    "NumStudents",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        self.part2_notifications.columns.name = ''

    def report_part1_grade_notified(self):

        def categorize_notifications(group):
            chronic_group = group.query('ChronicAbsentee == "Chronically Absent"')
            chronic_group_count = chronic_group.shape[0]
            no_notif = len(
                chronic_group.query(
                    'ExcessiveAbsentLetters == "NO" & TruancyLetterNotification == 0'
                )
            )
            letter_only = len(
                chronic_group.query(
                    'ExcessiveAbsentLetters == "YES" & TruancyLetterNotification == 0'
                )
            )
            notice_only = len(
                chronic_group.query(
                    'ExcessiveAbsentLetters == "NO" & TruancyLetterNotification > 0'
                )
            )
            letter_and_notice = len(
                chronic_group.query(
                    'ExcessiveAbsentLetters == "YES" & TruancyLetterNotification > 0'
                )
            )
            return pd.Series(
                [
                    chronic_group_count,
                    no_notif,
                    letter_only,
                    notice_only,
                    letter_and_notice,
                ],
                index=[
                    "NumStudents",
                    "NoNotifications",
                    "ExcessiveAbsenceLetter",
                    "NoticeofTruancy",
                    "BOTHLetterANDNotice",
                ],
            )

        self.part1_grade_notifications = self.clean_student_data.groupby(
            "Grade", observed=False
        ).apply(categorize_notifications)

        grade_counts = self.clean_student_data.groupby(
            "Grade", observed=False
        ).ID.count()

        self.part1_grade_notifications = pd.concat(
            [self.part1_grade_notifications, grade_counts], axis=1
        )

        total_row = (
            self.part1_grade_notifications.sum(0)
            .to_frame()
            .rename(columns={0: "All Students"})
            .T
        )

        self.part1_grade_notifications = (
            pd.concat([self.part1_grade_notifications, total_row])
            .assign(
                PctOfGrade=lambda df_: df_.NumStudents / df_.ID,
                percentNoNotification=lambda df_: df_.NoNotifications / df_.NumStudents,
                percentExcessive=lambda df_: df_.ExcessiveAbsenceLetter
                / df_.NumStudents,
                percentNotice=lambda df_: df_.NoticeofTruancy / df_.NumStudents,
                percentBoth=lambda df_: df_.BOTHLetterANDNotice / df_.NumStudents,
            )
            .rename_axis(["Grade Level"])
            .loc[
                :,
                [
                    "NumStudents",
                    "PctOfGrade",
                    "NoNotifications",
                    "percentNoNotification",
                    "ExcessiveAbsenceLetter",
                    "percentExcessive",
                    "NoticeofTruancy",
                    "percentNotice",
                    "BOTHLetterANDNotice",
                    "percentBoth",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        self.part1_grade_notifications.columns.name = ''

    def report_part2_grade_notified(self):

        def categorize_notifications(group):
            return pd.Series(
                [
                    len(group.query("TruancyLetterNotification == 0")),
                    len(group.query("TruancyLetterNotification == 1")),
                    len(group.query("TruancyLetterNotification == 2")),
                    len(group.query("TruancyLetterNotification >= 3")),
                    len(group),
                ],
                index=[
                    "ZeroNOTs",
                    "OneNOT",
                    "TwoNOT",
                    "ThreeMoreNOT",
                    "NumStudents",
                ],
            )

        self.part2_grade_notifications = (
            self.clean_student_data.query('ChronicAbsentee == "Chronically Absent"')
            .groupby("Grade", observed=False)
            .apply(categorize_notifications)
        )

        grade_counts = self.clean_student_data.groupby(
            "Grade", observed=False
        ).ID.count()

        self.part2_grade_notifications = pd.concat(
            [self.part2_grade_notifications, grade_counts], axis=1
        )

        total_row = (
            self.part2_grade_notifications.sum(0)
            .to_frame()
            .rename(columns={0: "All Students"})
            .T
        )

        self.part2_grade_notifications = (
            pd.concat([self.part2_grade_notifications, total_row])
            .assign(
                PctOfGrade=lambda df_: df_.NumStudents / df_.ID,
                percentZeroNOT=lambda df_: df_.ZeroNOTs / df_.NumStudents,
                percentOneNOT=lambda df_: df_.OneNOT / df_.NumStudents,
                percentTwoNOT=lambda df_: df_.TwoNOT / df_.NumStudents,
                percentThreeMoreNOT=lambda df_: df_.ThreeMoreNOT / df_.NumStudents,
            )
            .rename_axis(["Grade Level"])
            .loc[
                :,
                [
                    "NumStudents",
                    "PctOfGrade",
                    "ZeroNOTs",
                    "percentZeroNOT",
                    "OneNOT",
                    "percentOneNOT",
                    "TwoNOT",
                    "percentTwoNOT",
                    "ThreeMoreNOT",
                    "percentThreeMoreNOT",
                ],
            ]
            .rename(columns=self.standard_columns)
        )
        self.part2_grade_notifications.columns.name = ''

    def report_part3_grade_notified(self):

        def categorize_notifications(group):
            letter = len(group.query('ExcessiveAbsentLetters == "YES"'))
            return pd.Series(
                [
                    len(group),
                    letter,
                ],
                index=[
                    "NumStudents",
                    "ExcessiveAbsenceLetter",
                ],
            )

        self.part3_grade_notifications = (
            self.clean_student_data.query('ChronicAbsentee == "Chronically Absent"')
            .groupby("Grade", observed=False)
            .apply(categorize_notifications)
        )

        grade_counts = self.clean_student_data.groupby(
            "Grade", observed=False
        ).ID.count()

        self.part3_grade_notifications = pd.concat(
            [self.part3_grade_notifications, grade_counts], axis=1
        )

        total_row = (
            self.part3_grade_notifications.sum(0)
            .to_frame()
            .rename(columns={0: "All Students"})
            .T
        )

        self.part3_grade_notifications = (
            pd.concat([self.part3_grade_notifications, total_row])
            .assign(
                PctOfGrade=lambda df_: df_.NumStudents / df_.ID,
                percentExcessive=lambda df_: df_.ExcessiveAbsenceLetter
                / df_.NumStudents,
            )
            .rename_axis(["Grade Level"])
            .loc[
                :,
                [
                    "PctOfGrade",
                    "ExcessiveAbsenceLetter",
                    "percentExcessive",
                ],
            ]
            .rename(
                columns={
                    "ExcessiveAbsenceLetter": "Sent Excessive Absence Letter",
                    "percentExcessive": "Sent Excessive Absence Letter PERCENT",
                }
            )
            .rename(columns=self.standard_columns)
        )
        self.part3_grade_notifications.columns.name = ''

    def report_part1_school_notified(self):

        def categorize_notifications(group):
            chronic_group = group.query('ChronicAbsentee == "Chronically Absent"')
            chronic_group_count = chronic_group.shape[0]
            no_notif = len(
                chronic_group.query(
                    'ExcessiveAbsentLetters == "NO" & TruancyLetterNotification == 0'
                )
            )
            letter_only = len(
                chronic_group.query(
                    'ExcessiveAbsentLetters == "YES" & TruancyLetterNotification == 0'
                )
            )
            notice_only = len(
                chronic_group.query(
                    'ExcessiveAbsentLetters == "NO" & TruancyLetterNotification > 0'
                )
            )
            letter_and_notice = len(
                chronic_group.query(
                    'ExcessiveAbsentLetters == "YES" & TruancyLetterNotification > 0'
                )
            )
            return pd.Series(
                [
                    chronic_group_count,
                    no_notif,
                    letter_only,
                    notice_only,
                    letter_and_notice,
                ],
                index=[
                    "NumStudents",
                    "NoNotifications",
                    "ExcessiveAbsenceLetter",
                    "NoticeofTruancy",
                    "BOTHLetterANDNotice",
                ],
            )

        self.part1_school_notifications = self.clean_student_data.groupby(
            "SchoolName", observed=False
        ).apply(categorize_notifications)

        school_counts = self.clean_student_data.groupby(
            "SchoolName", observed=False
        ).ID.count()

        self.part1_school_notifications = pd.concat(
            [self.part1_school_notifications, school_counts], axis=1
        )

        self.part1_school_notifications = (
            self.part1_school_notifications.assign(
                PctOfGrade=lambda df_: df_.NumStudents / df_.ID,
                percentNoNotification=lambda df_: df_.NoNotifications / df_.NumStudents,
                percentExcessive=lambda df_: df_.ExcessiveAbsenceLetter
                / df_.NumStudents,
                percentNotice=lambda df_: df_.NoticeofTruancy / df_.NumStudents,
                percentBoth=lambda df_: df_.BOTHLetterANDNotice / df_.NumStudents,
            )
            .rename_axis(["School Name"])
            .loc[
                :,
                [
                    "ID",
                    "NumStudents",
                    "PctOfGrade",
                    "NoNotifications",
                    "percentNoNotification",
                    "ExcessiveAbsenceLetter",
                    "percentExcessive",
                    "NoticeofTruancy",
                    "percentNotice",
                    "BOTHLetterANDNotice",
                    "percentBoth",
                ],
            ]
            .rename(columns={"ID": "Total Enrollment"})
            .rename(columns=self.standard_columns)
        )
        self.part1_school_notifications.columns.name = ''

    def report_part2_school_notified(self):

        def categorize_notifications(group):
            group = group.query('ChronicAbsentee == "Chronically Absent"')
            return pd.Series(
                [
                    len(group.query("TruancyLetterNotification == 0")),
                    len(group.query("TruancyLetterNotification == 1")),
                    len(group.query("TruancyLetterNotification == 2")),
                    len(group.query("TruancyLetterNotification >= 3")),
                    len(group),
                ],
                index=[
                    "ZeroNOTs",
                    "OneNOT",
                    "TwoNOT",
                    "ThreeMoreNOT",
                    "NumStudents",
                ],
            )

        self.part2_school_notifications = (
            self.clean_student_data
            .groupby("SchoolName", observed=False)
            .apply(categorize_notifications)
        )

        grade_counts = self.clean_student_data.groupby(
            "SchoolName", observed=False
        ).ID.count()

        self.part2_school_notifications = pd.concat(
            [self.part2_school_notifications, grade_counts], axis=1
        )

        self.part2_school_notifications = (
            self.part2_school_notifications.assign(
                PctOfGrade=lambda df_: df_.NumStudents / df_.ID,
                percentZeroNOT=lambda df_: df_.ZeroNOTs / df_.NumStudents,
                percentOneNOT=lambda df_: df_.OneNOT / df_.NumStudents,
                percentTwoNOT=lambda df_: df_.TwoNOT / df_.NumStudents,
                percentThreeMoreNOT=lambda df_: df_.ThreeMoreNOT / df_.NumStudents,
            )
            .rename_axis(["School Name"])
            .loc[
                :,
                [
                    "ID",
                    "NumStudents",
                    "PctOfGrade",
                    "ZeroNOTs",
                    "percentZeroNOT",
                    "OneNOT",
                    "percentOneNOT",
                    "TwoNOT",
                    "percentTwoNOT",
                    "ThreeMoreNOT",
                    "percentThreeMoreNOT",
                ],
            ]
            .rename(columns={"ID": "Total Enrollment"})
            .rename(columns=self.standard_columns)
        )
        self.part2_school_notifications.columns.name = ''

    def report_part3_school_notified(self):

        def categorize_notifications(group):
            group = group.query('ChronicAbsentee == "Chronically Absent"')
            letter = len(group.query('ExcessiveAbsentLetters == "YES"'))
            return pd.Series(
                [
                    len(group),
                    letter,
                ],
                index=[
                    "NumStudents",
                    "ExcessiveAbsenceLetter",
                ],
            )

        self.part3_school_notifications = (
            self.clean_student_data
            .groupby("SchoolName", observed=False)
            .apply(categorize_notifications)
        )

        school_counts = self.clean_student_data.groupby(
            "SchoolName", observed=False
        ).ID.count()

        self.part3_school_notifications = pd.concat(
            [self.part3_school_notifications, school_counts], axis=1
        )

        self.part3_school_notifications = (
            self.part3_school_notifications.assign(
                PctOfGrade=lambda df_: df_.NumStudents / df_.ID,
                percentExcessive=lambda df_: df_.ExcessiveAbsenceLetter
                / df_.NumStudents,
            )
            .rename_axis(["School Name"])
            .loc[
                :,
                [
                    "ID",
                    "NumStudents",
                    "PctOfGrade",
                    "ExcessiveAbsenceLetter",
                    "percentExcessive",
                ],
            ]
            .rename(
                columns={
                    "ExcessiveAbsenceLetter": "Sent Excessive Absence Letter",
                    "percentExcessive": "Sent Excessive Absence Letter PERCENT",
                    "ID": "Total Enrollment",
                }
            )
            .rename(columns=self.standard_columns)
        )
        self.part3_school_notifications.columns.name = ''
