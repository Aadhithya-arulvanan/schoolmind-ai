import pandas as pd


def extract_name(question):

    q = question.lower()

    marks_df = pd.read_csv(
        "data/marks.csv"
    )

    names = marks_df["Name"].tolist()

    for name in names:

        if name.lower() in q:

            return name

    return None