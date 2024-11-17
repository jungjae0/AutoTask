import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.backends.backend_svg import svgProlog
from scipy.stats import pearsonr, linregress


def box_plot(data, columns_info, save_folder):

    for y, texts in columns_info.items():

        plt.figure(figsize=(10, 6))
        # sns.boxplot(x='M', y=y, data=data, palette="tab20", dodge=False, legend=False)
        sns.boxplot(x='M', y=y, hue='M', data=data, palette="tab20", dodge=False, legend=False)

        plt.title(texts[0])
        plt.xlabel(texts[1])
        plt.ylabel(texts[2])

        plt.savefig(os.path.join(save_folder, rf"{y}.png"))


def main():
    data_dir = "../data"
    # climate는 paddy와 field에 따라 다르기 때문에 2개만 나눠서 그림.

    files = ["TN_slope_sensitivity.csv", "TN_paddy_input_output.csv"]

    common_columns_info = {
        "TMX": ["Monthly Distribution of Max Temperature (TMX)", "Month", "Max Temperature (°C)"],
        "TMN": ["Monthly Distribution of Min Temperature (TMN)", "Month", "Min Temperature (°C)"],
        "SRAD": ["Monthly Distribution of Solar Radiation (SRAD)", "Month", "Solar Radiation (MJ/m²)"],
        "WSPD": ["Monthly Distribution of Wind Speed (WSPD)", "Month", "Wind Speed (m/s)"],
        "RHUM": ["Monthly Distribution of Relative Humidity (RHUM)", "Month", "Relative Humidity (%)"],
        "PRCP": ["Monthly Distribution of Precipitation (PRCP)", "Month", "Precipitation (mm)"],
        "r20": ["Monthly Days with 20mm+ Rainfall (r20)", "Month", "Days with 20mm+ Rainfall (days)"],
        "r30": ["Monthly Days with 30mm+ Rainfall (r30)", "Month", "Days with 30mm+ Rainfall (days)"],
        "r50": ["Monthly Days with 50mm+ Rainfall (r50)", "Month", "Days with 50mm+ Rainfall (days)"],
        "r80": ["Monthly Days with 80mm+ Rainfall (r80)", "Month", "Days with 80mm+ Rainfall (days)"],
        "r20_sum": ["Monthly Total Rainfall of 20mm+ Days (r20_sum)", "Month", "Total Rainfall of 20mm+ Days (mm)"],
        "r30_sum": ["Monthly Total Rainfall of 30mm+ Days (r30_sum)", "Month", "Total Rainfall of 30mm+ Days (mm)"],
        "r50_sum": ["Monthly Total Rainfall of 50mm+ Days (r50_sum)", "Month", "Total Rainfall of 50mm+ Days (mm)"],
        "r80_sum": ["Monthly Total Rainfall of 80mm+ Days (r80_sum)", "Month", "Total Rainfall of 80mm+ Days (mm)"],
        "fertN": ["Monthly Nitrogen Fertilizer Application (fertN)", "Month",
                  "Nitrogen Fertilizer Application (kg/ha)"],
    }

    paddy_columns_info = {}
    field_columns_info = {
        "Slope": ["Monthly Leaching Amount (slope)", "Month", "Leaching Amount (mm)"],
    }

    for file in files:
        if 'paddy' in file:
            save_folder = f"../results/paddy/plot_box"
            columns_info = {**common_columns_info, **paddy_columns_info}
        else:
            save_folder = f"../results/field/plot_box"
            columns_info = {**common_columns_info, **field_columns_info}

        os.makedirs(save_folder, exist_ok=True)

        os.makedirs(save_folder, exist_ok=True)
        file_path = os.path.join(data_dir, file)
        df = pd.read_csv(file_path)
        df['RHUM'] = df['RHUM'] * 100

        box_plot(df, columns_info, save_folder)



if __name__ == '__main__':
    main()