import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import pearsonr, linregress

def yearly_plot(data, save_folder):
    columns_info = {
        "TMX": ["Yearly Trends of Max Temperature (TMX)", "Year", "Max Temperature (°C)", "red"],
        "TMN": ["Yearly Trends of Min Temperature (TMN)", "Year", "Min Temperature (°C)", "lightcoral"],
        "SRAD": ["Yearly Trends of Solar Radiation (SRAD)", "Year", "Solar Radiation (MJ/m²)", "orange"],
        "WSPD": ["Yearly Trends of Wind Speed (WSPD)", "Year", "Wind Speed (m/s)", "green"],
        "RHUM": ["Yearly Trends of Relative Humidity (RHUM)", "Year", "Relative Humidity (%)", "purple"],
        "PRCP": ["Yearly Trends of Precipitation (PRCP)", "Year", "Precipitation (mm)", "blue"],
        "r20": ["Yearly Days with 20mm+ Rainfall (r20)", "Year", "Days with 20mm+ Rainfall (days)", "skyblue"],
        "r30": ["Yearly Days with 30mm+ Rainfall (r30)", "Year", "Days with 30mm+ Rainfall (days)", "skyblue"],
        "r50": ["Yearly Days with 50mm+ Rainfall (r50)", "Year", "Days with 50mm+ Rainfall (days)", "skyblue"],
        "r80": ["Yearly Days with 80mm+ Rainfall (r80)", "Year", "Days with 80mm+ Rainfall (days)", "skyblue"],
        "r20_sum": ["Yearly Total Rainfall of 20mm+ Days (r20_sum)", "Year", "Total Rainfall of 20mm+ Days (mm)", "lightblue"],
        "r30_sum": ["Yearly Total Rainfall of 30mm+ Days (r30_sum)", "Year", "Total Rainfall of 30mm+ Days (mm)", "lightblue"],
        "r50_sum": ["Yearly Total Rainfall of 50mm+ Days (r50_sum)", "Year", "Total Rainfall of 50mm+ Days (mm)", "lightblue"],
        "r80_sum": ["Yearly Total Rainfall of 80mm+ Days (r80_sum)", "Year", "Total Rainfall of 80mm+ Days (mm)", "lightblue"],
        # "fertN": ["Annual Nitrogen Fertilizer Application (fertN)", "Year", "Nitrogen Fertilizer Application (kg/ha)", "gold"],
        # "TN": ["Annual Nitrogen Leaching (TN)", "Year", "Nitrogen Leaching (kg/ha)", "gold"]
    }

    for key, values in columns_info.items():
        title  = values[0]
        xlabel = values[1]
        ylabel = values[2]
        color = values[3]

        plt.figure(figsize=(12, 6))
        sns.lineplot(x='Y', y=key, data=data, label=ylabel, color=color)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend()

        save_path = os.path.join(save_folder, key)
        plt.savefig(save_path)
        print("Save: ", save_path)
        # plt.show()

def main():
    data_dir = "../data"
    # climate는 paddy와 field에 따라 다르기 때문에 2개만 나눠서 그림.

    files = ["TN_slope_sensitivity.csv", "TN_paddy_input_output.csv"]

    for file in files:
        if 'paddy' in file:
            save_folder = '../results/paddy/plot_line'

        else:
            save_folder = '../results/field/plot_line'

        df = pd.read_csv(os.path.join(data_dir, file))
        os.makedirs(save_folder, exist_ok=True)
        yearly_plot(df, save_folder)






if __name__ == '__main__':
    main()