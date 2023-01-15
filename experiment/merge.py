import pandas as pd

# Merge a list of dataframes with different PICKAXES into one dataframe with a pickaxe column
from experiment.read import read_csv
from experiment.test import EXPERIMENT_PATH
from items import items
from utils.file import get_project_root

files = {
    items.DIAMOND_PICKAXE: "output_g10spmdw_1.csv",
    items.IRON_PICKAXE: "output_g10spmdw_2.csv",
    items.STONE_PICKAXE: "output_g10spmdw_3.csv",
    items.WOODEN_PICKAXE: "output_g10spmdw_4.csv",
    None: "output_g10spmdw_5.csv"
}

dfs = pd.DataFrame()

for pickaxe, file in files.items():
    df = read_csv(file)
    df["pickaxe"] = pickaxe if pickaxe else "None"
    dfs = dfs.append(df)

dfs.to_csv(get_project_root() / EXPERIMENT_PATH / "output_g10spmdw_wide.csv", index=True)

