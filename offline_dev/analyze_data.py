import pandas as pd
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import GridSearchCV
from surprise import KNNWithMeans


NORMALIZE = True


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


def train_model(ratings_df):
    reader = Reader(rating_scale=(1, 10))

    difficulty_df = ratings_df[['user', 'course', 'difficulty']]

    data = Dataset.load_from_df(difficulty_df,
                                reader)

    sim_options = {
        "name": ["msd", "cosine"],
        "user_based": [False, True],
        "min support": [1, 2, 3, 4, 5],
    }

    param_grid = {"sim_options": sim_options}

    gs = GridSearchCV(KNNWithMeans, param_grid, measures=["rmse", "mae"], cv=3)
    gs.fit(data)
    print("---best mae score: ", gs.best_score["mae"])
    print("---best mae params: ", gs.best_params["mae"])
    print("---best mae index: ", gs.best_index["mae"])
    print("--------------------------------------------")
    print("---best rmse score: ", gs.best_score["rmse"])
    print("---best rmse params: ", gs.best_params["rmse"])
    print("---best rmse index: ", gs.best_index["rmse"])

def main():
    ratings_df = pd.read_csv("offline_dev/ratings.csv",
                             index_col="id")

    print_stats(ratings_df)

    train_model(ratings_df)


if __name__ == "__main__":
    main()
