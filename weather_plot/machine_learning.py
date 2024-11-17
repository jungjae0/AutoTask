import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import matplotlib.cm as cm
from matplotlib import font_manager, rc
from scipy.stats import gaussian_kde
from scipy.interpolate import interpn
from scipy.stats import linregress
from matplotlib.colors import LinearSegmentedColormap
import mpl_scatter_density # adds projection='scatter_density'

font_path = "C:/Windows/Fonts/NGULIM.TTF"
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

from xgboost import XGBRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV, KFold
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from datashader.mpl_ext import dsshow
import datashader as ds


def using_datashader(ax, x, y, xlabel, ylabel, title, plot_width=50, plot_height=50):
    x = np.array([max(val, 0) for val in x])
    y = np.array([max(val, 0) for val in y])

    data , x_e, y_e = np.histogram2d( x, y, bins = [30,30], density = True )
    z = interpn( ( 0.5*(x_e[1:] + x_e[:-1]) , 0.5*(y_e[1:]+y_e[:-1]) ) , data , np.vstack([x,y]).T , method = "splinef2d", bounds_error = False)

    z[np.where(np.isnan(z))] = 0.0


    idx = z.argsort().astype(int)

    x, y, z = x[idx], y[idx], z[idx]

    ax.scatter( x, y, c=z, alpha=0.05)

    ax.grid(True)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    xy_max = max(x_max, y_max)
    xy_min = min(x_min, y_min)

    ax.plot([xy_min, xy_max], [xy_min, xy_max], color="green", linestyle="-", linewidth=2, label="1:1 Line")


    slope, intercept, _, _, _ = linregress(x, y)
    x_vals = np.array(ax.get_xlim())
    y_vals = intercept + slope * x_vals
    ax.plot(x_vals, y_vals, color="red", linestyle="--", linewidth=2, label="Regression Line")

    ax.set_xlim(xy_min, xy_max)
    ax.set_ylim(xy_min, xy_max)

    ax.legend()

    return ax

def initialize_model(model_name):
    if model_name == "xgb":
        model = XGBRegressor(max_depth=3, n_estimators=50, learning_rate=0.1, random_state=42)
    else:
        model = RandomForestRegressor(n_estimators=100, random_state=42)
    return model


def predict_target(df, x_cols, y_col, model_name, index, scatter_save_folder, featuer_save_folder):
    X = df[x_cols]
    y = df[y_col]
    scatter_fig_path = os.path.join(scatter_save_folder, f"{y_col}_{model_name}_scatter.png")
    feature_fig_path = os.path.join(featuer_save_folder, f"{y_col}_{model_name}_feature.png")


    if "TN" in y_col:
        xlabel, ylabel = "TN(kg/ha)", "TN(kg/ha)"
    elif "TP" in y_col:
        xlabel, ylabel = "TP(kg/ha)", "TP(kg/ha)"
    elif "MUSL" in y_col:
        xlabel, ylabel = "MUSL(ton/ha)", "MUSL(ton/ha)"
    else:
        xlabel, ylabel = "MUST(ton/ha)", "MUST(ton/ha)"

    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.7, random_state=42)

    model = initialize_model(model_name)

    model.fit(X_train, y_train)
    y_predict = model.predict(X_test)

    #----- 모델 결과 txt
    mae = mean_absolute_error(y_test, y_predict)
    mse = mean_squared_error(y_test, y_predict)
    rmse = np.sqrt(mse)
    r2score = r2_score(y_test, y_predict)

    print('MAE: {:.2f}'.format(mae))
    print('R2score: {:.2f}'.format(r2score))
    print('RMSE: {:.2f}'.format(rmse))

    # ----- 모델 결과 fig
    plt.clf()

    fig, (ax_train, ax_test) = plt.subplots(1, 2, figsize=(11, 6))

    using_datashader(ax_train, y_train, model.predict(X_train), xlabel, ylabel, "Train Data")
    using_datashader(ax_test, y_test, y_predict, xlabel, ylabel, "Test Data")

    plt.suptitle(f"{index} - {y_col}: {model_name.upper()}\n RMSE: {rmse:.3f} | R2: {r2score:.3f}", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    plt.savefig(scatter_fig_path)
    plt.close()

    print("Save:", scatter_fig_path)

    # ----- 피쳐 중요도 fig
    plt.clf()
    feature_importance = model.feature_importances_
    feature_importance_df = pd.DataFrame({'Feature': X.columns, 'Importance': feature_importance})
    feature_importance_df.sort_values(by=['Importance'], ascending=False, inplace=True)
    top_10_features = feature_importance_df.head(10)

    plt.figure(figsize=(10, 8))
    sns.barplot(x=top_10_features['Importance'], y=top_10_features['Feature'], palette="plasma", alpha=0.5)

    plt.title(f"{index} - {y_col}: {model_name.upper()} Top 10 Features")
    plt.xlabel('Feature Importance')
    plt.ylabel('Feature Name')
    plt.savefig(feature_fig_path)
    plt.close()
    print("Save:", feature_fig_path)


def main():
    data_dir = "../data"
    files = os.listdir(data_dir)

    models = ['xgb', 'rf']

    for file in files:
        if 'paddy' in file:
            index = 'paddy'
        else:
            index = 'field'
        y_col = file.split('_')[0]
        del_x_cols = ['Unnamed: 0', 'Y', y_col]
        df = pd.read_csv(os.path.join(data_dir, file))
        x_cols = list(df.columns)
        x_cols = [item for item in x_cols if item not in del_x_cols]
        for model_name in models:
            scatter_save_folder = f"../results/new2_{index}/{index}_{y_col}"
            os.makedirs(scatter_save_folder, exist_ok=True)

            feature_save_folder = f"../results/new2_{index}/{index}_{y_col}"
            os.makedirs(feature_save_folder, exist_ok=True)

            predict_target(df, x_cols, y_col, model_name, index, scatter_save_folder, feature_save_folder)





if __name__ == '__main__':
    main()