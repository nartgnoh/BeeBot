# botFairnessDistribution.py
import errno
import os
import random
import pandas as pd
import numpy as np
import xlsxwriter

from matplotlib import pyplot as plt


# changes for "dict_content.txt" and graph results
# loop quantity control
number_of_players_loop = 30
count_loop = 100
# folder name for bar and histo pngs
iteration_folder_name = 'Second Iteration'
parent_dir = r'C:\Users\Hong Tran\Python\BeeBot'

# creating new "dict_content.xlsx" file
dict_content_excel = xlsxwriter.Workbook('Code_files/Excel_files/dict_content.xlsx')
worksheet = dict_content_excel.add_worksheet()


# create new "sample_input.txt" file
input_file = open("Code_files/Text_files/sample_input.txt", "w")
# create new "dict_content.txt" file
dict_content_text = open("Code_files/Text_files/dict_content.txt", "w")


# creating a new "iteration_folder"
# check if folder already exists
try:
    child_dir = r'{}\Code_files\botFairnessDistribution_data\botFairnessDistribution_graphs'.format(parent_dir)
    path = os.path.join(child_dir, iteration_folder_name)
    os.mkdir(path)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise


number_of_players = 1
while number_of_players < number_of_players_loop+1:
    # fix for the full "GameName" not showing up
    # also the reason for the "FutureWarning: Passing a negative int..." error c:
    pd.set_option('display.max_colwidth', -1)
    # accessing GamesList.xlsx
    games_file = pd.read_excel(r'{}\Code_files\Excel_files\GameList.xlsx'.format(parent_dir))
    games_file_df = pd.DataFrame(games_file, columns=['GameName', 'PlayerNumMIN', 'PlayerNumMAX'])
    # calculating "player_range"
    player_range = games_file_df['PlayerNumMAX'] - games_file_df['PlayerNumMIN']
    games_file_df['PlayerRange'] = player_range
    # checking games within the specified range and creating a new dataframe for it
    player_range_check_df = games_file_df.loc[
        (games_file_df['PlayerNumMIN'] <= number_of_players) & (games_file_df['PlayerNumMAX'] >= number_of_players)]

    # printing games_names into "sample_input.txt" file
    count = 0
    while count < count_loop:
        game_names = pd.DataFrame(player_range_check_df, columns=['GameName'])
        random_game = game_names.sample().to_string(index=False, header=False)
        print(random_game, file=input_file)
        count += 1

    number_of_players += 1
input_file.close()
print('sample_input.txt is ready')


# counting repeats
text = open("Code_files/Text_files/sample_input.txt", "r")

# initial info for "dict_content.xlsx" file
dict_content_excel_array = []
dce_row = 0
dce_col = 0

# Create an empty dictionary
d = dict()
# Loop through each line of the file
for lines in text:
    # lowercase to avoid case mismatch and removes whitespace at the beginning (right) of the line
    # lines = lines.lower() # lowering unnecessary
    lines = lines.rstrip()
    # Split the lines into lines
    lines = lines.split("\n")
    # Iterate over each word in line
    for line in lines:
        # Check if the word is already in dictionary
        if line in d:
            # Increment count of word by 1
            d[line] = d[line] + 1
        else:
            # Add the word to dictionary with count 1
            d[line] = 1

# Print the contents of dictionary
for key in list(d.keys()):
    # print(key, ":", d[key])
    print(d[key], ":", key, file=dict_content_text)
    key_for_dce = [key, d[key]]
    dict_content_excel_array.append(key_for_dce)

# add "dict_content_excel_array" into "dict_content_excel" file
for GameName, CountFromData in (dict_content_excel_array):
    worksheet.write(dce_row, dce_col, GameName)
    worksheet.write(dce_row, dce_col + 1, CountFromData)
    dce_row += 1
dict_content_excel.close()


# finding total_sum and games_count
total_sum = 0
games_count = 0
for key in list(d.keys()):
    total_sum = total_sum + d[key]
    games_count += 1
# count_games = count_games/2
print(games_count)
print(total_sum)


# creating bar and histo graphs

# create bar graph of data
fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1])

game_name_graph = []
game_repeats = []
for key in list(d.keys()):
    game_name_graph.append(key)
    game_repeats.append(d[key])
ax.bar(game_name_graph, game_repeats)
plt.savefig(r'Code_files\botFairnessDistribution_data\botFairnessDistribution_graphs\{}\bar_'
            r'{}x{}'.format(iteration_folder_name, number_of_players_loop, count_loop))
plt.show()


# create histo graph of data
plt.hist(game_repeats, bins=games_count)
plt.savefig(r'Code_files\botFairnessDistribution_data\botFairnessDistribution_graphs\{}\histo_'
            r'{}x{}'.format(iteration_folder_name, number_of_players_loop, count_loop))
plt.show()


# program ends (to check if in infinite loops)
print('program done c:')
exit()
