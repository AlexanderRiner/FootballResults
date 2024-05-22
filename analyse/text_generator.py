import pandas as pd
import datetime
from .data_manager import get_all_data
import matplotlib as plt


def generate_text(data: pd.DataFrame, team1: str, team2: str) -> str:
    average_cards = average_cards_per_game(get_all_data(), team1, team2)
    # TODO Text generieren
    return f"{team1} has an average of {average_cards[0]:.2f} yellow cards and {team2} an average of {average_cards[1]:.2f} per game! At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua."


# This function calculates how often the two teams have played against each other in the past X years
def games_played_between_teams(data, team1, team2, years):
    # Filter the data for matches between the two teams
    recent_years = datetime.now().year - years
    filtered_data = data[(data['Date'].dt.year >= recent_years) &
                         (((data['Home Team'] == team1) & (data['Away Team'] == team2)) |
                          ((data['Home Team'] == team2) & (data['Away Team'] == team1)))]
    return len(filtered_data)


# This function calculates the overall statistics for wins, draws and defeats for the two teams
def overall_stats(data, team1, team2):
    team1_wins = len(data[((data['Home Team'] == team1) & (data['Result'] == 'H')) |
                          ((data['Away Team'] == team1) & (data['Result'] == 'A'))])

    team2_wins = len(data[((data['Home Team'] == team2) & (data['Result'] == 'H')) |
                          ((data['Away Team'] == team2) & (data['Result'] == 'A'))])

    draws = len(data[data['Result'] == 'D'])

    team1_losses = len(data[((data['Home Team'] == team1) & (data['Result'] == 'A')) |
                            ((data['Away Team'] == team1) & (data['Result'] == 'H'))])

    team2_losses = len(data[((data['Home Team'] == team2) & (data['Result'] == 'A')) |
                            ((data['Away Team'] == team2) & (data['Result'] == 'H'))])

    return team1_wins, team2_wins, draws, team1_losses, team2_losses


# This function calculates the percentage by which the home team will win the match if it is leading at half-time
def home_win_when_leading_at_half(data):
    leading_at_half = data[(data['Half Time Home Goals'] > data['Half Time Away Goals'])]
    home_wins = leading_at_half[leading_at_half['Result'] == 'H']
    return len(home_wins) / len(leading_at_half) * 100 if len(leading_at_half) > 0 else 0


# This function calculates the percentage by which the away team will win the match if it is leading at half-time
def away_win_when_leading_at_half(data):
    leading_at_half = data[(data['Half Time Away Goals'] > data['Half Time Home Goals'])]
    away_wins = leading_at_half[leading_at_half['Result'] == 'A']
    return len(away_wins) / len(leading_at_half) * 100 if len(leading_at_half) > 0 else 0


# This function calculates the average number of goals scored between the two teams in the first and second half
def average_goals_per_half(data):
    first_half_goals = data['Half Time Home Goals'] + data['Half Time Away Goals']
    second_half_goals = (data['Full Time Home Goals'] - data['Half Time Home Goals']) + (
            data['Full Time Away Goals'] - data['Half Time Away Goals'])

    avg_first_half_goals = first_half_goals.mean()
    avg_second_half_goals = second_half_goals.mean()

    return avg_first_half_goals, avg_second_half_goals


# This function calculates the average number of yellow and red cards received per match per team
def average_cards_per_game(data, team1, team2):
    avg_yellow_team1 = data.apply(
        lambda row: row['HY'] if row['HomeTeam'] == team1 else (row['AY'] if row['AwayTeam'] == team1 else None),
        axis=1).dropna().mean()

    avg_yellow_team2 = data.apply(
        lambda row: row['HY'] if row['HomeTeam'] == team2 else (row['AY'] if row['AwayTeam'] == team2 else None),
        axis=1).dropna().mean()

    return (avg_yellow_team1, avg_yellow_team2)

    # avg_yellow_cards_home = data['Home Yellow Cards'].mean()
    # avg_yellow_cards_away = data['Away Yellow Cards'].mean()
    # avg_red_cards_home = data['Home Red Cards'].mean()
    # avg_red_cards_away = data['Away Red Cards'].mean()
    #
    # return avg_yellow_cards_home, avg_yellow_cards_away, avg_red_cards_home, avg_red_cards_away


# This function calculates the accuracy on shots
def calculate_shot_accuracy(data):
    home_shots = data['Home Shots']
    away_shots = data['Away Shots']
    home_shots_on_target = data['Home Shots on Target']
    away_shots_on_target = data['Away Shots on Target']

    home_accuracy = (home_shots_on_target.sum() / home_shots.sum()) * 100 if home_shots.sum() > 0 else 0
    away_accuracy = (away_shots_on_target.sum() / away_shots.sum()) * 100 if away_shots.sum() > 0 else 0

    return home_accuracy, away_accuracy


# This function calculates relevant correlations
def calculate_relevant_correlations(data):
    # Relevant metrics for the correlation
    metrics = ['Fouls Committed', 'Corners', 'Shots on Target', 'Shots', 'Yellow Cards', 'Red Cards']

    # Add a binary column for win (1) and loss (0)
    data['Home Win'] = data['Result'].apply(lambda x: 1 if x == 'H' else 0)
    data['Away Win'] = data['Result'].apply(lambda x: 1 if x == 'A' else 0)

    # Add the win columns to the metrics
    metrics += ['Home Win', 'Away Win']

    # Calculate the correlations
    correlation_matrix = data[metrics].corr()

    # Find the highest correlation
    corr = correlation_matrix.unstack()
    corr = corr[corr.index.get_level_values(0) != corr.index.get_level_values(1)]
    highest_corr = corr.abs().sort_values(ascending=False).head(1).index[0]
    highest_corr_value = corr.loc[highest_corr]

    return correlation_matrix, highest_corr, highest_corr_value


###################### TEXT IN PDF

def T_generate_text(data: pd.DataFrame, team1: str, team2: str) -> str:
    home_win_percentage = home_win_when_leading_at_half(data)
    away_win_percentage = away_win_when_leading_at_half(data)
    avg_first_half, avg_second_half = average_goals_per_half(data)
    avg_yellow_home, avg_yellow_away, avg_red_home, avg_red_away = average_cards_per_game(data)

    # Calculate the number of games played between the teams in the past X years
    # games_played = games_played_between_teams(data, team1, team2, years)

    # Calculate overall statistics
    team1_wins, team2_wins, draws, team1_losses, team2_losses = overall_stats(data, team1, team2)

    text = ""
    # text = f"In the past {years} years, {team1} and {team2} have played against each other {games_played} times.\n\n"
    text += f"{team1} Overall Stats: {team1_wins} Wins, {team1_losses} Losses, {draws} Draws\n"
    text += f"{team2} Overall Stats: {team2_wins} Wins, {team2_losses} Losses, {draws} Draws\n\n"
    text += f"In {home_win_percentage:.2f}% of the games, {team1} wins when leading at halftime.\n"
    text += f"In {away_win_percentage:.2f}% of the games, {team2} wins when leading at halftime.\n"
    text += f"Average number of goals in the first half: {avg_first_half:.2f}\n"
    text += f"Average number of goals in the second half: {avg_second_half:.2f}\n"
    text += f"Average number of yellow cards per game ({team1}): {avg_yellow_home:.2f}\n"
    text += f"Average number of yellow cards per game ({team2}): {avg_yellow_away:.2f}\n"
    text += f"Average number of red cards per game ({team1}): {avg_red_home:.2f}\n"
    text += f"Average number of red cards per game ({team2}): {avg_red_away:.2f}\n"

    # description for highest correlation
    # metric1, metric2 = highest_corr
    # description = (
    #     f"\nThe highest correlation is between {metric1} and {metric2} with a value of {highest_corr_value:.2f}. "
    #     f"This means that as {metric1} increases, {metric2} tends to increase as well (or decrease, if the value is negative). "
    #     "A high positive correlation (close to +1) indicates that these two metrics move in the same direction, "
    #     "while a high negative correlation (close to -1) indicates that they move in opposite directions. "
    #     "For example, if the correlation is between 'Home Shots on Target' and 'Home Win', it suggests that the more shots on target "
    #     "the home team has, the more likely they are to win."
    # )
    # text
    # 1 = description

    return text

    ###################### PLOTS

    # Pie plot for overall statistics


def plot_overall_stats(team1, team2, team1_wins, team2_wins, draws, team1_losses, team2_losses):
    # Data for the pie plot
    labels = [f'{team1} Wins', 'Draws', f'{team2} Wins']
    sizes = [team1_wins, draws, team2_wins]
    colors = ['#ff9999', '#66b3ff', '#99ff99']

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title('Overall Statistics')

    # Bar plot for shot accuracy


def plot_shot_accuracy(team1, team2, home_accuracy, away_accuracy):
    labels = [team1, team2]
    accuracies = [home_accuracy, away_accuracy]

    plt.figure(figsize=(8, 6))
    plt.bar(labels, accuracies, color=['blue', 'red'])
    plt.xlabel('Teams')
    plt.ylabel('Shot Accuracy (%)')
    plt.title('Percentage of Shots on Target')
    plt.ylim(0, 100)

    for i in range(len(accuracies)):
        plt.text(i, accuracies[i] + 1, f'{accuracies[i]:.2f}%', ha='center', va='bottom')

    # Correlation plot (heatmap)

# def plot_correlation_heatmap(correlation_matrix):
#     plt.figure(figsize=(10, 8))
#     sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
#     plt.title('Correlation Matrix')



##################### DUMMY PLOTS ########################
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def plot_correlation_heatmap(correlation_matrix):
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Matrix')
    plt.savefig('correlation_heatmap.png')
    plt.show()

# Example usage with dummy data
# Create a sample correlation matrix for demonstration
np.random.seed(0)
data = np.random.rand(10, 10)
correlation_matrix = pd.DataFrame(data, columns=['HF', 'AF', 'HC', 'AC', 'HS', 'AS', 'HY', 'AY', 'HR', 'AR']).corr()

new_labels = ['Home Fouls', 'Away Fouls', 'Home Corners', 'Away Corners', 'Home Shots', 'Away Shots',
              'Home Yellow', 'Away Yellow', 'HomeRed', 'AwayRed']
correlation_matrix.columns = new_labels
correlation_matrix.index = new_labels

plot_correlation_heatmap(correlation_matrix)


def plot_overall_stats(team1, team2, team1_wins, team2_wins, draws):
    # Data for the pie plot
    labels = [f'{team1} Wins', 'Draws', f'{team2} Wins']
    sizes = [team1_wins, draws, team2_wins]
    colors = ['#ff9999', '#66b3ff', '#99ff99']

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title('Overall Statistics')
    plt.savefig('overall.png')
    plt.show()

# Example usage with dummy data
team1 = 'Arsenal'
team2 = 'Chelsea'
team1_wins = 10
team2_wins = 4
draws = 2

plot_overall_stats(team1, team2, team1_wins, team2_wins, draws)

def plot_shot_accuracy(team1, team2, home_accuracy, away_accuracy):
    labels = [team1, team2]
    accuracies = [home_accuracy, away_accuracy]

    plt.figure(figsize=(8, 6))
    plt.bar(labels, accuracies, color=['blue', 'red'])
    plt.xlabel('Teams')
    plt.ylabel('Shot Accuracy (%)')
    plt.title('Percentage of Shots on Target')
    plt.ylim(0, 100)

    for i in range(len(accuracies)):
        plt.text(i, accuracies[i] + 1, f'{accuracies[i]:.2f}%', ha='center', va='bottom')

    plt.savefig('shot_accuracy.png')
    plt.show()

# Example usage with dummy data
team1 = 'Arsenal'
team2 = 'Chelsea'
home_accuracy = 76.12
away_accuracy = 82.98

plot_shot_accuracy(team1, team2, home_accuracy, away_accuracy)
