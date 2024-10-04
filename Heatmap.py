import pandas as pd

# LIST ATT SC SN DY CD PR GR TR TN AL DT DTS 

class AttendanceHeatMap:
    def __init__(self, att_datafile):
        self.att_datafile = att_datafile

    def tweak_data(self, df):
        daily_absence = (
            df.rename(columns={"Student#": "StudentNumber", "All day": "AllDay"})
            .fillna("00")
            .assign(
                excused=lambda df_:df_.AllDay.isin(["I", "G", "X"]),
                unexcused=lambda df_:df_.AllDay.isin(["N", "O", "S", "U"]),
                unverified=lambda df_:df_.AllDay.isin(["A"]),
            )
            .groupby("Date")
            .agg({"excused": "sum", "unexcused": "sum", "unverified": "sum"})
            .assign(combined=lambda df_: df_.sum(axis=1))
        )

        enroll_changes = (
            df.assign(EntLv=df["Ent/Lv"].map({"E": 1, "L": -1}).fillna(0).astype("int"))
            .groupby("Date")
            .EntLv.sum()
        )

        absence_by_date = pd.concat(
            [daily_absence, enroll_changes.cumsum()], axis=1
        ).assign(pctAbsent=lambda df_: df_.combined / df_.EntLv)

        return absence_by_date

    def read_process_data(self):

        if not self.att_datafile:
            self.clean_absences_by_date = None
            return

        df = pd.read_excel(self.att_datafile, parse_dates=["Date"])
        self.clean_absences_by_date = self.tweak_data(df)

    def return_data_dict(self):
        data_dict = dict()
        data_dict["heatmap"] = self.clean_absences_by_date

        return data_dict
