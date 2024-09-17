import pandas as pd
import os


class AttendanceExcelGenerator:
    def __init__(self, attend, truancy, filename, school_type="TK-12"):
        self.adatt = attend
        self.truancy = truancy
        self.filename = filename
        self.school_type = school_type
        self.template_filepath = os.path.join(
            os.path.join("templates", "TK12"), "CalDATT_TK_12_Template.xlsx"
        )
        self.truancy_template_filepath = os.path.join(
            os.path.join("templates", "TK12"), "CalDATT_TK_12_Truancy_Template.xlsx"
        )

        if self.school_type == "TK-8":
            self.template_filepath = os.path.join(
                os.path.join("templates", "TK8"), "CalDATT_TK_8_Template.xlsx"
            )
            self.truancy_template_filepath = os.path.join(
                os.path.join("templates", "TK8"), "CalDATT_TK_8_Truancy_Template.xlsx"
            )
        elif self.school_type == "HS":
            self.template_filepath = os.path.join(
                os.path.join("templates", "912"), "CalDATT_9_12_Template.xlsx"
            )
            self.truancy_template_filepath = os.path.join(
                os.path.join("templates", "912"), "CalDATT_9_12_Truancy_Template.xlsx"
            )

        print(
            f"using templates {self.template_filepath} and {self.truancy_template_filepath}"
        )

    def create_excel(self):

        # ws = wb.create_sheet(title="By Zip code")
        with pd.ExcelWriter(self.filename, engine="xlsxwriter") as writer:
            self.adatt.byschool.to_excel(
                writer,
                sheet_name="School Summary",
                header=True,
                index=False,
                startrow=4,
            )
            self.adatt.bygrade.to_excel(
                writer,
                sheet_name="By Grade, Overall",
                header=True,
                index=False,
                startrow=4,
            )
            self.adatt.byrace.to_excel(
                writer,
                sheet_name="By Race, Ethnicity",
                header=True,
                index=False,
                startrow=4,
            )
            self.adatt.bygender.to_excel(
                writer, sheet_name="By Gender", header=True, index=False, startrow=4
            )
            self.adatt.byracegender.to_excel(
                writer,
                sheet_name="By Race & Gender",
                header=True,
                index=False,
                startrow=4,
            )
            self.adatt.byracegrade.to_excel(
                writer,
                sheet_name="By Race & Grade",
                header=True,
                index=False,
                startrow=4,
            )
            self.adatt.byIEP.to_excel(
                writer,
                sheet_name="By Sp Needs Status",
                header=True,
                index=False,
                startrow=4,
            )
            self.adatt.byEngLearner.to_excel(
                writer, sheet_name="By EL Status", header=True, index=False, startrow=4
            )
            self.adatt.byFreeReduced.to_excel(
                writer,
                sheet_name="By Lunch Status",
                header=True,
                index=False,
                startrow=4,
            )
            self.adatt.byzipcode.to_excel(
                writer, sheet_name="By Zip code", header=True, index=False, startrow=4
            )
            self.adatt.all_students.to_excel(
                writer,
                sheet_name="List of Students",
                header=True,
                index=False,
                startrow=3,
            )

            workbook = writer.book
            worksheet = writer.sheets["School Summary"]

            bold_wrap = workbook.add_format({"bold": True, "text_wrap": True})
            pct = workbook.add_format({"num_format": "0.0%"})

            worksheet.set_row(4, 64, bold_wrap)

            worksheet.set_column(0, 0, 26)
            worksheet.set_column(1, 2, 12, pct)
            worksheet.set_column(3, 26, 12)
            for i in range(4, 26, 2):
                worksheet.set_column(i, i, 12, pct)
            worksheet.set_row(4, 64, bold_wrap)

            worksheet = writer.sheets["List of Students"]
            worksheet.add_table(
                3,
                0,
                len(self.adatt.all_students) + 3,
                5,
                {
                    "columns": [
                        {"header": label}
                        for label in self.adatt.all_students.columns.to_list()
                    ]
                },
            )
            worksheet.autofit()

            worksheet = writer.sheets["By Gender"]
            worksheet.set_column(10, 0, 12, pct)

            chart1 = workbook.add_chart(
                {
                    "type": "column",
                }
            )
            chart1.add_series(
                {
                    "name": ["By Gender", 4, 0],
                    "categories": ["By Gender", 5, 0, 6, 0],
                    "values": ["By Gender", 5, 10, 6, 10],
                }
            )
            worksheet.insert_chart("D26", chart1)

        # severe, moderate, all chronic, at-risk, satisfactory
        report_colors = [
            "ffc000",
            "ffcc99",
            "ff6d6d",
            "ffff99",
            "c3d69b",
        ]
        # wb = pxl.load_workbook("23-24 Cal DATT- TK-12 Template.xlsx")
        # ws = wb["Type Zip codes"]
        # for rowy, row in enumerate(allZips, start=4):
        #     for colx, value in enumerate(row, start=1):
        #         ws.cell(column=colx, row=rowy, value=value)
        # wb.save("final.xlsx")

        # sheets = [
        #     ('file1.csv', 'Sheet A'),
        #     ('file2.csv', 'Sheet B'),
        #     ('file3.csv', 'Sheet C')
        # ]

        # for filename, sheet in sheets:
        #     with open(filename, newline='') as f_input:
        #         ws = wb[sheet]

        # wb.save('data.xlsx')

        # try except for file saving

    #     while True:
    # try:
    #     workbook.close()
    # except xlsxwriter.exceptions.FileCreateError as e:
    #     decision = input("Exception caught in workbook.close(): %s\n"
    #                      "Please close the file if it is open in Excel.\n"
    #                      "Try to write file again? [Y/n]: " % e)
    #     if decision != 'n':
    #         continue

    # break
