import pandas as pd
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import GridSearchCV
from surprise import KNNWithMeans, KNNBasic, KNNWithZScore, SlopeOne


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


def tune_KNNWithMeans(diff_data, wl_data, output_file):
    sim_options = {
        "name": ["msd", "cosine"],
        "user_based": [False, True],
        "min support": [1, 2, 3, 4, 5],  # min number of common items between user for similarity not to be 0
    }
    param_grid = {"sim_options": sim_options,
                  "min_k": [1, 2, 3, 4, 5]  # minimum neighbors to calculate
                  }

    gs = GridSearchCV(KNNWithMeans, param_grid, measures=["mae"], cv=3)

    output_file.write("-------------------------------------------------\n")
    output_file.write("KNNWithMeans:\n")
    output_file.write("-------------------------------------------------\n")
    output_file.write("difficulty:\n")
    gs.fit(diff_data)
    output_file.write("best score: ")
    output_file.write(str(gs.best_score["mae"]) + "\n")
    output_file.write("best params: ")
    output_file.write(str(gs.best_params["mae"]) + "\n")

    output_file.write("\nworkload:\n")
    gs.fit(wl_data)
    output_file.write("best score: ")
    output_file.write(str(gs.best_score["mae"]) + "\n")
    output_file.write("best params: ")
    output_file.write(str(gs.best_params["mae"]) + "\n")
    output_file.write("-------------------------------------------------\n\n")


def tune_KNNBasic(diff_data, wl_data, output_file):
    sim_options = {
        "name": ["msd", "cosine"],
        "user_based": [False, True],
        "min support": [1, 2, 3, 4, 5],  # min number of common items between user for similarity not to be 0
    }
    param_grid = {"sim_options": sim_options,
                  "min_k": [1, 2, 3, 4, 5]  # minimum neighbors to calculate
                  }

    gs = GridSearchCV(KNNBasic, param_grid, measures=["mae"], cv=3)

    output_file.write("-------------------------------------------------\n")
    output_file.write("KNNWithZScore:\n")
    output_file.write("-------------------------------------------------\n")
    output_file.write("difficulty:\n")
    gs.fit(diff_data)
    output_file.write("best score: ")
    output_file.write(str(gs.best_score["mae"]) + "\n")
    output_file.write("best params: ")
    output_file.write(str(gs.best_params["mae"]) + "\n")

    output_file.write("\nworkload:\n")
    gs.fit(wl_data)
    output_file.write("best score: ")
    output_file.write(str(gs.best_score["mae"]) + "\n")
    output_file.write("best params: ")
    output_file.write(str(gs.best_params["mae"]) + "\n")
    output_file.write("-------------------------------------------------\n\n")


def tune_KNNWithZScore(diff_data, wl_data, output_file):
    sim_options = {
        "name": ["msd", "cosine"],
        "user_based": [False, True],
        "min support": [1, 2, 3, 4, 5],  # min number of common items between user for similarity not to be 0
    }
    param_grid = {"sim_options": sim_options,
                  "min_k": [1, 2, 3, 4, 5]  # minimum neighbors to calculate
                  }

    gs = GridSearchCV(KNNWithZScore, param_grid, measures=["mae"], cv=3)

    output_file.write("-------------------------------------------------\n")
    output_file.write("KNNBasic:\n")
    output_file.write("-------------------------------------------------\n")
    output_file.write("difficulty:\n")
    gs.fit(diff_data)
    output_file.write("best score: ")
    output_file.write(str(gs.best_score["mae"]) + "\n")
    output_file.write("best params: ")
    output_file.write(str(gs.best_params["mae"]) + "\n")

    output_file.write("\nworkload:\n")
    gs.fit(wl_data)
    output_file.write("best score: ")
    output_file.write(str(gs.best_score["mae"]) + "\n")
    output_file.write("best params: ")
    output_file.write(str(gs.best_params["mae"]) + "\n")
    output_file.write("-------------------------------------------------\n\n")


def tune_SlopeOne(diff_data, wl_data, output_file):
    param_grid = {}

    gs = GridSearchCV(SlopeOne, param_grid, measures=["mae"], cv=3)

    output_file.write("-------------------------------------------------\n")
    output_file.write("SlopeOne:\n")
    output_file.write("-------------------------------------------------\n")
    output_file.write("difficulty:\n")
    gs.fit(diff_data)
    output_file.write("best score: ")
    output_file.write(str(gs.best_score["mae"]) + "\n")
    output_file.write("best params: ")
    output_file.write(str(gs.best_params["mae"]) + "\n")

    output_file.write("\nworkload:\n")
    gs.fit(wl_data)
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
    tune_KNNWithMeans(diff_data, wl_data, output_file)
    tune_KNNWithZScore(diff_data, wl_data, output_file)
    tune_SlopeOne(diff_data, wl_data, output_file)

    output_file.close()


def main():
    ratings_df = pd.read_csv("offline_dev/ratings.csv",
                             index_col="id")

    print_stats(ratings_df) # not to file

    tune_params(ratings_df)


if __name__ == "__main__":
    main()
