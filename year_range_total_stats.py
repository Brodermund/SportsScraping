"""Module providing a function printing python version."""
# import sys
import os
import time
import json
from pathlib import Path
from operator import itemgetter
from datetime import datetime
# from ratelimit import limits, sleep_and_retry
from bs4 import BeautifulSoup as soup
import requests
import pandas as pd
MIN_PYTHON = (3, 10)
# if sys.version_info < MIN_PYTHON:
#     sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)



CURRENT_SEASON = 2024
START_SEASON = 1966
END_SEASON = 2024
POS_FILTER = {}
SORT_STAT = "pass_att"

CALL_LIMIT = 20
CALL_PERIOD = 60


players_array = {}

# @sleep_and_retry
# @limits(calls=20, period=60)
def html_request(url):
    """Takes URL input and returns the site data in text format"""
    sleep_time = CALL_PERIOD/CALL_LIMIT
    time.sleep(sleep_time)
    data = requests.get(url,timeout=10).text
    return data
def load_json(file_path):
    """Function that loads a JSON file"""
    with open(file_path,encoding='utf-8') as file:
        data = json.load(file)
        return data
stats_ref = load_json("Utils/StatsRef.json")
stats_ignore = load_json("Utils/StatsIgnore.json")
class General:
    """Class Representing a Players General Stats for a Statstical Season"""
    def __init__(self,dictionary):
        self.games = dictionary["games"]
        self.games_started = dictionary["games_started"]
class Rushing:
    """Class Representing a Players Rushing Stats for a Statstical Season"""
    def __init__(self,dic):
        self.rush_att = dic["rush_att"] if "rush_att"in dic else [0]
        self.rush_yds = dic["rush_yds"] if "rush_yds"in dic else [0]
        self.rush_td = dic["rush_td"] if "rush_td"in dic else [0]
        self.rush_first_down = dic["rush_first_down"] if "rush_first_down"in dic else [0]
        self.rush_long = dic["rush_long"] if "rush_long"in dic else [0]
        self.rush_yds_per_att = dic["rush_yds_per_att"] if "rush_yds_per_att"in dic else [0]
        self.rush_yds_per_g = dic["rush_yds_per_g"] if "rush_yds_per_g"in dic else [0]
        self.rush_att_per_g = dic["rush_att_per_g"] if "rush_att_per_g"in dic else [0]
        self.fumbles = dic["fumbles"] if "fumbles"in dic else [0]
class Receiving:
    """Class Representing a Players Receiving Stats for a Statstical Season"""
    def __init__(self,dic):
        self.targets = dic["targets"] if "targets"in dic else [0]
        self.rec = dic["rec"] if "rec"in dic else [0]
        self.rec_yds = dic["rec_yds"] if "rec_yds"in dic else [0]
        self.rec_yds_per_rec = dic["rec_yds_per_rec"] if "rec_yds_per_rec"in dic else [0]
        self.rec_td = dic["rec_td"] if "rec_td"in dic else [0]
        self.rec_first_down = dic["rec_first_down"] if "rec_first_down"in dic else [0]
        self.rec_long = dic["rec_long"] if "rec_long"in dic else [0]
        self.rec_per_g = dic["rec_per_g"] if "rec_per_g"in dic else [0]
        self.rec_yds_per_g = dic["rec_yds_per_g"] if "rec_yds_per_g"in dic else [0]
        self.catch_pct = dic["catch_pct"] if "catch_pct"in dic else [0]
        self.rec_yds_per_tgt = dic["rec_yds_per_tgt"] if "rec_yds_per_tgt"in dic else [0]
class Passing:
    """Class Representing a Players Passing Stats for a Statstical Season"""
    def __init__(self,dic):
        self.pass_cmp = dic["pass_cmp"] if "pass_cmp"in dic else [0]
        self.pass_att = dic["pass_att"] if "pass_att"in dic else [0]
        self.qb_rec = dic["qb_rec"] if "qb_rec"in dic else [0]
        self.pass_cmp_pct = dic["pass_cmp_pct"] if "pass_cmp_pct"in dic else [0]
        self.pass_yds = dic["pass_yds"] if "pass_yds"in dic else [0]
        self.pass_td = dic["pass_td"] if "pass_td"in dic else [0]
        self.pass_td_pct = dic["pass_td_pct"] if "pass_td_pct"in dic else [0]
        self.pass_int = dic["pass_int"] if "pass_int"in dic else [0]
        self.pass_int_pct = dic["pass_int_pct"] if "pass_int_pct"in dic else [0]
        self.pass_first_down = dic["pass_first_down"] if "pass_first_down"in dic else [0]
        self.pass_long = dic["pass_long"] if "pass_long"in dic else [0]
        self.pass_yds_per_att = dic["pass_yds_per_att"] if "pass_yds_per_att"in dic else [0]
        self.pass_adj_yds_per_att = dic["pass_adj_yds_per_att"] if "pass_adj_yds_per_att"in dic else [0]
        self.pass_yds_per_cmp = dic["pass_yds_per_cmp"] if "pass_yds_per_cmp"in dic else [0]
        self.pass_yds_per_g = dic["pass_yds_per_g"] if "pass_yds_per_g"in dic else [0]
        self.pass_rating = dic["pass_rating"] if "pass_rating"in dic else [0]
        self.pass_sacked = dic["pass_sacked"] if "pass_sacked"in dic else [0]
        self.pass_sacked_yds = dic["pass_sacked_yds"] if "pass_sacked_yds"in dic else [0]
        self.pass_sacked_pct = dic["pass_sacked_pct"] if "pass_sacked_pct"in dic else [0]
        self.pass_net_yds_per_att = dic["pass_net_yds_per_att"] if "pass_net_yds_per_att"in dic else [0]
        self.pass_adj_net_yds_per_att = dic["pass_adj_net_yds_per_att"] if "pass_adj_net_yds_per_att"in dic else [0]
class Season:
    """Class Representing a single Statstical Season"""
    def __init__(self, year):
        self.year = year
        self.general = None
        self.passing = None
        self.rushing = None
        self.receiving = None
class Player:
    """Class Representing a single Player Instance"""
    def __init__(self, name, player_id, pos ,stats):
        self.name = name
        self.id = player_id
        self.pos = pos
        self.stats = stats
        self.totals = {}

    def get_totals(self):
        """Function that returns the total sum stats for the Player"""
        total_dict = {}
        fin_dict = {}
        for key in self.stats:
            gen_stats = vars(self.stats[key].general)
            pass_stats = vars(self.stats[key].passing)
            rush_stats = vars(self.stats[key].rushing)
            receiving_stats = vars(self.stats[key].receiving)
            for item in gen_stats:
                total_dict.setdefault(item,[]).append(gen_stats[item][0])
            for item in pass_stats:
                total_dict.setdefault(item,[]).append(pass_stats[item][0])
            for item in rush_stats:
                total_dict.setdefault(item,[]).append(rush_stats[item][0])
            for item in receiving_stats:
                total_dict.setdefault(item,[]).append(receiving_stats[item][0])
        for key in total_dict:
            cal = stat_calculations(total_dict,key)
            fin_dict.setdefault(stats_ref[key]["title"],cal)
        return fin_dict
    def get_yearly(self,year):
        """Function that returns the total sum stats for every season"""
        year_dict = {}
        fin_dict = {}
        if year in self.stats:
            gen_stats = vars(self.stats[year].general)
            pass_stats = vars(self.stats[year].passing)
            rush_stats = vars(self.stats[year].rushing)
            receiving_stats = vars(self.stats[year].receiving)
            for item in gen_stats:
                year_dict.setdefault(item,[]).append(gen_stats[item][0])
            for item in pass_stats:
                year_dict.setdefault(item,[]).append(pass_stats[item][0])
            for item in rush_stats:
                year_dict.setdefault(item,[]).append(rush_stats[item][0])
            for item in receiving_stats:
                year_dict.setdefault(item,[]).append(receiving_stats[item][0])
            for key in year_dict:
                cal = stat_calculations(year_dict,key)
                fin_dict.setdefault(stats_ref[key]["title"],cal)
            return fin_dict
        return None
def get_player(row):
    """Function that returns Player obj from array or creates and appends one"""
    player_id = ""
    player_name = ""
    position = ""
    for cell in row.findAll('td'):
        if cell.attrs["data-stat"] == "name_display":
            player_id = cell.attrs["data-append-csv"]
            player_name = cell.text
        elif cell.attrs["data-stat"] == "pos":
            position = cell.text
        else:
            continue


    if player_id in players_array:
        player = players_array[player_id]
        # print("{0} already exists in Players Array".format(playerName))
        return player
    player = Player(player_name,player_id,position,{})
    if player.pos in POS_FILTER or len(POS_FILTER) == 0:
        players_array.setdefault(player_id,player)
    return player
def _sum(arr):
    sum_var = 0
    for i in arr:
        arg = int(i) if i != '' else 0
        sum_var = sum_var + arg
    return sum_var
def stat_sum(dictionary,stat):
    """Returns the sum of all values in a stat array"""
    if stat in dictionary:
        sum_result = _sum(dictionary[stat])
        return sum_result
    return None
def calculate_record(dictionary):
    """Calculates the Record for the QB"""
    w = 0
    l = 0
    t = 0
    for item in dictionary["qb_rec"]:
        if item != "" and item != "0":
            splitlist = item.split("-")
            w = w + int(splitlist[0])
            l = l + int(splitlist[1])
            t = t + int(splitlist[2])
    return f"{w}-{l}-{t}"
def stat_calculations_advanced(dictionary,stat):
    """Calculates and returns the Total Value"""
    att = stat_sum(dictionary,"pass_att")
    yds = stat_sum(dictionary,"pass_yds")
    pass_td = stat_sum(dictionary,"pass_td")
    pass_int = stat_sum(dictionary,"pass_int")
    sks = stat_sum(dictionary,"pass_sacked")
    sk_yds = stat_sum(dictionary,"pass_sacked_yds")
    label = {
        "anya":"pass_adj_net_yds_per_att",
        "nya":"pass_net_yds_per_att",
        "aya":"pass_adj_yds_per_att",
        "sk_pct":"pass_sacked_pct",
    }
    anya_num = (yds - sk_yds + (20 * pass_td) - (45 * pass_int))
    comp_num = yds - sk_yds if stat is label["nya"] else anya_num if stat is label["anya"] else sks
    aya_num = yds + 20 * pass_td - 45 * pass_int
    num = aya_num if stat is label["aya"] else comp_num
    den = att if stat is label["aya"] else att + sks
    if den == 0:
        return 0
    round_length = 4 if stat is label["sk_pct"] else 2
    return round(num/den,round_length)
def stat_calculations(dictionary,stat):
    """Calculates and returns the Total Value"""
    stat_type = stats_ref[stat]["type"]
    if stat_type in ('descriptive', 'cumulative'):
        descriptive_result = dictionary[stat][0]
        cumulative_result = stat_sum(dictionary,stat)
        return descriptive_result if stat_type == "descriptive" else cumulative_result
    if stat_type in ('percentage', 'average'):
        num_arg = stats_ref[stat]["Calculate"]["num"]
        den_arg = stats_ref[stat]["Calculate"]["den"]
        num = _sum(dictionary[num_arg])
        den = _sum(dictionary[den_arg])
        round_length = 4 if stat_type == "percentage" else 2
        return 0 if den == 0 else round(num/den,round_length)
    if stat_type in ('record', 'max'):
        record_result = calculate_record(dictionary)
        max_result = max(dictionary[stat])
        return record_result if stat_type == "record" else max_result
    if stat_type in ('rating', 'advanced'):
        rating_result = round(calculate_qb_rating(dictionary),2)
        advanced_result = stat_calculations_advanced(dictionary,stat)
        return rating_result if stat_type == "rating" else advanced_result
    return 0
def calculate_qb_rating(dictionary):
    """Calculates and returns the QB Rating"""
    att = stat_sum(dictionary,"pass_att")
    cmp = stat_sum(dictionary,"pass_cmp")
    yds = stat_sum(dictionary,"pass_yds")
    td = stat_sum(dictionary,"pass_td")
    interceptions = stat_sum(dictionary,"pass_int")
    if att != 0:
        rate = handle_nfl_passer_rating(att,cmp,yds,td,interceptions)
        return rate
    return 0
def handle_nfl_passer_rating(att,cmpls, yds, tds, ints):
    """Defines a function which handles passer rating calculation for the NFL."""
    def _min_max(x, xmin, xmax):
        """
        Defines a function which enforces a minimum and maximum value.
        Input: x, the value to check.
        Input: xmin, the minumum value.
        Input: xmax, the maximum value.
        Output: Either x, xmin or xmax, depending.
        """
        # Check if x is less than the minimum. If so, return the minimum.
        if x < xmin:
            return xmin
        # Check if x is greater than the maximum. If so, return the maximum.
        elif x > xmax:
            return xmax
        # Otherwise, just return x. And weep for the future.
        else:
            return x        
    # Step 0: Make sure these are floats, dammit.
    att = att + 0.0
    cmpls = cmpls + 0.0
    yds = yds + 0.0
    tds = tds + 0.0
    ints = ints + 0.0
    # Step 1: The completion percentage.
    step_1 = cmpls/att
    step_1 = step_1 - 0.3
    step_1 = step_1 * 5
    step_1 = _min_max(step_1, 0, 2.375)
    # Step 2: The yards per attempt.
    step_2 = yds/att
    step_2 = step_2 - 3
    step_2 = step_2 * 0.25
    step_2 = _min_max(step_2, 0, 2.375)
    # Step 3: Touchdown percentage.
    step_3 = tds/att
    step_3 = step_3 * 20
    step_3 = _min_max(step_3, 0, 2.375)
    
    # Step 4: Interception percentage.
    step_4 = ints/att
    step_4 = step_4 * 25
    step_4 = 2.375 - step_4
    step_4 = _min_max(step_4, 0, 2.375)
    
    # Step 5: Compute the rating based on the sum of steps 1-4.
    rating = step_1 + step_2 + step_3 + step_4 + 0.0
    rating = rating / 6
    rating = rating * 100
    
    # Step 6: Return the rating, formatted to 1 decimal place, as a Decimal.
    return rating
def get_headers(table,dictionary):
    """retrieves the headers of the table"""
    for row in table.thead.find_all('tr'):
        if "class" in  row.attrs:
            # print(row)
            if row.attrs["class"] == "over_header":
                continue
        else:
            for column in row.find_all('th'):
                attr = column.attrs["data-stat"]
                if attr in stats_ignore:
                    continue
                dictionary.setdefault(attr,[])
def get_table_row(row,dictionary):
    """retreives the data for each row of the table"""
    for cell in row.findAll('td'):
        attr = cell.attrs["data-stat"]
        if attr in stats_ignore:
            continue
        if attr not in dictionary:
            continue
        dictionary.setdefault(attr,[]).append(cell.text)
    return dictionary
def get_stat_class(key,table):
    """Gets the Correct Stats for the provided Key"""
    dictionary = {}
    get_headers(table,dictionary)
    for value in dictionary.values():
        value.append("0")
    if key == "passing":
        return Passing(dictionary)
    if key == "rushing":
        return Rushing(dictionary)
    return Receiving(dictionary)
def get_season_stats(season):
    """fills empty stat classes with zeros"""
    season_str = str(season)
    table_dict = get_stats(season)
    passing_table = table_dict["passing"]
    rushing_table = table_dict["scrimmage"]
    for player in players_array.values():
        # print(player.name)
        if season_str in player.stats:
            s_obj = player.stats[season_str]
            for key in vars(s_obj):
                if key == "passing" and s_obj.passing is None:
                    stat_class = get_stat_class(key,passing_table)
                    s_obj.passing = stat_class
                if key == "rushing" and s_obj.rushing is None:
                    stat_class = get_stat_class(key,rushing_table)
                    s_obj.rushing = stat_class
                if key == "receiving" and s_obj.receiving is None:
                    stat_class = get_stat_class(key,rushing_table)
                    s_obj.receiving = stat_class
                continue
def get_stats(year):
    """Makes html requests and creates Player and season objects returns dictionary of tables"""
    to_fetch = {"passing":"pass_att","scrimmage":"rush_att"}
    table_dict = {}
    for key,sort in to_fetch.items():
        base_url = "https://www.pro-football-reference.com"
        url = f"{base_url}/years/{year}/{key}.htm#{key}::{sort}"
        # check_limit()
        table_file = Path(f"Tables/{year}/{key}.txt")
        if not os.path.exists(Path(f"Tables/{year}")):
            os.makedirs(Path(f"Tables/{year}"))
        if table_file.is_file() and year != CURRENT_SEASON:
            with open(table_file,encoding="utf-8") as file:
                text_data = file.read()
                file.close()
        else:
            text_data = html_request(url)
            with open(table_file,"w",encoding="utf-8") as file:
                file.write(text_data)
                file.close()
        data = soup(text_data, 'html.parser')
        table = data.find('table', id=key)
        table_dict.setdefault(key,table)
        for row in table.tbody.find_all('tr'):
            dictionary = {}
            get_headers(table,dictionary)
            fetched_player = get_player(row)
            if fetched_player.pos not in POS_FILTER and len(POS_FILTER) > 0:
                continue
            new_stat = get_table_row(row,dictionary)
            if str(year) in fetched_player.stats:
                fetched_season = fetched_player.stats[str(year)]
                if key == "passing":
                    fetched_season.passing = Passing(new_stat)
                else:
                    fetched_season.rushing = Rushing(new_stat)
                    fetched_season.receiving = Receiving(new_stat)
                if fetched_season.general is None:
                    fetched_season.general = General(new_stat)
            else:
                fetched_season = Season(year)
                fetched_season.general = General(new_stat)
                if key == "passing":
                    fetched_season.passing = Passing(new_stat)
                else:
                    fetched_season.rushing = Rushing(new_stat)
                    fetched_season.receiving = Receiving(new_stat)
                player = players_array[fetched_player.id]
                player.stats.setdefault(str(year),fetched_season)
    return table_dict
def leader_stats(start_season,end_season):
    """Gets the Stats and returns a dictionary of Dataframes"""
    dataframes = {}
    x = range(start_season,end_season + 1)
    final_dictionary = {}
    season_dictionary = {}
    s_dictionary = {}
    final_list = []
    for season in x:
        print(f"Starting Season {season}")
        get_season_stats(season)
        # if end_season - start_season >= 8 and season != end_season:
        #     time.sleep(8)
    for player in players_array.values():
        list_player = get_totals(player,)
        final_list.append(list_player)

        for key in x:
            season_key = str(key)
            s_dictionary.setdefault(season_key,[])
            season_list_item = get_season_dictionary(player,season_key)
            if season_list_item is None:
                continue
            s_dictionary.setdefault(season_key,[]).append(season_list_item)
    for seasons,values in s_dictionary.items():
        season_dictionary.setdefault(seasons,{})
        sorted_list = sorted(values, key=itemgetter(stats_ref[SORT_STAT]["title"]), reverse=True)
        for player in sorted_list:
            for key,value in player.items():
                season_dictionary[seasons].setdefault(key,[]).append(value)
    new_list = sorted(final_list, key=itemgetter(stats_ref[SORT_STAT]["title"]), reverse=True)
    for player_1 in new_list:
        for key,value in player_1.items():
            final_dictionary.setdefault(key,[]).append(value)
    df = pd.DataFrame(final_dictionary)
    df.columns = pd.MultiIndex.from_tuples([tuple(c.split("☳")) for c in df.columns])
    dataframes.setdefault("Totals",df)
    for key,item in season_dictionary.items():
        s_frame = pd.DataFrame(item)
        s_frame.columns = pd.MultiIndex.from_tuples([tuple(c.split("☳")) for c in s_frame.columns])
        dataframes.setdefault(key,s_frame)
    return dataframes
def format_excel_column(book,sheet,column):
    """Formats the Columns in the Excel Sheet"""
    column_format = None
    percent = book.add_format({'num_format': '0.0%','align':'center'})
    whole = book.add_format({'num_format': '#,##0','align':'center'})
    whole_border = book.add_format({'num_format': '#,##0','align':'center','right':1})
    decimal = book.add_format({'num_format': '#,##0.00','align':'center'})
    decimal_border = book.add_format({'num_format': '#,##0.00','align':'center','right':1})
    if column["format"] == "percent":
        column_format = percent
    if column["format"] == "whole":
        column_format = whole
    if column["format"] == "whole_border":
        column_format = whole_border
    if column["format"] == "decimal":
        column_format = decimal
    if column["format"] == "decimal_border":
        column_format = decimal_border
    sheet.set_column_pixels(column["index"],column["index"],column["sizePx"],column_format)
def save_to_excel(start_season,end_season,dataframes):
    """Takes a dictionary of dataframes and saves them to a single excel sheet"""
    output_path = Path("/Users/avatara/Desktop/SportsScraping/Output")
    if len(POS_FILTER) == 0:
        file_path = output_path.joinpath(f'{start_season} to {end_season}.xlsx')
    else:
        if len(POS_FILTER) > 3:
            file_path = output_path.joinpath(f'multiple | {start_season} to {end_season}.xlsx')
        else:
            pos_str = " ".join(POS_FILTER)
            file_path = output_path.joinpath(f'{pos_str} | {start_season} to {end_season}.xlsx')
    with pd.ExcelWriter(file_path) as writer:
        workbook = writer.book
        column_ref = load_json("Utils/ColumnRef.json")
        for title,frame in dataframes.items():
            frame.to_excel(writer, sheet_name=title)
        for worksheet in writer.sheets.values():
            worksheet.freeze_panes(2, 2)    # Freeze the first row.
            for item in column_ref.values():
                format_excel_column(workbook,worksheet,item)
def get_totals(player):
    """gets totals for the player"""
    player_dict = {}
    # print(f"Getting Totals for {player.name}")
    player.totals = player.get_totals()
    # dictionary.setdefault(stats_ref["Player"]["title"],[]).append( player.name)
    # dictionary.setdefault(stats_ref["pos"]["title"],[]).append( player.pos)
    player_dict.setdefault(stats_ref["Player"]["title"],player.name)
    player_dict.setdefault(stats_ref["pos"]["title"],player.pos)
    for stats in player.totals:
        player_dict.setdefault(stats,player.totals[stats])
        # dictionary.setdefault(stats,[]).append(player.totals[stats])
    return player_dict
def get_season_dictionary(player,year):
    """gets the season dictionary"""

    if player.get_yearly(year) is None:
        return None
    else:
        player_dict = {}
        yearly = player.get_yearly(year)
        player_dict.setdefault(stats_ref["Player"]["title"],player.name)
        player_dict.setdefault(stats_ref["pos"]["title"],player.pos)
        for stats in yearly:
            player_dict.setdefault(stats,yearly[stats])
        return player_dict
def run_program(start_season,end_season):
    """Run the Program"""
    dataframes = leader_stats(start_season,end_season)
    save_to_excel(start_season,end_season,dataframes)

    print("done")

# def Test():
#     ## Test code Here
#     print("Test")

run_program(START_SEASON,END_SEASON)

# if __name__ == "__main__":
#   num1 = sys.argv[1]
#   num2 = sys.argv[2]
#   run_program(int(num1),int(num2))
