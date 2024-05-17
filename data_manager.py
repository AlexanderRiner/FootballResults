import pandas as pd
import os
import json
from settings_manager import settings_manager
from fpdf import FPDF as fpdf
import matplotlib.pyplot as plt
from io import BytesIO

class data_manager:
    @staticmethod
    def get_data_as_df(year: int):
        df = pd.read_csv(f"data/{year-1}{year}.csv")
        return df

    @staticmethod
    def get_all_data():
        s = settings_manager()
        current_league = s.user_league
        directory = os.fsencode(f"data/{current_league}")

        list_of_df = []

        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if not filename.endswith(".csv"):
                print("ERROR Filename CSV")
                continue
            try:
                df = pd.read_csv(f"data/{current_league}/{filename}")
                #rename columns
                rename_dict = {
                    "HomeTeam" : "Home Team",
                    "AwayTeam" : "Away Team",
                    "Date" : "Match Date",
                    "Div" : "League Division",
                    "Time" : "Time of kick off",
                    "FTHG" : "Full Time Home Team Goals",
                    "HG" : "Full Time Home Team Goals",
                    "FTAG" : "Full Time Away Team Goals",
                    "AG" : "Full Time Away Team Goals",
                    "FTR" : "Full Time Result (H= Home Win, D=Draw, A=Away Win)",
                    "Res" : "Full Time Result (H= Home Win, D=Draw, A=Away Win)",
                    "HTHG" : "Half Time Home Team Goals",
                    "HTAG" : "Half Time Home Team Goals",
                    "HTR" : "Half Time Result(H= Home Win, D=Draw, A=Away Win)",
                    "Referee" : "Match Referee",
                    "HS" : "Home Team Shots",
                    "AS" : "Away Team Shots",
                    "HST" : "Home Team Shots on Target",
                    "AST" : "Away Team Shots on Target",
                    "HF" : "Home Team Fouls Committed",
                    "AF" : "Away Team Fouls Committed",
                    "HC" : "Home Team Corners",
                    "AC" : "Away Team Corners",
                    "HY" : "Home Team Yellow Cards",
                    "AY" : "Away Team Yellow Cards",
                    "HR" : "Home Team Red Cards",
                    "AR" : "Away Team Red Cards",
                }
                df.rename(columns=rename_dict, inplace=True)
                
            except Exception as e:
                print(f"Error with file {filename}: {e}")
            list_of_df.append(df)
        combined_df = pd.concat(list_of_df)

        def custom_date_parser(date_str):
            try:
                # Try parsing date with four-digit year
                return pd.to_datetime(date_str, format='%d/%m/%Y')
            except ValueError:
                # If parsing fails, try parsing with two-digit year
                return pd.to_datetime(date_str, format='%d/%m/%y')

        combined_df['Date'] = combined_df['Date'].apply(custom_date_parser)

        filtered_df = combined_df[(combined_df['Date'].dt.year >= s.user_start_year) & (combined_df['Date'].dt.year <= s.user_end_year)]

        return filtered_df

    @staticmethod
    def get_all_teams():
        try:
            df = data_manager.get_all_data()
            unique_values_list = list(set(df['HomeTeam'].unique()).union(df['AwayTeam'].unique()))
            unique_values_list = list(filter(lambda x: not pd.isna(x), unique_values_list))

            return unique_values_list
        except Exception as e:
            print(f"Teams Error: {e}")

    def analyse_data(self, team1, team2):
        pdf = fpdf('P', 'mm', 'A4') # A4 (210 by 297 mm)

        PHEIGHT = 297
        PWIDTH = 210
        margin_side = 7

        pdf.add_page()
        pdf.set_margins(margin_side, 0, margin_side)

        pdf.set_font('Arial', 'B', 14)

        df = data_manager.get_all_data()

        columns_to_keep = ['HomeTeam', 'Date', 'FTHG', 'HTHG', 'HST', 'HS', 'HF', 'HC']
        try:
            team1_home_df = df[df['HomeTeam'] == team1]
            team1_home_df = team1_home_df.loc[:, columns_to_keep]
            team1h_df = team1_home_df.groupby(team1_home_df['Date'].dt.year).agg({'FTHG': 'sum', 'HTHG': 'sum', 'HST': 'sum', 'HS': 'sum', 'HF': 'sum', 'HC': 'sum'})

            columns_to_keep = ['HomeTeam', 'Date', 'FTAG', 'HTAG', 'AST', 'AS', 'AF', 'AC']
            team1_away_df = df[df['AwayTeam'] == team1]
            team1_away_df = team1_away_df.loc[:, columns_to_keep]
            team1a_df = team1_away_df.groupby(team1_away_df['Date'].dt.year).agg(
                {'FTAG': 'sum', 'HTAG': 'sum', 'AST': 'sum', 'AS': 'sum', 'AF': 'sum', 'AC': 'sum'})

            ## TODO DAS BENUTZEN
            print(team1a_df.head())
        except Exception as e:
            print(e)


        total_games_home = df.groupby([df['Date'].dt.year, 'HomeTeam']).size().reset_index(name='Count')
        team1_home = total_games_home[total_games_home['HomeTeam'] == team1]
        team2_home = total_games_home[total_games_home['HomeTeam'] == team2]

        total_games_away = df.groupby([df['Date'].dt.year, 'AwayTeam']).size().reset_index(name='Count')
        team1_away = total_games_away[total_games_away['AwayTeam'] == team1]
        team2_away = total_games_away[total_games_away['AwayTeam'] == team2]

        self.create_bar(team1_home['Count'], team2_home['Count'], team1_home['Date'],
                        team2_home['Date'], team1, team2, 1,  "Home Matches per Year")
        self.create_bar(team1_away['Count'], team2_away['Count'], team1_away['Date'],
                        team2_away['Date'], team1, team2, 2,  "Away Matches per Year")

        team1_home_df = df[df['HomeTeam'] == team1]
        team2_home_df = df[df['HomeTeam'] == team2]
        # Group by year and aggregate points using sum
        team1_home_by_year = team1_home_df.groupby(team1_home_df['Date'].dt.year)['FTHG'].sum()
        team2_home_by_year = team2_home_df.groupby(team2_home_df['Date'].dt.year)['FTHG'].sum()
        self.create_bar(team1_home_by_year.values, team2_home_by_year.values, team1_home_by_year.index, team2_home_by_year.index, team1, team2, 3,  "Away Goals per Year")

        team1_home_df = df[df['AwayTeam'] == team1]
        team2_home_df = df[df['AwayTeam'] == team2]
        # Group by year and aggregate points using sum
        team1_home_by_year = team1_home_df.groupby(team1_home_df['Date'].dt.year)['FTAG'].sum()
        team2_home_by_year = team2_home_df.groupby(team2_home_df['Date'].dt.year)['FTAG'].sum()
        self.create_bar(team1_home_by_year.values, team2_home_by_year.values, team1_home_by_year.index, team2_home_by_year.index, team1, team2, 4, "Home Goals per Year")
        self.create_bar(team1_home_by_year.values, team2_home_by_year.values, team1_home_by_year.index, team2_home_by_year.index, team1, team2, 5, "Away Goals per Year")
        self.create_bar(team1_home_by_year.values, team2_home_by_year.values, team1_home_by_year.index, team2_home_by_year.index, team1, team2, 6, "Away Goals per Year")
        self.create_bar(team1_home_by_year.values, team2_home_by_year.values, team1_home_by_year.index, team2_home_by_year.index, team1, team2, 7, "Away Goals per Year")
        self.create_bar(team1_home_by_year.values, team2_home_by_year.values, team1_home_by_year.index, team2_home_by_year.index, team1, team2, 8, "Away Goals per Year")

        ## Shots on Target
        ## Corner, Fouls, Free kicks
        ## Rote und Gelbe Karte

        title_x = pdf.l_margin
        # Set the position
        pdf.set_x(title_x)

        pdf.cell(w=40, h=10, txt=f"{team1} vs {team2} Performance Report ({settings_manager().user_start_year}-{settings_manager().user_end_year})", border=0, ln=1, align='', fill=False, link='')
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(w=PWIDTH-2*margin_side, h=5, txt=f"Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.",
                 border=0, align='J', fill=False)

        top_margin = 60
        height = 57

        for i in range(1, 9):
            try:
                pdf.image(f'tmp/plot{i}.png', x=(0 if i % 2 != 0 else 1)*96+7, y=top_margin+((i-1)//2)*height, w=100)
            except Exception as e:
                print(f"Error with image generation: {e}")

        file_name = f'exports/{team1}_vs_{team2}.pdf'
        pdf.output(file_name, 'F')
        return file_name

    def create_bar(self, x1: list, x2: list, y1: list, y2: list, x1_name: str, x2_name: str, plot_number: int, title: str):
        plt.figure(figsize=(10, 6))
        # Width of a bar
        width = 0.4

        plt.bar(y1 - (width / 2), x1, width=width, color='skyblue',
                label=x1_name)
        plt.bar(y2 + (width / 2), x2, width=width, color='purple',
                label=x2_name)
        plt.legend(loc="best")
        plt.title(title)
        plt.xticks(y1)
        plt.grid(axis='y', alpha=0.7)

        plt.savefig(f'tmp/plot{plot_number}.png')

