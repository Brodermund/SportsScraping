"""Module providing a function printing python version."""
# import sys
import time
import json
from pathlib import Path
from ratelimit import limits, sleep_and_retry
from bs4 import BeautifulSoup as soup
import requests
import pandas as pd
MIN_PYTHON = (3, 10)
# if sys.version_info < MIN_PYTHON:
#     sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

START_SEASON = 2018
END_SEASON = 2024
CALLS = 20
RATE_LIMIT = 60
players_array = {}

@sleep_and_retry
@limits(calls=CALLS, period=RATE_LIMIT)
def check_limit():
    """Empty function just to check for calls to API"""
    return
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
    def __init__(self,dictionary):
        self.rush_att = dictionary["rush_att"]
        self.rush_yds = dictionary["rush_yds"]
        self.rush_td = dictionary["rush_td"]
        self.rush_first_down = dictionary["rush_first_down"]
        self.rush_long = dictionary["rush_long"]
        self.rush_yds_per_att = dictionary["rush_yds_per_att"]
        self.rush_yds_per_g = dictionary["rush_yds_per_g"]
        self.rush_att_per_g = dictionary["rush_att_per_g"]
        self.fumbles = dictionary["fumbles"]
class Receiving:
    """Class Representing a Players Receiving Stats for a Statstical Season"""
    def __init__(self,dictionary):
        self.targets = dictionary["targets"]
        self.rec = dictionary["rec"]
        self.rec_yds = dictionary["rec_yds"]
        self.rec_yds_per_rec = dictionary["rec_yds_per_rec"]
        self.rec_td = dictionary["rec_td"]
        self.rec_first_down = dictionary["rec_first_down"]
        self.rec_long = dictionary["rec_long"]
        self.rec_per_g = dictionary["rec_per_g"]
        self.rec_yds_per_g = dictionary["rec_yds_per_g"]
        self.catch_pct = dictionary["catch_pct"]
        self.rec_yds_per_tgt = dictionary["rec_yds_per_tgt"]
class Passing:
    """Class Representing a Players Passing Stats for a Statstical Season"""
    def __init__(self,dictionary):
        self.pass_cmp = dictionary["pass_cmp"]
        self.pass_att = dictionary["pass_att"]
        self.qb_rec = dictionary["qb_rec"]
        self.pass_cmp_pct = dictionary["pass_cmp_pct"]
        self.pass_yds = dictionary["pass_yds"]
        self.pass_td = dictionary["pass_td"]
        self.pass_td_pct = dictionary["pass_td_pct"]
        self.pass_int = dictionary["pass_int"]
        self.pass_int_pct = dictionary["pass_int_pct"]
        self.pass_first_down = dictionary["pass_first_down"]
        self.pass_long = dictionary["pass_long"]
        self.pass_yds_per_att = dictionary["pass_yds_per_att"]
        self.pass_adj_yds_per_att = dictionary["pass_adj_yds_per_att"]
        self.pass_yds_per_cmp = dictionary["pass_yds_per_cmp"]
        self.pass_yds_per_g = dictionary["pass_yds_per_g"]
        self.pass_rating = dictionary["pass_rating"]
        self.pass_sacked = dictionary["pass_sacked"]
        self.pass_sacked_yds = dictionary["pass_sacked_yds"]
        self.pass_sacked_pct = dictionary["pass_sacked_pct"]
        self.pass_net_yds_per_att = dictionary["pass_net_yds_per_att"]
        self.pass_adj_net_yds_per_att = dictionary["pass_adj_net_yds_per_att"]
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
            fin_dict.setdefault(stats_ref[key]["title"],[]).append(cal)
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
                fin_dict.setdefault(stats_ref[key]["title"],[]).append(cal)
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
    players_array.setdefault(player_id,player)
    return player
def _sum(arr):
    sum_var = 0
    for i in arr:
        sum_var = sum_var + int(i)
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
    if att < 10:
        return 0
    e = (cmp/att - 0.3) * 5
    f = (yds/att - 3) * 0.25
    g = (td/att) * 20
    h = 2.375 - (interceptions/att * 25)

    a = 0 if e <0 else e if e <2.375 else 2.375
    b = 0 if f <0 else f if f <2.375 else 2.375
    c = 0 if g <0 else g if g <2.375 else 2.375
    d = 0 if h <0 else h if h <2.375 else 2.375
    rate = ((a + b + c + d)/6) * 100
    return rate
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
        check_limit()
        data = soup(requests.get(url,timeout=10).text, 'html.parser')
        table = data.find('table', id=key)
        table_dict.setdefault(key,table)
        for row in table.tbody.find_all('tr'):
            dictionary = {}
            get_headers(table,dictionary)
            fetched_player = get_player(row)
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
    for season in x:
        print(f"Starting Season {season}")
        get_season_stats(season)
        if end_season - start_season >= 8 and season != end_season:
            time.sleep(8)
    for player in players_array.values():
        get_totals(player,final_dictionary)
        for key in player.stats:
            get_season_dictionary(player,key,season_dictionary)
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
    file_path = output_path.joinpath(f'{start_season} to {end_season}.xlsx')
    with pd.ExcelWriter(file_path) as writer:
        workbook = writer.book
        column_ref = load_json("Utils/ColumnRef.json")
        for title,frame in dataframes.items():
            frame.to_excel(writer, sheet_name=title)
        for worksheet in writer.sheets.values():
            worksheet.freeze_panes(2, 2)    # Freeze the first row.
            for item in column_ref.values():
                format_excel_column(workbook,worksheet,item)
def get_totals(player,dictionary):
    """gets totals for the player"""
    # print(f"Getting Totals for {player.name}")
    player.totals = player.get_totals()
    dictionary.setdefault(stats_ref["Player"]["title"],[]).append( player.name)
    dictionary.setdefault(stats_ref["pos"]["title"],[]).append( player.pos)
    for stats in player.totals:
        dictionary.setdefault(stats,[]).append(player.totals[stats][0])
def get_season_dictionary(player,year,dictionary):
    """gets the season dictionary"""
    if player.get_yearly(year) is None:
        pass
    else:
        dictionary.setdefault(str(year),dict())
        yearly = player.get_yearly(year)
        dictionary[str(year)].setdefault(stats_ref["Player"]["title"],[]).append( player.name)
        dictionary[str(year)].setdefault(stats_ref["pos"]["title"],[]).append( player.pos)
        for stats in yearly:
            dictionary[str(year)].setdefault(stats,[]).append(yearly[stats][0])
def run_program(start_season,end_season):
    """Run the Program"""
    dataframes = leader_stats(start_season,end_season)
    save_to_excel(start_season,end_season,dataframes)


            # worksheet.set_column_pixels(0, 0, 30, standard)
            # worksheet.set_column_pixels(1, 1, 175, standard)
            # worksheet.set_column_pixels(2, 3, 45, standard)
            # worksheet.set_column_pixels(4, 4, 45, rightborder)
            # worksheet.set_column_pixels(5, 6, 60, standard)
            # worksheet.set_column_pixels(7, 7, 60, percent)
            # worksheet.set_column_pixels(8, 9, 60, standard)
            # worksheet.set_column_pixels(10, 10, 60, percent)
            # worksheet.set_column_pixels(11, 11, 60, standard)
            # worksheet.set_column_pixels(12, 12, 60, percent)
            # worksheet.set_column_pixels(13, 21, 60, standard)
            # worksheet.set_column_pixels(22, 22, 60, percent)
            # worksheet.set_column_pixels(23, 23, 60, standard)
            # worksheet.set_column_pixels(24, 24, 60, rightborder)
            # worksheet.set_column_pixels(25, 31, 60, standard)
            # worksheet.set_column_pixels(32, 33, 60, rightborder)
            # worksheet.set_column_pixels(34, 42, 60, standard)
            # worksheet.set_column_pixels(43, 43, 60, percent)
            # worksheet.set_column_pixels(44, 44, 60, standard)
    print("done")

# def Test():
#     ## Test code Here
#     print("Test")

run_program(START_SEASON,END_SEASON)

# if __name__ == "__main__":
#   num1 = sys.argv[1]
#   num2 = sys.argv[2]
#   run_program(int(num1),int(num2))
