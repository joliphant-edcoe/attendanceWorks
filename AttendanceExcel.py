import pandas as pd
import os
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows


class AttendanceExcelGenerator:
    def __init__(self, attend, truancy, filename, school_type="TK-12"):
        self.adatt = attend
        self.truancy = truancy
        self.filename = filename
        self.school_type = school_type
        self.year = "2024-25"
        self.prior_year_str = (
            str(int(self.year[:4]) - 1) + "-" + str(int(self.year[-2:]) - 1)
        )
        self.two_yr_prior_year_str = (
            str(int(self.year[:4]) - 2) + "-" + str(int(self.year[-2:]) - 2)
        )

        # Tk-12 is the default
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
        self.template_wb = load_workbook(self.template_filepath)
        self.truancy_template_wb = load_workbook(self.truancy_template_filepath)

    def append_data_to_templates(self):

        self._write_df_to_excel(
            "By Grade By Year",
            self.adatt.bygrade,
            [5],
            [1],
            start_row=6,
        )
        self._write_df_to_excel(
            "By Grade By Year",
            self.adatt.bygrade_prior,
            [21],
            [1],
            start_row=22,
            year_str=self.prior_year_str,
        )
        self._write_df_to_excel(
            "By Grade By Year",
            self.adatt.bygrade_two_yr_prior,
            [37],
            [1],
            start_row=38,
            year_str=self.two_yr_prior_year_str,
        )

        self._write_df_to_excel(
            "School Summary", self.adatt.byschool.reset_index(), [2], [6], start_col=1
        )
        self._write_df_to_excel(
            "By Grade, Overall",
            self.adatt.bygrade,
            [2, 25, 25, 48, 48],
            [4, 2, 8, 2, 8],
        )
        self._write_df_to_excel(
            "By Race, Ethnicity",
            self.adatt.byrace,
            [2, 18, 18, 39, 39, 60],
            [4, 2, 9, 2, 9, 5],
        )
        self._write_df_to_excel(
            "By Gender", self.adatt.bygender, [2, 12, 12, 33, 33], [5, 2, 8, 2, 8]
        )
        self._write_df_to_excel(
            "By Race & Gender",
            self.adatt.byracegender,
            [2, 26, 47],
            [4, 2, 2],
            start_col=3,
        )
        self._write_df_to_excel(
            "By Race & Grade",
            self.adatt.byracegrade,
            [2, 92, 116],
            [4, 2, 3],
            start_col=3,
        )
        self._write_df_to_excel(
            "By Sp Needs Status", self.adatt.byIEP, [2, 12, 12], [3, 2, 8]
        )
        self._write_df_to_excel(
            "By EL Status", self.adatt.byEngLearner, [2, 12, 12], [3, 2, 8]
        )
        self._write_df_to_excel(
            "By Lunch Status", self.adatt.byFreeReduced, [2, 12, 12], [3, 2, 8]
        )
        self._write_df_to_excel(
            "By Zip code",
            self.adatt.byzipcode.reset_index().iloc[:-1, :].iloc[:20, :],
            [2, 30, 53, 75, 96],
            [4, 6, 6, 6, 6],
            start_col=1,
        )
        self._write_df_to_excel(
            "By Zip code",
            self.adatt.byzipcode.reset_index().iloc[-1, :].to_frame().T,
            start_col=1,
            start_row=26,
        )
        self._write_df_to_excel(
            "Suspensions in Each School",
            self.adatt.by_suspension_school.reset_index(),
            [2],
            [8],
            start_col=1,
            start_row=5,
        )

        self._write_df_to_excel(
            "List of students",
            self.adatt.all_students,
            [2],
            [1],
            start_row=4,
            start_col=1,
        )

        self.template_wb.save(self.filename)

    def _write_df_to_excel(
        self,
        sheet_name,
        data_df,
        year_r_list=[],
        year_c_list=[],
        start_row=6,
        start_col=2,
        year_str=None,
    ):
        if not year_str:
            year_str = self.year

        ws = self.template_wb[sheet_name]
        # print(data_df)
        rows = dataframe_to_rows(data_df, index=False, header=False)

        for r_idx, row in enumerate(rows, start_row):
            for c_idx, value in enumerate(row, start_col):
                ws.cell(row=r_idx, column=c_idx, value=value)

        for r, c in zip(year_r_list, year_c_list):
            ws.cell(row=r, column=c, value=year_str)
