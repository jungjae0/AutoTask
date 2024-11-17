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
        "Rainfall Days":["r20", "r30", "r50", "r80", "PRCP"],
        "Total Rainfall": ["r20_sum", "r30_sum", "r50_sum", "r80_sum", "PRCP"]
    }


    for key, values in combine_info.items():
        df = data[values]
        g = sns.PairGrid(df, vars=values)
        g.map_upper(upper_r2)
        g.map_lower(lower_scatter_with_reg)
        g.map_diag(sns.histplot, kde=True, color="gold", bins=10)
        r2_save_path = os.path.join(save_folder, f"pair_r2_{key}.png")
        plt.savefig(r2_save_path)
        print("Save:", r2_save_path)


    for key, values in combine_info.items():
        df = data[values]
        g = sns.PairGrid(df)
        g.map_upper(corrfunc)
        g.map_lower(lower_scatter_with_reg2)
        g.map_diag(sns.histplot, kde=True, color="gold", bins=10)

        r_save_path = os.path.join(save_folder, f"pair_r_{key}.png")
        plt.savefig(r_save_path)

        print("Save:", r_save_path)


def target_scatter(data, target, save_folder):
    combine_info = {
        "Climate": ["TMX", "TMN", "SRAD", "WSPD", "RHUM", "PRCP"],
        "Rainfall Days":["r20", "r30", "r50", "r80"],
        "Total Rainfall": ["r20_sum", "r30_sum", "r50_sum", "r80_sum"]
    }

    for key, x_columns in combine_info.items():
        n_cols = len(x_columns)
        n_rows = 2
        plt.figure(figsize=(n_cols * 4, 4))
        for i, x_column in enumerate(x_columns):
            x = data[[x_column]].values
            y = data[target].values

            # 회귀 모델 생성
            model = LinearRegression()
            model.fit(x, y)
            y_pred = model.predict(x)

            # R^2 계산
            r2 = r2_score(y, y_pred)

            # 서브플롯 설정 (1행 n_cols 열)
            ax = plt.subplot(n_rows, n_cols // n_rows, i + 1)
            ax.scatter(x, y, color='blue', label='Data points')
            ax.plot(x, y_pred, color='red', linewidth=2, label='Regression line')
            ax.set_title(f'Regression of {target} on {x_column}')
            ax.set_xlabel(x_column)
            ax.set_ylabel(target)
            ax.legend()
            ax.grid()
            ax.text(0.05, 0.95, f'$R^2={r2:.2f}$', transform=ax.transAxes, fontsize=12, verticalalignment='top')

            # 정사각형 유지
            ax.set_aspect('equal', adjustable='box')

        plt.tight_layout()
        # save_path = os.path.join(save_folder, f"target_scatter_{key}.png")
        # plt.savefig(save_path)

        plt.show()


def main():
    # climate 간의 pair
    data_dir = "../data"
    files = os.listdir(data_dir)
    files = []

    for file in files:
        file_path = os.path.join(data_dir, file)
        target = file.split("_")[0]
        df = pd.read_csv(file_path)
        if 'paddy' in file:
            save_folder = f"../results/new_paddy/paddy_{target}"

        else:
            save_folder = f"../results/new_field/field_{target}"

        os.makedirs(save_folder, exist_ok=True)

        pair_plot(df, save_folder)
        # target_scatter(df, target, save_folder)



if __name__ == '__main__':
    main()