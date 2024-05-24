import pandas as pd
from settings import UserSettings


class GenerateText:
    """
    A class to generate descriptive text based on football match statistics
    between two specified teams.

    Attributes:
    data (pd.DataFrame): DataFrame containing match data.
    team1 (str): Name of the first team.
    team2 (str): Name of the second team.
    matches (pd.DataFrame): Filtered DataFrame containing matches between the two teams.
    highest_win (str): Description of the match with the highest win.
    avg_yellow_cards (tuple): Average yellow cards per game for both teams.
    avg_red_cards (tuple): Average red cards per game for both teams.
    shot_accuracy_team1 (float): Shot accuracy for team1.
    shot_accuracy_team2 (float): Shot accuracy for team2.
    avg_first_half_goals (float): Average goals scored in the first half.
    avg_second_half_goals (float): Average goals scored in the second half.
    team1_wins (int): Number of wins for team1.
    team1_losses (int): Number of losses for team1.
    draws (int): Number of draws between the two teams.

    Methods:
    _calculate_all_stats(): Calculate all necessary statistics for the matches.
    get_text() -> str: Generate a descriptive text based on the calculated statistics.
    overall_stats(): Calculate overall statistics for wins, losses, and draws for the teams.
    calculate_highest_win(): Calculate the highest win between the two teams based on goal difference.
    win_percentage_when_leading_at_half(home=True) -> float: Calculate the win percentage when leading at halftime.
    average_cards_per_game(yellow_card=True) -> tuple: Calculate the average number of yellow or red cards per game for both teams.
    average_goals_per_half() -> None: Calculate the average number of goals scored in the first and second half.
    calculate_shot_accuracy() -> tuple: Calculate the shot accuracy for both teams.
    """

    def __init__(self, data: pd.DataFrame, team1: str, team2: str):
        """
        Initialize the GenerateText class with match data and teams.

        Parameters:
        data (pd.DataFrame): DataFrame containing match data.
        team1 (str): Name of the first team.
        team2 (str): Name of the second team.
        """
        self.data = data
        self.team1 = team1
        self.team2 = team2
        # Filter matches between the two teams
        try:
            self.matches = self.data[((self.data['HomeTeam'] == self.team1) & (self.data['AwayTeam'] == self.team2)) |
                                     ((self.data['HomeTeam'] == self.team2) & (self.data['AwayTeam'] == self.team1))]

            # Check that the teams have played against each other and raise ValueError if not
            if len(self.matches) == 0:
                raise ValueError
        except Exception:
            # Pass the ValueError up to commands/analyse.py
            raise ValueError
        # Calculate all statistics
        self._calculate_all_stats()

    def _calculate_all_stats(self) -> None:
        """
        Calculate all necessary statistics for the matches.
        """
        self.overall_stats()
        self.calculate_highest_win()
        self.average_goals_per_half()
        self.avg_yellow_cards = self.average_cards_per_game(yellow_card=True)
        self.avg_red_cards = self.average_cards_per_game(yellow_card=False)
        self.shot_accuracy_team1, self.shot_accuracy_team2 = self.calculate_shot_accuracy()

    def get_text(self) -> str:
        """
        Generate a descriptive text based on the calculated statistics.

        Returns:
        str: A formatted string with match statistics and comparisons.
        """
        return (f"During {UserSettings.get_instance().starting_year} and {UserSettings.get_instance().ending_year}, "
                f"{self.team1} played {len(self.matches)} games against {self.team2}, winning {self.team1_wins}, "
                f"losing {self.team1_losses} and drawing {self.draws} games. On average, {self.avg_first_half_goals:.1f} "
                f"goals were scored in the first half and {self.avg_second_half_goals:.1f} goals in the second. {self.highest_win} "
                f"was the highest win in this time period. {self.team1} had an average of {self.avg_yellow_cards[0]:.2f} yellow cards "
                f"and {self.avg_red_cards[0]:.2f} red cards per game. {self.team2} had an average of {self.avg_yellow_cards[1]:.2f} yellow cards "
                f"and {self.avg_red_cards[1]:.2f} red cards per game. {self.team1} had a shooting accuracy of {self.shot_accuracy_team1:.0f}% while "
                f"{self.team2} had an accuracy of {self.shot_accuracy_team2:.0f}%. In the entire league, when the home team was leading at halftime, "
                f"{self.win_percentage_when_leading_at_half(home=True)}% of the time they won the game, whereas when the away team was leading, "
                f"{self.win_percentage_when_leading_at_half(home=False)}% of games were won.")

    def overall_stats(self) -> None:
        """
        Calculate overall statistics for wins, losses, and draws for the teams.
        """
        self.team1_wins = self.matches[((self.matches['HomeTeam'] == self.team1) & (self.matches['FTR'] == 'H')) |
                                       ((self.matches['AwayTeam'] == self.team1) & (self.matches['FTR'] == 'A'))].shape[
            0]

        self.team1_losses = self.matches[((self.matches['HomeTeam'] == self.team2) & (self.matches['FTR'] == 'H')) |
                                         ((self.matches['AwayTeam'] == self.team2) & (
                                                 self.matches['FTR'] == 'A'))].shape[0]

        self.draws = self.matches[self.matches['FTR'] == 'D'].shape[0]

    def calculate_highest_win(self) -> None:
        """
        Calculate the highest win between the two teams based on goal difference.
        """
        # Calculate the goal difference without modifying self.matches directly
        temp_matches = self.matches.copy()
        goal_diff = (temp_matches['FTHG'] - temp_matches['FTAG']).abs()
        # Combine the goal difference with the matches DataFrame temporarily
        temp_matches['GoalDiff'] = goal_diff

        # Find the match with the highest goal difference
        highest_win_match = temp_matches.loc[temp_matches['GoalDiff'].idxmax()]

        if highest_win_match['FTHG'] > highest_win_match['FTAG']:
            result = f"{highest_win_match['HomeTeam']} {highest_win_match['FTHG']:.0f}:{highest_win_match['FTAG']:.0f} {highest_win_match['AwayTeam']}"
        else:
            result = f"{highest_win_match['AwayTeam']} {highest_win_match['FTAG']:.0f}:{highest_win_match['FTHG']:.0f} {highest_win_match['HomeTeam']}"

        self.highest_win = result

    def win_percentage_when_leading_at_half(self, home=True) -> float:
        """
        Calculate the win percentage by which the home or away team will win the match if it is leading at halftime.
        (Over the entire period and not just in a head-to-head comparison)

        Parameters:
        home (bool): True if calculating for home team, False for away team.

        Returns:
        float: Win percentage when leading at halftime.
        """
        leading_at_half = self.data[self.data['HTHG'] > self.data['HTAG']] if home else self.data[
            self.data['HTAG'] > self.data['HTHG']]
        wins = leading_at_half[leading_at_half['FTR'] == ('H' if home else 'A')]

        percentage = (len(wins) / len(leading_at_half) * 100) if len(leading_at_half) > 0 else 0
        return round(percentage)

    def average_cards_per_game(self, yellow_card=True) -> tuple:
        """
        Calculate the average number of yellow or red cards per game for both teams.

        Parameters:
        yellow_card (bool): True to calculate yellow cards, False for red cards.

        Returns:
        tuple: Average number of cards per game for team1 and team2.
        """
        card_type = 'Y' if yellow_card else 'R'
        home_card_column = f'H{card_type}'
        away_card_column = f'A{card_type}'

        avg_cards_team1 = self.data.apply(
            lambda row: row[home_card_column] if row['HomeTeam'] == self.team1 else (
                row[away_card_column] if row['AwayTeam'] == self.team1 else None),
            axis=1).dropna().mean()

        avg_cards_team2 = self.data.apply(
            lambda row: row[home_card_column] if row['HomeTeam'] == self.team2 else (
                row[away_card_column] if row['AwayTeam'] == self.team2 else None),
            axis=1).dropna().mean()

        return avg_cards_team1, avg_cards_team2

    def average_goals_per_half(self) -> None:
        """
        Calculate the average number of goals scored between the two teams in the first and second half.

        Returns:
        None
        """
        #Calculate the total number of goals scored in the first half
        first_half_goals = self.matches['HTHG'] + self.matches['HTAG']
        #Calculate the total number of goals scored in the second half
        second_half_goals = (self.matches['FTHG'] - self.matches['HTHG']) + (
                self.matches['FTAG'] - self.matches['HTAG'])

        #Calculate the average number of goals for each half
        self.avg_first_half_goals = first_half_goals.mean()
        self.avg_second_half_goals = second_half_goals.mean()

    def calculate_shot_accuracy(self) -> tuple:
        """
        Calculate the shot accuracy for both teams.

        Returns:
        tuple: Shot accuracy for team1 and team2.
        """

        def shot_accuracy(team: str) -> float:
            """Helper function to calculate shot accuracy for a given team"""
            team_home = self.data[self.data['HomeTeam'] == team]
            team_away = self.data[self.data['AwayTeam'] == team]

            shots = team_home['HS'].sum() + team_away['AS'].sum()
            shots_on_target = team_home['HST'].sum() + team_away['AST'].sum()

            accuracy = (shots_on_target / shots) * 100 if shots > 0 else 0
            return accuracy

        team1_accuracy = shot_accuracy(self.team1)
        team2_accuracy = shot_accuracy(self.team2)
        return team1_accuracy, team2_accuracy

    def calculate_relevant_correlations(self):
        """
        Calculate the relevant correlations.

        Returns:
        DataFrame: correlation matrix
        """
        # Relevant metrics for the correlation
        metrics = ['HF', 'AF', 'HC', 'AC', 'HS', 'AS', 'HY', 'AY', 'HR', 'AR']
    
        # Create a binary win/loss column for home and away
        self.data['HomeWin'] = self.data['FTR'].apply(lambda x: 1 if x == 'H' else 0)
        self.data['AwayWin'] = self.data['FTR'].apply(lambda x: 1 if x == 'A' else 0)
    
        # Add these win columns to the metrics
        metrics += ['HomeWin', 'AwayWin']
    
        # Create the correlation matrix
        correlation_matrix = self.data[metrics].corr()

        # Rename the columns and index
        new_labels = ['Home Fouls', 'Away Fouls', 'Home Corners', 'Away Corners', 'Home Shots', 'Away Shots',
                      'Home Yellow', 'Away Yellow', 'Home Red', 'Away Red', 'Home Win', 'Away Win']
        correlation_matrix.columns = new_labels
        correlation_matrix.index = new_labels
    
        return correlation_matrix

   ################### Plots ########################

# Pie plot for overall statistics
def plot_overall_stats(self):
    # Data for the pie plot
    labels = [f'{self.team1} Wins', 'Draws', f'{self.team2} Wins']
    sizes = [self.team1_wins,self.draws, self.team2_wins]
    colors = ['#ff9999', '#66b3ff', '#99ff99']

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title('Overall Statistics')
    plt.savefig('overall.png')
    plt.show


# Bar plot for shot accuracy
def plot_shot_accuracy(self):
    labels = [team1, team2]
    accuracies = [self.shot_accuracy_team1, self.shot_accuracy_team2]

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

# Plot a heatmap for the correlation matrix of various match metrics including wins
def plot_correlation_heatmap(self):
    correlation_matrix = self.calculate_relevant_correlations()

    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Matrix')
    plt.savefig('correlation_heatmap.png')
    plt.show()


