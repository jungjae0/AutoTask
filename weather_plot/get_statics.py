import pandas as pd
import os


def main():
    data_dir = "../data"
    files = os.listdir(data_dir)

    for file in files:
        file_path = os.path.join(data_dir, file)
        df = pd.read_csv(file_path)
        df = df.drop(columns=['Unnamed: 0', "Y", "M"])
        target = file.split('_')[0]

        if 'paddy' in file:
            dir = f"../results/paddy/paddy_{target}"
        else:
            dir = f"../results/field/field_{target}"

        os.makedirs(dir, exist_ok=True)
        save_path = os.path.join(dir, f"{target}_summary_statistics.csv")



        summary_statistics = df.describe()
        summary_statistics = summary_statistics.reset_index()
        summary_statistics = summary_statistics.rename(columns={"index": "column"})
        summary_statistics.to_csv(save_path, index=False)


        # data_quality_summary = {
        #     "Total Rows": df.shape[0],
        #     "Total Columns": df.shape[1],
        #     "Missing Values": missing_values,
        #     "Missing Values Ratio": missing_ratio
        # }
        #
        # print("데이터 품질 요약:")
        # for key, value in data_quality_summary.items():
        #     print(f"{key}: {value}")



if __name__ == '__main__':
    main()