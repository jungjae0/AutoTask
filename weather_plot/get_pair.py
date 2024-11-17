import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import pearsonr, linregress
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


def calculate_r2(x, y):
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    return r_value ** 2


def upper_r2(x, y, **kwargs):
    r2 = calculate_r2(x, y)
    ax = plt.gca()
    ax.annotate(f'{r2:.2f}', xy=(0.5, 0.5), xycoords='axes fraction',
                ha='center', va='center', fontsize=12, color='black')


def lower_scatter_with_reg(x, y, **kwargs):
    ax = plt.gca()
    sns.regplot(x=x, y=y, ax=ax, scatter_kws={'s': 10}, line_kws={"color": "red"})


def corrfunc(x, y, **kws):
    r = np.corrcoef(x, y)[0, 1]
    plt.gca().annotate(f"{r:.2f}", xy=(0.5, 0.5), xycoords="axes fraction",
                       ha="center", va="center", fontsize=12)


def lower_scatter_with_reg2(x, y, **kwargs):
    ax = plt.gca()
    sns.regplot(x=x, y=y, ax=ax, scatter_kws={'s': 10}, line_kws={"color": "red"})


def pair_plot(data, save_folder):
    combine_info = {
        "Climate": ["TMX", "TMN", "SRAD", "WSPD", "RHUM", "PRCP"],
        "Rainfall Days": ["r20", "r30", "r50", "r80", "PRCP"],
        "Total Rainfall": ["r20_sum", "r30_sum", "r50_sum", "r80_sum", "PRCP"]
    }

    for key, values in combine_info.items():
        df = data[values]
        g = sns.PairGrid(df, vars=values)
        g.map_upper(upper_r2)
        g.map_lower(lower_scatter_with_reg)
        g.map_diag(sns.histplot, kde=True, color="gold", bins=10)
        r2_save_path = os.path.join(save_folder, f"r2_{key}.png")
        plt.savefig(r2_save_path)
        print("Save:", r2_save_path)

    for key, values in combine_info.items():
        df = data[values]
        g = sns.PairGrid(df)
        g.map_upper(corrfunc)
        g.map_lower(lower_scatter_with_reg2)
        g.map_diag(sns.histplot, kde=True, color="gold", bins=10)

        r_save_path = os.path.join(save_folder, f"r_{key}.png")
        plt.savefig(r_save_path)

        print("Save:", r_save_path)


def main():
    # climate 간의 pair
    data_dir = "../data"
    files = ["TN_paddy_input_output.csv", "TN_slope_sensitivity.csv"]

    for file in files:
        if 'paddy' in file:
            save_folder = f"../results/new_paddy/pair_plot"
        else:
            save_folder = f"../results/new_field/pair_plot"

        os.makedirs(save_folder, exist_ok=True)
        file_path = os.path.join(data_dir, file)
        df = pd.read_csv(file_path)
        pair_plot(df, save_folder)


if __name__ == '__main__':
    main()