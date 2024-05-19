import os

import pandas as pd

from misc import *
from settings import *


def get_all_data() -> pd.DataFrame:
    """
    Retrieves and combines data from CSV files within the specified directory.

    This function reads all CSV files within the directory corresponding to the user's selected league,
    combines them into a single DataFrame, parses the 'Date' column using a custom date parser,
    and filters the DataFrame based on the user's specified starting and ending years.

    Returns:
        pd.DataFrame: Combined and filtered DataFrame containing football data.
    """
    # Directory where CSV files are stored
    directory = os.fsencode(f"data/{SettingsManager.user_settings.league.name}")

    list_of_df = []  # List to store individual DataFrames from CSV files

    # Iterate through each file in the directory
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if not filename.endswith(".csv"):
            print("ERROR: Filename is not a CSV file")
            continue
        try:
            # Read CSV file and append DataFrame to list
            df = pd.read_csv(f"data/{SettingsManager.user_settings.league.name}/{filename}")
            list_of_df.append(df)
        except Exception as e:
            print(f"Error with file {filename}: {e}")

    # Combine individual DataFrames into a single DataFrame
    combined_df = pd.concat(list_of_df)

    # Custom date parser function to handle different date formats
    def custom_date_parser(date_str):
        try:
            # Try parsing date with four-digit year
            return pd.to_datetime(date_str, format='%d/%m/%Y')
        except ValueError:
            # If parsing fails, try parsing with two-digit year
            return pd.to_datetime(date_str, format='%d/%m/%y')

    # Apply custom date parser to 'Date' column
    combined_df['Date'] = combined_df['Date'].apply(custom_date_parser)

    # Filter DataFrame based on user's specified starting and ending years
    filtered_df = combined_df[
        (combined_df['Date'].dt.year >= SettingsManager.user_settings.starting_year) &
        (combined_df['Date'].dt.year <= SettingsManager.user_settings.ending_year)
        ]

    return filtered_df


def get_all_teams() -> list[str]:
    """
    Retrieves a list of all unique team names from the football data.

    This function fetches all football data, extracts unique team names from both the 'HomeTeam'
    and 'AwayTeam' columns, removes any NaN values, and returns the list of unique team names.

    Returns:
        list[str]: List of unique team names.
    """
    # Get all football data
    df = get_all_data()

    # Extract unique team names from 'HomeTeam' and 'AwayTeam' columns
    unique_home_teams = df['HomeTeam'].unique()
    unique_away_teams = df['AwayTeam'].unique()

    # Combine unique team names and remove NaN values
    unique_values_list = list(set(unique_home_teams).union(unique_away_teams))
    team_names = [team_name for team_name in unique_values_list if not pd.isna(team_name)]

    return team_names


def get_data_with_columns(teams: [str]) -> pd.DataFrame:
    """
    Retrieves football data with specified columns for the given teams.

    This function fetches football data, selects specified columns for each team,
    aggregates the data based on year and team, and returns a DataFrame containing
    the aggregated data.

    Args:
        teams (list[str]): List of team names.

    Returns:
        pd.DataFrame: DataFrame containing aggregated football data.
    """
    try:
        # Get all football data
        df = get_all_data()

        # Define columns to keep for each team type (home and away)
        data_to_keep = {
            "HomeTeam": ['FTHG', 'HTHG', 'HST', 'HS', 'HF', 'HC', 'HY', 'HR', 'FTR'],
            "AwayTeam": ['FTAG', 'HTAG', 'AST', 'AS', 'AF', 'AC', 'AY', 'AR' 'FTR']
        }

        # Define new column names
        new_names = ['Full Time Goals', 'Half Time Goals', 'Shots on Target', 'Shots',
                     'Fouls Committed', 'Corners', 'Yellow Cards', 'Red Cards', 'Result']

        # List to store DataFrames for each team
        team_dfs = []

        for team in teams:
            # List to store DataFrames for home and away data
            list_of_dfs = []

            # Iterate over home and away team types
            for team_type, columns in data_to_keep.items():
                # Select columns to keep and aggregate by sum
                columns_to_keep = {element: "sum" for element in columns}

                # Filter data for the current team
                new_df = df[df[team_type].str.lower() == team.lower()]

                # Select required columns and rename team column
                new_df = new_df.loc[:, columns + ['Date', team_type]]
                new_df = new_df.rename(columns={team_type: 'Team'})

                # Aggregate data by year and team
                new_df = new_df.groupby([new_df['Date'].dt.year, "Team"]).agg(columns_to_keep)
                list_of_dfs.append(new_df)

            # Combine home and away data into a single DataFrame
            combined_data = {}
            for home_column, away_column, new_name in zip(data_to_keep["HomeTeam"], data_to_keep["AwayTeam"],
                                                          new_names):
                combined_data[f"{new_name}"] = list_of_dfs[0][home_column] + list_of_dfs[1][away_column]

            team_dfs.append(pd.DataFrame(combined_data))

        # Concatenate DataFrames for all teams
        return pd.concat(team_dfs)

    except FileNotFoundError as e:
        print(f"{RED}File not found error: {e}{END}")
        print(f"{RED}Try running the update_data function and trying again.{END}")

    except PermissionError as e:
        print(f"{RED}Permission error: {e}{END}")
        print(f"{RED}Try running the update_data function and trying again.{END}")

    except pd.errors.ParserError as e:
        print(f"{RED}Parser error: {e}{END}")
        print(f"{RED}Try running the update_data function and trying again.{END}")

    except (KeyError, ValueError) as e:
        print(f"{RED}Data processing error: {e}{END}")
        print(f"{RED}Try running the update_data function and trying again.{END}")
