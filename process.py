import os
import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
import itertools
plt.rcParams.update({'figure.max_open_warning': 0})
marker = itertools.cycle(('X', '.', '*', 's', '^', 'd'))

def build_us_time_series_csv():
    """
    Make us_time_series.csv for convinience
    :return: us_csv
    """
    csv_file = pd.read_csv("WVS_TimeSeries_1981_2020_ascii_v2_0.csv")
    print("Done reading")
    us_csv = csv_file[csv_file["COUNTRY_ALPHA"] == "USA"]
    us_csv.to_csv("us_time_series.csv", encoding="utf-8", index=False)
    return us_csv


def calc_time_series_single_question(us_csv, question_id, options, reverse=False):
    """
    :param us_csv: pandas csv from us_time_series.csv
    :param question_id: e.g. "A001"
    :param options: options to consider. e.g. [1, 2, 3, 4]
    :param reverse: reverse the strength
    :return: result format: {1982:{"counts": {1: 23, 2: 45, 3: 56, 4: 67}, "avg": 2.87}, "1990":{}, ...}
    """
    years = us_csv["S020"].unique()
    result = {year: {"counts": {}, "avg": 0.0, "strength": 0.0} for year in years}
    for year in years:
        year_csv = us_csv[us_csv["S020"] == year]
        value_counts = dict(year_csv[question_id].value_counts())
        # print(year, value_counts)
        result[year]["counts"] = value_counts
        avg = 0.0
        tot = 0.0
        for option in value_counts.keys():
            if option in options:
                avg += option * value_counts[option]
                tot += value_counts[option]
        if tot == 0.0:
            result[year]["avg"] = np.nan
            result[year]["strength"] = np.nan
        else:
            avg /= tot
            result[year]["avg"] = avg
            result[year]["strength"] = max(options) - avg if reverse else avg
    return result

def plot_time_series(result, label="Time Series", title=""):
    years = sorted(list(result.keys()))
    x = list(range(len(years)))
    y = []
    for year in years:
        y.append(result[year]["strength"])
    plt.plot(x, y, label=label, marker=next(marker))
    plt.xticks(x, years)
    plt.xlabel("Time")
    plt.ylabel("Strength")
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(title)
    plt.subplots_adjust(right=0.6)

def plot_bar_time_series(result, options, title=""):
    years = sorted(list(result.keys()))
    matrix = [[] for _ in years]
    for i, year in enumerate(years):
        for j, opt in enumerate(options):
            if opt not in result[year]["counts"].keys():
                matrix[i].append(np.nan)
            else:
                matrix[i].append(result[year]["counts"][opt])
    matrix = np.array(matrix).astype("float32")
    rowsum = matrix.sum(axis=1).reshape(-1, 1)
    matrix /= rowsum
    matrix_df = pd.DataFrame(matrix, index=years, columns=options)
    fig, ax = plt.subplots(figsize=(12, 6))
    matrix_df.plot(kind='bar', ax=ax)
    plt.xticks(rotation=0)
    plt.title(title)

if __name__ == "__main__":
    # Run this only once
    # build_us_time_series_csv()

    # Read csv from file
    us_csv = pd.read_csv("us_time_series.csv")
    os.makedirs("figs/bar", exist_ok=True)
    os.makedirs("figs/series", exist_ok=True)

    # [Neighbors]
    """
    On this list are various groups of people. 
    Could you please mention any that you would not like to have as neighbors?
    """
    configs = [
        ["A124_02", "Neighbours: People of a different race"],
        ["A124_03", "Neighbours: Heavy drinkers"],
        ["A124_04", "Neighbours: Emotionally unstable people"],
        ["A124_05", "Neighbours: Muslims"],
        ["A124_06", "Neighbours: Immigrants/foreign workers"],
        ["A124_07", "Neighbours: People who have AIDS"],
        ["A124_08", "Neighbours: Drug addicts"],
        ["A124_09", "Neighbours: Homosexuals"],
        ["A124_12", "Neighbours: People of a different religion"]
    ]
    # Time Series Plot
    plt.figure(figsize=(14, 6))
    for config in configs:
        result = calc_time_series_single_question(us_csv, config[0], [0, 1], reverse=False)
        plot_time_series(result, label=config[1])
    plt.savefig("figs/series/neighbours_series.pdf")
    plt.clf()
    # Bar Plot
    for config in configs:
        result = calc_time_series_single_question(us_csv, config[0], [0, 1], reverse=False)
        plot_bar_time_series(result, [0, 1], title=config[1])
        plt.savefig(
            "figs/bar/{}_bar.pdf".format(config[1].replace(":", "").replace(" ", "_").replace("/", "_").lower()))
        plt.clf()

    # [Confidence]
    """
    I am going to name a number of organizations. 
    For each one, could you tell me how much confidence you have in them: 
    is it a great deal of confidence, quite a lot of confidence, 
    not very much confidence or none at all?
    """
    configs = [
        ["E069_01", "Confidence: Churches"],
        ["E069_02", "Confidence: Armed Forces"],
        ["E069_04", "Confidence: The Press"],
        ["E069_05", "Confidence: Labour Unions"],
        ["E069_06", "Confidence: The Police"],
        ["E069_07", "Confidence: Parliament"],
        ["E069_08", "Confidence: The Civil Services"],
        ["E069_10", "Confidence: Television"],
        ["E069_11", "Confidence: The Government"],
        ["E069_12", "Confidence: The Political Parties"],
        ["E069_13", "Confidence: Major Companies"],
        ["E069_14", "Confidence: The Environmental Protection Movement"],
        ["E069_15", "Confidence: The Women´s Movement"],
        ["E069_17", "Confidence: Justice System/Courts"],
        ["E069_18", "Confidence: The European Union"],
        ["E069_20", "Confidence: The United Nations"],
        ["E069_21", "Confidence: The Arab League"],
        ["E069_24", "Confidence: The NAFTA"],
        ["E069_29", "Confidence: The APEC"]
    ]
    # Time Series Plot
    plt.figure(figsize=(14, 6))
    for config in configs:
        result = calc_time_series_single_question(us_csv, config[0], [1, 2, 3, 4], reverse=True)
        plot_time_series(result, label=config[1])
    plt.savefig("figs/series/confidence_series.pdf")
    plt.clf()
    # Bar Plot
    for config in configs:
        result = calc_time_series_single_question(us_csv, config[0], [1, 2, 3, 4], reverse=True)
        plot_bar_time_series(result, [1, 2, 3, 4], title=config[1])
        plt.savefig("figs/bar/{}_bar.pdf".format(config[1].replace(":", "").replace(" ", "_").replace("/", "_").lower()))
        plt.clf()

        # [Importance in Life]
        """
        For each of the following aspects, indicate how important it is in your life. 
        Would you say it is very important, rather important, 
        not very important or not important at all
        """
        configs = [
            ["A001", "Important in life: Family"],
            ["A002", "Important in life: Friends"],
            ["A003", "Important in life: Leisure time"],
            ["A004", "Important in life: Politics"],
            ["A005", "Important in life: Work"],
            ["A006", "Important in life: Religion"]
        ]
        # Time Series Plot
        plt.figure(figsize=(14, 6))
        for config in configs:
            result = calc_time_series_single_question(us_csv, config[0], [1, 2, 3, 4], reverse=True)
            plot_time_series(result, label=config[1])
        plt.savefig("figs/series/importance_series.pdf")
        plt.clf()
        # Bar Plot
        for config in configs:
            result = calc_time_series_single_question(us_csv, config[0], [1, 2, 3, 4], reverse=True)
            plot_bar_time_series(result, [1, 2, 3, 4], title=config[1])
            plt.savefig(
                "figs/bar/{}_bar.pdf".format(config[1].replace(":", "").replace(" ", "_").replace("/", "_").lower()))
            plt.clf()