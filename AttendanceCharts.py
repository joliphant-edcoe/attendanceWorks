import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

sns.set_theme(style="darkgrid")


class AttendanceChartsExcel:
    def __init__(self, attend):
        self.adatt = attend

    def by_grade_charts(self):
        fig, axs = plt.subplots(2, 2, figsize=(12, 12))

        plotdata = self.adatt.bygrade.iloc[:-1, :5].set_index("Grade").iloc[:, [1, 3]]
        ax = axs[0][0]
        plotdata.plot(kind="bar", stacked=True, ax=ax)
        ax.grid(True)
        ax.set_title(
            "What percentage of students in each grade level (and overall)\nhave moderate or severe chronic absence?"
        )
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, 0))

        plotdata = self.adatt.bygrade.iloc[:-1, :5].set_index("Grade").iloc[:, [0, 2]]
        ax = axs[0][1]
        plotdata.plot(kind="bar", stacked=True, ax=ax)
        ax.grid(True)
        ax.set_title(
            "How many students in each grade level (and overall)\nhave moderate or severe chronic absence?"
        )

        plotdata = self.adatt.bygrade.iloc[:-1,]
        ax = axs[1][0]
        sns.barplot(
            data=plotdata,
            x="Grade",
            y="PERCENT satisfactory attendance",
            hue="Grade",
            ax=ax,
        )
        ax.grid(True)
        ax.set_title(
            "What percentage of students in each grade level (and overall)\nhave satisfactory attendance?"
        )
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, 0))

        ax = axs[1][1]
        sns.barplot(
            data=plotdata,
            x="Grade",
            y="NUMBER satisfactory attendance",
            hue="Grade",
            ax=ax,
        )
        ax.grid(True)
        ax.set_title(
            "How many students in each grade level (and overall)\nhave satisfactory attendance?"
        )
        plt.show()

        fig.savefig("charts/by_grade_plots.png")

    def by_race_charts(self):
        fig, axs = plt.subplots(2, 2, figsize=(12, 12))

        plotdata = (
            self.adatt.byrace.iloc[:-2, :5].set_index("Race/Ethnicity").iloc[:, [1, 3]]
        )
        ax = axs[0][0]
        plotdata.plot(kind="bar", stacked=True, ax=ax)
        ax.grid(True)
        ax.set_title(
            "What percentage of students in each race/ethnicity have\nmoderate or severe chronic absence?"
        )
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, 0))

        plotdata = (
            self.adatt.byrace.iloc[:-2, :5].set_index("Race/Ethnicity").iloc[:, [0, 2]]
        )
        ax = axs[0][1]
        plotdata.plot(kind="bar", stacked=True, ax=ax)
        ax.grid(True)
        ax.set_title(
            "How many students in each race/ethnicity have\nmoderate or severe chronic absence?"
        )

        plotdata = self.adatt.byrace.iloc[:-2,]
        ax = axs[1][0]
        sns.barplot(
            data=plotdata,
            x="Race/Ethnicity",
            y="PERCENT satisfactory attendance",
            hue="Race/Ethnicity",
            ax=ax,
        )
        ax.grid(True)
        ax.set_title(
            "What percentage of students in each race/ethnicity have\nsatisfactory attendance?"
        )
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, 0))

        ax = axs[1][1]
        sns.barplot(
            data=plotdata,
            x="Race/Ethnicity",
            y="NUMBER satisfactory attendance",
            hue="Race/Ethnicity",
            ax=ax,
        )
        ax.grid(True)
        ax.set_title(
            "How many students in each race/ethnicity have\nsatisfactory attendance?"
        )
        plt.show()

        fig.savefig("charts/by_race_plots.png")

    def by_gender_charts(self):
        fig, axs = plt.subplots(2, 2, figsize=(12, 12))

        plotdata = self.adatt.bygender.iloc[:2, :5].set_index("Gender").iloc[:, [1, 3]]
        ax = axs[0][0]
        plotdata.plot(kind="bar", stacked=True, ax=ax)
        ax.grid(True)
        ax.set_title(
            "What percentage of boys and girls have moderate or severe\nchronic absence?"
        )
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, 0))

        plotdata = self.adatt.bygender.iloc[:2, :5].set_index("Gender").iloc[:, [0, 2]]
        ax = axs[0][1]
        plotdata.plot(kind="bar", stacked=True, ax=ax)
        ax.grid(True)
        ax.set_title(
            "How many boys and girls have moderate or severe\nchronic absence?"
        )

        plotdata = self.adatt.bygender.iloc[:2,]
        ax = axs[1][0]
        sns.barplot(
            data=plotdata,
            x="Gender",
            y="PERCENT satisfactory attendance",
            hue="Gender",
            ax=ax,
        )
        ax.grid(True)
        ax.set_title("What percentage of boys and girls have\nsatisfactory attendance?")
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, 0))

        ax = axs[1][1]
        sns.barplot(
            data=plotdata,
            x="Gender",
            y="NUMBER satisfactory attendance",
            hue="Gender",
            ax=ax,
        )
        ax.grid(True)
        ax.set_title("How many boys and girls have\nsatisfactory attendance?")
        plt.show()

        fig.savefig("charts/by_gender_plots.png")

    def by_sp_needs_charts(self):
        fig, axs = plt.subplots(1, 2, figsize=(12, 6))

        plotdata = (
            self.adatt.byIEP.iloc[:-1, :5].set_index("IEP Status").iloc[:, [1, 3]]
        )
        ax = axs[0]
        plotdata.plot(kind="bar", stacked=True, ax=ax)
        ax.grid(True)
        ax.set_title(
            "Do students with special needs have higher rates of moderate or\nsevere chronic absence?"
        )
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, 0))

        palette_color = sns.color_palette("deep")
        plotdata = self.adatt.byIEP.set_index("IEP Status").iloc[0, [4, 6, 8]]
        keys = [
            "NUMBER ALL\nchronic absence",
            "NUMBER at-risk\nattendance",
            "NUMBER satisfactory\nattendance",
        ]
        numbers = plotdata.tolist()
        explode = [0.1, 0, 0]
        ax = axs[1]
        plt.pie(
            numbers,
            labels=keys,
            colors=palette_color,
            autopct="%.1f%%",
            explode=explode,
        )
        ax.set_title(
            "What are the attendance patterns of students with\nspecial needs?"
        )

        plt.show()

        fig.savefig("charts/by_sp_needs_plots.png")

    def by_eng_learners_charts(self):
        fig, axs = plt.subplots(1, 2, figsize=(12, 6))

        plotdata = (
            self.adatt.byEngLearner.iloc[:-1, :5].set_index("EL Status").iloc[:, [1, 3]]
        )
        ax = axs[0]
        plotdata.plot(kind="bar", stacked=True, ax=ax)
        ax.grid(True)
        ax.set_title(
            "Do English Learners have different rates of moderate or severe\nchronic absence than students not learning English?"
        )
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, 0))

        palette_color = sns.color_palette("deep")
        plotdata = self.adatt.byEngLearner.set_index("EL Status").iloc[0, [4, 6, 8]]
        keys = [
            "NUMBER ALL\nchronic absence",
            "NUMBER at-risk\nattendance",
            "NUMBER satisfactory\nattendance",
        ]
        numbers = plotdata.tolist()
        explode = [0.1, 0, 0]
        ax = axs[1]
        plt.pie(
            numbers,
            labels=keys,
            colors=palette_color,
            autopct="%.1f%%",
            explode=explode,
        )
        ax.set_title("What are the attendance patterns of English Learners?")

        plt.show()

        fig.savefig("charts/by_eng_learners_plots.png")

    def by_lunch_status_charts(self):
        fig, axs = plt.subplots(1, 2, figsize=(12, 6))

        plotdata = (
            self.adatt.byFreeReduced.iloc[:-1, :5]
            .set_index("Free/Reduced Lunch Status")
            .iloc[:, [1, 3]]
        )
        ax = axs[0]
        plotdata.plot(kind="bar", stacked=True, ax=ax)
        ax.grid(True)
        ax.set_title(
            "Do students with free/reduced lunch status have higher rates of\nchronic or severe chronic absence?"
        )
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, 0))

        palette_color = sns.color_palette("deep")
        plotdata = self.adatt.byFreeReduced.set_index("Free/Reduced Lunch Status").iloc[
            0, [4, 6, 8]
        ]
        keys = [
            "NUMBER ALL\nchronic absence",
            "NUMBER at-risk\nattendance",
            "NUMBER satisfactory\nattendance",
        ]
        numbers = plotdata.tolist()
        explode = [0.1, 0, 0]
        ax = axs[1]
        plt.pie(
            numbers,
            labels=keys,
            colors=palette_color,
            autopct="%.1f%%",
            explode=explode,
        )
        ax.set_title(
            "What are the attendance patterns of district students\nwith Free/Reduced Lunch status?"
        )

        plt.show()

        fig.savefig("charts/by_lunch_status_plots.png")

    def by_zipcode_charts(self):
        fig, axs = plt.subplots(4, 1, figsize=(8, 30))

        plotdata = (
            self.adatt.byzipcode.iloc[:-2, ]
            .sort_values("Total Students", ascending=True)
            .assign(
                Zip=lambda df_: df_["Zip Code"] + " - " + df_["Zip Code Description"]
            )
            .set_index("Zip")
            .iloc[:,[3,5]]
        )
        ax = axs[0]
        plotdata.plot(kind="barh", stacked=True, ax=ax)
        ax.grid(True)
        ax.set_title(
            "What percentage of students in each Zip code have\nmoderate or severe chronic absence?"
        )
        ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0, 0))

        plotdata = (
            self.adatt.byzipcode.iloc[:-2, ]
            .sort_values("Total Students", ascending=True)
            .assign(
                Zip=lambda df_: df_["Zip Code"] + " - " + df_["Zip Code Description"]
            )
            .set_index("Zip")
            .iloc[:,[2,4]]
        )
        ax = axs[1]
        plotdata.plot(kind="barh", stacked=True, ax=ax)
        ax.grid(True)
        ax.set_title(
            "How many students in each Zip code have\nmoderate or severe chronic absence?"
        )

        plotdata = self.adatt.byzipcode.assign(
            Zip=lambda df_: df_["Zip Code"] + " - " + df_["Zip Code Description"]
        ).iloc[:-2, :]
        ax = axs[2]
        sns.barplot(
            data=plotdata,
            x="PERCENT satisfactory attendance",
            y="Zip",
            hue="Zip",
            ax=ax,
        )
        ax.grid(True)
        ax.set_title(
            "What percentage of students in each ZIP code have\nsatisfactory attendance?"
        )
        ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0, 0))

        ax = axs[3]
        sns.barplot(
            data=plotdata,
            x="NUMBER satisfactory attendance",
            y="Zip",
            hue="Zip",
            ax=ax,
        )
        ax.grid(True)
        ax.set_title(
            "How many students in each ZIP code have\nsatisfactory attendance?"
        )

        plt.show()
        fig.savefig("charts/by_zipcode_plots.png")
