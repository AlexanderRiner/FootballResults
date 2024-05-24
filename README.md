# FootballResults

A python project designed to analyze and visualize football data by comparing the performance
of two teams and generating a detailed PDF report that includes plots and textual analysis.
The program is organized into several scripts, each handling a specific part of the workflow.

# Table of Contents

- Installation
- Usage and Features
- How the Program Works
- Ideas for Future Improvement
- Contributing
- License
- Contact

# Installation

### Clone the repository

    git clone https://github.com/alexanderhepburn/FootballResults.git

### Navigate to the project directory

    cd FootballResults

### Install the required dependencies

    pip install -r requirements.txt

# Usage and Features

1. To start the program, run the ```run.py``` script
2. The program will ask you to input a command
3. to get an overview of the available commands, input ```help```
4. Choose one of the following features:

- ```analyse``` create a report with two football teams of your choice
- ```teams``` view the available teams in your selected league
- ```settings``` view and change your current settings (you can change the years for the statistics here or change the
  preferred league)
- ```update_data``` update all data manually

5. after you analyse two teams of your choice, the program will automatically create a PDF document of the football
   statistics on your local drive
6. You can repeat the steps if you want to analyse different teams in different leagues

# Debugging

If the programm has any errors, try creating a virtual environment and installing all requirements:

    python3 -m venv myenv

Replace myenv with your environment name and run the environment:

    source myenv/bin/activate

Install the requirements:

    pip install -r requirements.txt

Run the script (make sure you are in the FootballResults directory):

    python3 run.py

# How the Program Works

## Key Components and Their Interactions

1. Main script ```run.py```

- **Purpose:** Entry point for the program.
- **Functionality:**
  Calls ```setup_program.setup_program()``` to install dependencies and create necessary directories.
  Runs the main loop provided by ```command_manager.run_program()``` to handle user inputs.

2. Setup ```setup_program.py```

- **Purpose:** Sets up the program environment.
- **Functionality:**
  Installs required dependencies from ```requirements.txt``` using ```subprocess```.
  Creates ```tmp``` and ```exports``` directories if they do not exist.
  Checks if the data directory exists and calls ```network_manager.get_all_data()``` if data needs to be downloaded.

3. Command management ```command.py```, ```commands.py```, ```command_manager.py```

- **Purpose:** Manages user commands.
- **Classes and Functions:**
    - ```Command``` Abstract base class for all commands. Implements common attributes and abstract
      method ```execute()```.
    - ```get_commands()``` Returns a list of command
      instances (```Analyse```, ```Teams```, ```UpdateData```, ```Settings```).
    - ```run_program()``` Main loop that prompts the user for commands, matches the input with available commands, and
      executes the corresponding command’s ```execute()``` method.
      Handles special commands like ```help``` to list all commands and ```end``` to terminate the program.

4. Data management ```data_manager.py```, ```network_manager.py```

- **Purpose:** Handles data retrieval, downloading, and preparation.
- **Functions:**
    - ```data_manager.py```
        - ```get_all_data()``` Reads CSV files from the ```data``` directory, combines them into a DataFrame, and
          filters based on user settings.
        - ```get_all_teams()``` Extracts and returns a list of unique team names from the data.
        - ```get_data_with_columns()``` Retrieves and aggregates specific columns of data for the selected teams.
    - ```etwork_manager.py```
        - ```get_all_data()``` Downloads football data for all years and leagues, saves them as CSV files in
          the ```data``` directory.

5. PDF creation ```pdf_creator.py```

- **Purpose:** Generates a PDF report.
- **Function:** ```create_pdf()``` Takes the team names and text content, creates a PDF with this information, and
  embeds plots generated by the ```Plot``` class.

6. Plotting ```plot.py```

- **Purpose:** Generates visual plots comparing team performance metrics.
- **Class:** ```Plot```
    - **Methods:**
        - ```__init__()``` Initializes the ```Plot``` object with data and team information, then
          calls ```plot_bars()``` to create all required plots.
        - ```create_bar()``` Creates individual bar plots for each specified metric and saves them as images.
        - ```plot_bars()``` Iterates through the specified metrics, extracts the relevant data for the two teams, and
          calls ```create_bar()``` for each metric.

7. Analysis ```analyse.py```

- **Purpose:** Orchestrates the analysis and report generation process.
- **Class:** ```Analyse```
    - **Method:** ```execute():```
        - Prompts the user to input two team names.
        - Validates the input and ensures two unique teams are selected.
        - Calls ```analyse.analyse()``` to generate the report.
        - Opens the generated PDF report using ```system_handling.open_file()```.

8. Text Generation ```text_generator.py```

- **Purpose:** Generates textual analysis for the PDF report.
- **Functions:**
    - ```generate_text()``` Placeholder function to generate text content for the report.
- **Helper functions:** Calculate various statistics like games played, overall stats, win percentages, average goals,
  card counts, shot accuracy, and correlations.
    - ```T_generate_text()``` Compiles the calculated statistics into a comprehensive text format for inclusion in the
      PDF report.

9. Settings
   Management ```settings_manager.py```, ```settings_object.py```, ```settings_option.py```, ```user_settings.py```

- **Purpose:** Manages user settings.
- **Classes:**
    - **```SettingsManager```**
        - Manages settings initialization, reset, and refresh.
        - Provides methods to update settings and save them to a JSON file.
    - **```SettingsObject```**
        - Represents user settings with attributes for the starting year, ending year, and selected league.
        - Provides methods to load default and user-defined settings from a JSON file.
    - **```SettingsOption```**, **```RangeSettingsOption```**, **```ListSettingsOption**```
        - Represent different types of settings options.
        - Provide methods to validate and display setting options.
    - **```UserSettings```**
        - Singleton class that provides access to the current settings instance and updates settings.

10. Utility ```system_handling.py```

- **Purpose:** Handles system-specific tasks.
- **Function:**
    - ```open_file()``` Opens a file using the default application based on the operating system.

# Ideas for Future Improvement

1. Enhanced data visualization:
    - Interactive plots: Use libraries like Plotly or Bokeh to create interactive plots, allowing users to hover over
      data points for detailed insights and dynamic data exploration.
      Expanded data analysis:

2. Advanced metrics:
    - Introduce advanced football metrics such as expected goals, passing accuracy, and possession percentage to provide
      deeper insights into team and player performance.

3. User interface enhancements:graphical user interface (GUI):
    - Develop a user-friendly GUI using frameworks like Tkinter, PyQt, or a web-based interface with Flask/Django to
      improve accessibility and ease of use.

# Contributing

- Fork the repository
- Create a new branch for your feature or bug fix
- Commit your changes
- Push to the branch
- Open a Pull Request

# License

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to use, copy, modify, and distribute the Software without restriction, subject to
the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

# Contact

- Email: student@student.unisg.ch
- linkedin: www.linkedin.com/in/student
- GitHub: https://github.com/Student

*Note:* This README contains placeholder information to demonstrate the structure and completeness of the document. The
contact details are not real and are included only for illustrative purposes as we did not want to share our real
contact details.

# Disclaimer

This project has utilized ChatGPT for assistance with various code snippets and project documentation.