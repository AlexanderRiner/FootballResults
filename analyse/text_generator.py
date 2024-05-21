import pandas as pd
import datetime
from .data_manager import get_all_data
import matplotlib as plt

def generate_text(data: pd.DataFrame, team1: str, team2: str) -> str:
    games_played = games_played_between_teams(get_all_data(), team1, team2)
    win_losses_draw = overall_stats(get_all_data(), team1, team2)
    high_win = highest_win(get_all_data(),team1,team2)
    average_goals_half = average_goals_per_half(get_all_data(), team1, team2)
    average_yellow_cards = average_yellow_cards_per_game(get_all_data(), team1, team2)
    average_red_cards = average_red_cards_per_game(get_all_data(), team1, team2)
    shot_accuracy = calculate_shot_accuracy(get_all_data(), team1, team2)
    home_win_after_leading_at_halftime = home_win_when_leading_at_half(get_all_data())
    away_win_after_leading_at_halftime = away_win_when_leading_at_half(get_all_data())

    return (f"In the above mentioned period {team1} has played {games_played} games against {team2}. "
            f"{team1} has won {win_losses_draw[0]} game(s), {team2} has won {win_losses_draw[1]} game(s) & {win_losses_draw[2]} game(s) ended in a draw. "
            f"{high_win} was the highest win in this time period. "
            f"On average, {average_goals_half[0]:.2f} goals are scored between the two teams in the first half and {average_goals_half[1]:.2f} goals in the second half. "
            f"{team1} has an average of {average_yellow_cards[0]:.2f} yellow cards and {average_red_cards[0]:.2f} red cards per game. "
            f"{team2} has an average of {average_yellow_cards[1]:.2f} yellow cards and {average_red_cards[1]:.2f} red cards per game. "
            f"{team1} has a shooting accuracy of {shot_accuracy[0]:.0f}% while {team2} has an accuracy of {shot_accuracy[1]:.0f}%. "
            f"\n\nOverall stats for the period:"
            f"\nWhen the home team is leading at halftime, {home_win_after_leading_at_halftime}% of the games end with a win for the home team. "
            f"When the away team is leading at halftime, {away_win_after_leading_at_halftime}% of the games end with a win for the away team. ")

# This function calculates how often the two teams have played against each other in the past X years
def games_played_between_teams(data, team1, team2):
    # Filter the data for matches between the two teams
    filtered_data = data[(((data['HomeTeam'] == team1) & (data['AwayTeam'] == team2)) |
                          ((data['HomeTeam'] == team2) & (data['AwayTeam'] == team1)))]
    return len(filtered_data)


# This function calculates the overall statistics for wins, draws and defeats for the two teams
def overall_stats(data, team1, team2):
    # Filter the data for matches between team1 and team2
    matches = data[((data['HomeTeam'] == team1) & (data['AwayTeam'] == team2)) |
                   ((data['HomeTeam'] == team2) & (data['AwayTeam'] == team1))]

    team1_wins = len(matches[((matches['HomeTeam'] == team1) & (matches['FTR'] == 'H')) |
                             ((matches['AwayTeam'] == team1) & (matches['FTR'] == 'A'))])

    team2_wins = len(matches[((matches['HomeTeam'] == team2) & (matches['FTR'] == 'H')) |
                             ((matches['AwayTeam'] == team2) & (matches['FTR'] == 'A'))])

    team1_draws = len(matches[((matches['HomeTeam'] == team1) & (matches['FTR'] == 'D')) |
                              ((matches['AwayTeam'] == team1) & (matches['FTR'] == 'D'))])

    team2_draws = len(matches[((matches['HomeTeam'] == team2) & (matches['FTR'] == 'D')) |
                              ((matches['AwayTeam'] == team2) & (matches['FTR'] == 'D'))])

    team1_losses = len(matches[((matches['HomeTeam'] == team1) & (matches['FTR'] == 'A')) |
                               ((matches['AwayTeam'] == team1) & (matches['FTR'] == 'H'))])

    team2_losses = len(matches[((matches['HomeTeam'] == team2) & (matches['FTR'] == 'A')) |
                               ((matches['AwayTeam'] == team2) & (matches['FTR'] == 'H'))])

    return team1_wins, team2_wins, team1_draws, team2_draws, team1_losses, team2_losses

#This function determines the highest win in the Head to Head comparison
def highest_win(data, team1, team2):
    # Filter the data for matches between the two teams
    matches = data[(((data['HomeTeam'] == team1) & (data['AwayTeam'] == team2)) |
                    ((data['HomeTeam'] == team2) & (data['AwayTeam'] == team1)))]

    # Calculate the goal differences
    matches['GoalDiff'] = matches.apply(lambda row: abs(row['FTHG'] - row['FTAG']), axis=1)

    # Find the match with the highest goal difference
    highest_win_match = matches.loc[matches['GoalDiff'].idxmax()]

    if highest_win_match['FTHG'] > highest_win_match['FTAG']:
        return f"{highest_win_match['HomeTeam']} {int(highest_win_match['FTHG'])}:{int(highest_win_match['FTAG'])} {highest_win_match['AwayTeam']}"
    else:
        return f"{highest_win_match['AwayTeam']} {int(highest_win_match['FTAG'])}:{int(highest_win_match['FTHG'])} {highest_win_match['HomeTeam']}"


# This function calculates the percentage by which the home team will win the match if it is leading at half-time
def home_win_when_leading_at_half(data):
    leading_at_half = data[(data['HTHG'] > data['HTAG'])]
    home_wins = leading_at_half[leading_at_half['FTR'] == 'H']

    percentage = (len(home_wins) / len(leading_at_half) * 100) if len(leading_at_half) > 0 else 0

    return round(percentage)


# This function calculates the percentage by which the away team will win the match if it is leading at half-time
def away_win_when_leading_at_half(data):
    leading_at_half = data[(data['HTAG'] > data['HTHG'])]
    away_wins = leading_at_half[leading_at_half['FTR'] == 'A']

    percentage = (len(away_wins) / len(leading_at_half) * 100) if len(leading_at_half) > 0 else 0
    return round(percentage)


# This function calculates the average number of goals scored between the two teams in the first and second half
def average_goals_per_half(data, team1, team2):
    #Filter the data for matches involving team1 and team2
    team1_home = data[data['HomeTeam'] == team1]
    team1_away = data[data['AwayTeam'] == team1]
    team2_home = data[data['HomeTeam'] == team2]
    team2_away = data[data['AwayTeam'] == team2]

    matches = pd.concat([team1_home[team1_home['AwayTeam'] == team2], team1_away[team1_away['HomeTeam'] == team2],
                         team2_home[team2_home['AwayTeam'] == team1], team2_away[team2_away['HomeTeam'] == team1]])

    first_half_goals = matches['HTHG'] + matches['HTAG']
    second_half_goals = (matches['FTHG'] - matches['HTHG']) + (matches['FTAG'] - matches['HTAG'])

    avg_first_half_goals = first_half_goals.mean()
    avg_second_half_goals = second_half_goals.mean()

    return avg_first_half_goals, avg_second_half_goals


# This function calculates the average number of yellow cards received per match per team
def average_yellow_cards_per_game(data, team1, team2):
    avg_yellow_team1 = data.apply(
        lambda row: row['HY'] if row['HomeTeam'] == team1 else (row['AY'] if row['AwayTeam'] == team1 else None),
        axis=1).dropna().mean()

    avg_yellow_team2 = data.apply(
        lambda row: row['HY'] if row['HomeTeam'] == team2 else (row['AY'] if row['AwayTeam'] == team2 else None),
        axis=1).dropna().mean()

    return (avg_yellow_team1, avg_yellow_team2)

# This function calculates the average number of red cards received per match per team
def average_red_cards_per_game(data, team1, team2):
    avg_red_team1 = data.apply(
        lambda row: row['HR'] if row['HomeTeam'] == team1 else (row['AR'] if row['AwayTeam'] == team1 else None),
        axis=1).dropna().mean()

    avg_red_team2 = data.apply(
        lambda row: row['HR'] if row['HomeTeam'] == team2 else (row['AR'] if row['AwayTeam'] == team2 else None),
        axis=1).dropna().mean()

    return (avg_red_team1, avg_red_team2)


# This function calculates the accuracy on shots
def calculate_shot_accuracy(data, team1, team2):
    # Filter data for matches involving team1
    team1_home = data[data['HomeTeam'] == team1]
    team1_away = data[data['AwayTeam'] == team1]

    # Calculate shots and shots on target for team1
    team1_shots = team1_home['HS'].sum() + team1_away['AS'].sum()
    team1_shots_on_target = team1_home['HST'].sum() + team1_away['AST'].sum()

    # Calculate accuracy for team1
    team1_accuracy = (team1_shots_on_target / team1_shots) * 100 if team1_shots > 0 else 0

    # Filter data for matches involving team2
    team2_home = data[data['HomeTeam'] == team2]
    team2_away = data[data['AwayTeam'] == team2]

    # Calculate shots and shots on target for team2
    team2_shots = team2_home['HS'].sum() + team2_away['AS'].sum()
    team2_shots_on_target = team2_home['HST'].sum() + team2_away['AST'].sum()

    # Calculate accuracy for team2
    team2_accuracy = (team2_shots_on_target / team2_shots) * 100 if team2_shots > 0 else 0

    return team1_accuracy, team2_accuracy


# This function calculates relevant correlations
def calculate_relevant_correlations(data):
    # Relevant metrics for the correlation
    metrics = ['HF', 'AF', 'HC', 'AC', 'HS', 'AS', 'HY', 'AY', 'HR', 'AR']

    # Add a binary column for win (1) and loss (0)
    data['HomeWin'] = data['FTR'].apply(lambda x: 1 if x == 'H' else 0)
    data['AwayWin'] = data['FTR'].apply(lambda x: 1 if x == 'A' else 0)

    # Add the win columns to the metrics
    metrics += ['HomeWin', 'AwayWin']

    # Calculate the correlations
    correlation_matrix = data[metrics].corr()

    # Rename the columns and index
    new_labels = ['Home Fouls', 'Away Fouls', 'Home Corners', 'Away Corners', 'Home Shots', 'Away Shots',
                  'Home Yellow', 'Away Yellow', 'HomeRed', 'AwayRed']

    # Find the highest correlation
    corr = correlation_matrix.unstack()
    corr = corr[corr.index.get_level_values(0) != corr.index.get_level_values(1)]
    highest_corr = corr.abs().sort_values(ascending=False).head(1).index[0]
    highest_corr_value = corr.loc[highest_corr]

    return correlation_matrix, highest_corr, highest_corr_value



    ###################### PLOTS

# Pie plot for overall statistics
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
    plt.show


# Bar plot for shot accuracy
def plot_shot_accuracy(team1, team2, team1_accuracy, team2_accuracy):
    labels = [team1, team2]
    accuracies = [team1_accuracy, team2_accuracy]

    plt.figure(figsize=(8, 6))
    plt.bar(labels, accuracies, color=['blue', 'red'])
    plt.xlabel('Teams')
    plt.ylabel('Shot Accuracy (%)')
    plt.title('Percentage of Shots on Target')
    plt.ylim(0, 100)

    for i in range(len(accuracies)):
        plt.text(i, accuracies[i] + 1, f'{accuracies[i]:.2f}%', ha='center', va='bottom')


# Correlation plot (heatmap)
def plot_correlation_heatmap(correlation_matrix):
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Matrix')
    plt.savefig('correlation_heatmap.png')
    plt.show()

    correlation_matrix = pd.DataFrame(get_all_data(), columns= ['HF', 'AF', 'HC', 'AC', 'HS', 'AS', 'HY', 'AY', 'HR', 'AR'])

    # Rename the columns and index
    new_labels = ['Home Fouls', 'Away Fouls', 'Home Corners', 'Away Corners', 'Home Shots', 'Away Shots',
                  'Home Yellow', 'Away Yellow', 'HomeRed', 'AwayRed']
    correlation_matrix.columns = new_labels
    correlation_matrix.index = new_labels

    plot_correlation_heatmap(correlation_matrix)
