import pandas as pd
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import GridSearchCV
from surprise import KNNWithMeans, KNNBasic


PARAMS_TUNING_FILE_NAME = "offline_dev/params_tuning.txt"
#NORMALIZE = True


def print_stats(ratings_df):
    print("-----------stats-----------")
    print("---------------------------")
    print("number of ratings:", len(ratings_df))
    print("number of rated courses:", ratings_df['course'].nunique())
    print("number of raters:", ratings_df['user'].nunique())
    users = ratings_df['user'].value_counts()
    print("users with more then 8 ratings:", len(users[users >= 8]))

    print("\n10 most rated courses:")
    print(ratings_df['course'].value_counts().head(10))


def cv_KNNWithMeans(ratings_df):
    reader = Reader(rating_scale=(1, 10))

    difficulty_df = ratings_df[['user', 'course', 'difficulty']]

    data = Dataset.load_from_df(difficulty_df,
                                reader)

    sim_options = {
        "name": ["msd", "cosine"],
        "user_based": [False, True],
        "min support": [1, 2, 3, 4, 5],
    }
    param_grid = {"sim_options": sim_options, }

    gs = GridSearchCV(KNNWithMeans, param_grid, measures=["rmse", "mae"], cv=3)
    gs.fit(data)
    print("---best mae score: ", gs.best_score["mae"])
    print("---best mae params: ", gs.best_params["mae"])
    print("---best mae index: ", gs.best_index["mae"])


def tune_KNNBasic(diff_data, wl_data, output_file):
    sim_options = {
        "name": ["msd", "cosine"],
        "user_based": [False, True],
        "min support": [1, 2, 3, 4, 5],  # min number of common items between user for similarity not to be 0
        "min_k": [1, 2, 3, 4, 5]  # minimum neighbors to calculate
    }
    param_grid = {"sim_options": sim_options}

    gs = GridSearchCV(KNNBasic, param_grid, measures=["rmse", "mae"], cv=3)

    gs.fit(diff_data)

    output_file.write("-------------------------------------------------\n")

    output_file.write("KNNBasic:\n")
    output_file.write("-------------------------------------------------\n")
    output_file.write("difficulty:\n")
    output_file.write("best score: ")
    output_file.write(str(gs.best_score["mae"]) + "\n")
    output_file.write("best params: ")
    output_file.write(str(gs.best_params["mae"]) + "\n")
    output_file.write("-------------------------------------------------\n\n")


def tune_params(ratings_df):
    reader = Reader(rating_scale=(1, 10))

    difficulty_df = ratings_df.loc[:, ['user', 'course', 'difficulty']]
    workload_df = ratings_df.loc[:, ['user', 'course', 'workload']]

    diff_data = Dataset.load_from_df(difficulty_df, reader)
    wl_data = Dataset.load_from_df(workload_df, reader)

    output_file = open(PARAMS_TUNING_FILE_NAME, "w+")

    tune_KNNBasic(diff_data, wl_data, output_file)




def main():
    ratings_df = pd.read_csv("offline_dev/ratings.csv",
                             index_col="id")

    print_stats(ratings_df) # not to file

    tune_params(ratings_df)

if __name__ == "__main__":
    main()
