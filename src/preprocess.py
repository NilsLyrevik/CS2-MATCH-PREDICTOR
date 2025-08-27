import pandas as pd
import json
import os

def load_matches(json_file="data/raw/matches.json"):
    with open(json_file, "r", encoding="utf-8") as f:
        matches = json.load(f)
    df = pd.DataFrame(matches)
    return df

def encode_teams(df):
    teams = pd.unique(df[["team1", "team2"]].values.ravel())
    team2id = {team: idx for idx, team in enumerate(teams)}
    df["team1_id"] = df["team1"].map(team2id)
    df["team2_id"] = df["team2"].map(team2id)
    return df, team2id

def encode_maps(df):
    maps = df["map"].unique()
    map2id = {m: i for i, m in enumerate(maps)}
    df["map_id"] = df["map"].map(map2id)
    return df, map2id

def create_target(df):
    df["target"] = (df["team1_score"] > df["team2_score"]).astype(int)
    return df

def add_score_diff(df):
    df["score_diff"] = df["team1_score"] - df["team2_score"]
    return df

def save_processed(df, path="data/processed/matches.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved processed data to {path}")

if __name__ == "__main__":
    df = load_matches("data/raw/matches.json")
    df, team2id = encode_teams(df)
    df, map2id = encode_maps(df)
    df = create_target(df)
    df = add_score_diff(df)
    save_processed(df)
