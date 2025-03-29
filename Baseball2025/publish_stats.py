#/usr/bin/env/python3

# auto run on pi from /etc/rc.local

import json
import os
import random
import sys
import time
import uuid

from datetime import datetime
from datetime import timedelta
from ftplib import FTP
from lxml import html

import requests

session_id = uuid.uuid1()
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",

    'Cache-Control': 'private, max-age=0, no-cache',
    "Pragma": "no-cache",
    "Expires": "Thu, 01 Jan 1970 00:00:00 GMT",
    "SessionId": str(session_id),
	"Accept-Encoding": "gzip, deflate, br",
	"Host": "httpbin.org",
	"Sec-Ch-Ua-Mobile": "?0",
	"Sec-Fetch-Dest": "document",
	"Sec-Fetch-Mode": "navigate",
	"Sec-Fetch-Site": "none",
	"Sec-Fetch-User": "?1"
}

time.sleep(1)

script_path = os.path.dirname(os.path.realpath(__file__))

DAYS = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}

TEST = False
RUN_ON_SCHEDULE = False
SLEEP_TIME = 0

DATA_FILE_PATH = os.path.join(script_path, 'data')

BASE_PITCHER_STATS = {'SV': 0, 'IP': 0.0, 'ER': 0, 'WAR': 0.0, 'ERA': 0.00, "GS": 0, "W": 0}
BASE_HITTER_STATS = {'HR': 0.0, 'OPS': 0.0, 'WAR': 0.0, 'SB': 0}

HANS = 'Hans'
GREGORY = 'Gregory'
PAUL = "Paul"

# baseball reference keys
player_br = {
    "Julio Rodriguez": {"Team": GREGORY, "Pick": 1, 'Fragment': "rodriju01.shtml", 'type': "batting"},
    "Bryce Miller": {"Team": GREGORY, "Pick": 6, 'Fragment': "millebr04.shtml", 'type': "pitching"},
    "Luke Raley": {"Team": GREGORY, "Pick": 7, 'Fragment': "raleylu01.shtml", 'type': "batting"},
    "Bryan Woo": {"Team": GREGORY, "Pick": 12, 'Fragment': "woobr01.shtml", 'type': "pitching"},
    "Andres Munoz": {"Team": GREGORY, "Pick": 13, 'Fragment': "munozan01.shtml", 'type': "pitching"},
    "Donovan Solano": {"Team": GREGORY, "Pick": 18, 'Fragment': "solando01.shtml", 'type': "batting"},
    "Austin Shenton": {"Team": GREGORY, "Pick": 19, 'Fragment': "shentau01.shtml", 'type': "batting"},
    "Matt Brash": {"Team": GREGORY, "Pick": 24, 'Fragment': "brashma01.shtml", 'type': "pitching"},

    "Cal Raleigh": {"Team": HANS, "Pick": 2, 'Fragment': "raleica01.shtml", 'type': "batting"},
    "Logan Gilbert": {"Team": HANS, "Pick": 5, 'Fragment': "gilbelo01.shtml", 'type': "pitching"},
    "J.P. Crawford": {"Team": HANS, "Pick": 8, 'Fragment': "crawfjp01.shtml", 'type': "batting"},
    "Randy Arozarena": {"Team": HANS, "Pick": 11, 'Fragment': "arozara01.shtml", 'type': "batting"},
    "Ryan Bliss": {"Team": HANS, "Pick": 14, 'Fragment': "blissry01.shtml", 'type': "batting"},
    "Rowdy Tellez": {"Team": HANS, "Pick": 17, 'Fragment': "tellero01.shtml", 'type': "batting"},
    "Cole Young": {"Team": HANS, "Pick": 20, 'Fragment': "youngco01.shtml", 'type': "batting"},
    "Gregory Santos": {"Team": HANS, "Pick": 23, 'Fragment': "santogr01.shtml", 'type': "pitching"},

    "George Kirby": {"Team": PAUL, "Pick": 3, 'Fragment': "kirbyge01.shtml", 'type': "pitching"},
    "Victor Robles": {"Team": PAUL, "Pick": 4, 'Fragment': "roblevi01.shtml", 'type': "batting"},
    "Dylan Moore": {"Team": PAUL, "Pick": 9, 'Fragment': "mooredy01.shtml", 'type': "batting"},
    "Luis Castillo": {"Team": PAUL, "Pick": 10, 'Fragment': "castilu02.shtml", 'type': "pitching"},
    "Jorge Polanco": {"Team": PAUL, "Pick": 15, 'Fragment': "polanjo01.shtml", 'type': "batting"},
    "Trent Thornton": {"Team": PAUL, "Pick": 16, 'Fragment': "thorntr01.shtml", 'type': "pitching"},
    "Harry Ford": {"Team": PAUL, "Pick": 21, 'Fragment': "fordha01.shtml", 'type': "batting"},
    "Eduard Bazardo": {"Team": PAUL, "Pick": 22, 'Fragment': "bazared01.shtml", 'type': "pitching"},

    "Mitch Garver": {'Fragment': "garvemi01.shtml", 'type': "batting"},
}

teams = {
    GREGORY: [],
    HANS: [],
    PAUL: []
}


def accumulate_group_stat(item, stats):
    local_name = item["Stat"]
    guys = item["Guys"]
    total = 0
    tool_tip = ''
    sorted_guys = sorted(guys, key=lambda x: -stats[x][local_name])
    for guy in sorted_guys:
        stat = stats[guy][local_name]
        total = total + stat
        if stat > 0:
            tool_tip = "{}&#10;{}: {}".format(tool_tip, guy, my_round(stat, 0))

    return total, tool_tip


def get_mariners_no_hit():
    site = 'https://www.nonohitters.com/no-hitters-against-the-seattle-mariners/'
    xpath = 'count(//table[@class="nonolist"]/tbody/tr/th[number(text())>0])'
    page = requests.get(site, headers)
    tree = html.fromstring(page.text)
    value = tree.xpath(xpath)

    return value - 5


def get_pitcher_count():
    mariners_team_pitching_site = 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=br&url=%2Fteams%2FSEA%2F2023.shtml&div=div_team_pitching'
    mariners_pitcher_count_xpath = "count(//table[@id='team_pitching']//tr[number(td[@data-stat='IP']/text()) > 0])"
    site = mariners_team_pitching_site
    page = requests.get(site, headers)
    tree = html.fromstring(page.text)
    value = tree.xpath(mariners_pitcher_count_xpath) - 2

    return value


def get_stat_dict():
    stat_dict = {'Mariners': {}}

    print("Construct Team")
    for player in player_br:
        if "Team" in player_br[player]:
            team = player_br[player]["Team"]
            pick = player_br[player]["Pick"]
            teams[team].append((pick, player))

    print("Extracting batting stats")
    page = None
    with open(os.path.join(script_path, 'hitting.txt'), "r") as text_file:
        page = text_file.read()

    start_index = page.index('{"app":')
    end_index = page.index('"user":{}}') + 10
    stats_json = page[start_index:end_index]

    y = json.loads(stats_json)

    # in this thing teamStats has runsScored and runsAllowed
    # playerStats has everything else that we currently want
    batting_stats = y['page']['content']['stats']
    team_stats = batting_stats['teamStats']['team'][0]['stats']

    for stat in team_stats:
        if stat['name'] == 'runs':
            stat_dict['Mariners']['RunsScored'] = int(stat['displayValue'])
        if stat['name'] == 'stolenBases':
            stat_dict['Mariners']['TeamSteals'] = int(stat['displayValue'])

    opponent_stats = batting_stats['teamStats']['opponent'][0]['stats']
    for stat in opponent_stats:
        if stat['name'] == 'runs':
            stat_dict['Mariners']['RunsAllowed'] = int(stat['displayValue'])

    player_stats = batting_stats['playerStats'][0]

    stat_dict['Mariners']['PositionPlayersUsed'] = []
    collect_batting = ['homeRuns', 'OPS', 'WARBR', 'stolenBases']
    for player in player_stats:
        name = player['athlete']['name']
        gp = my_round(float(player['statGroups']['stats'][0]['displayValue']), 3)
        if gp > 0:
            stat_dict['Mariners']['PositionPlayersUsed'].append(name)
        if name in player_br:
            this_player_stats = {}
            stat_dict[name] = this_player_stats
            for stat in player['statGroups']['stats']:
                if stat['name'] in collect_batting:
                    this_player_stats[stat['abbreviation']] = my_round(float(stat['displayValue']), 3)

    time.sleep(SLEEP_TIME)

    print("Extracting pitching stats")
    page = None
    with open(os.path.join(script_path, 'pitching.txt'), "r") as text_file:
        page = text_file.read()

    start_index = page.index('{"app":')
    end_index = page.index('"user":{}}') + 10
    stats_json = page[start_index:end_index]

    y = json.loads(stats_json)
    pitching_stats = y['page']['content']['stats']
    player_stats = pitching_stats['playerStats'][0]

    collect_pitching = ['saves', 'innings', 'earnedRuns', 'WARBR', 'ERA', "gamesStarted", "wins"]
    for player in player_stats:
        if player['athlete']['shortName'] != 'D. Castillo' and player['athlete']['shortName'] != 'T. Miller' and player['athlete']['shortName'] != 'M. Ford':
            name = player['athlete']['shortName'][player['athlete']['shortName'].index(' ') + 1:]
            if name in player_br:
                player_br[name]["Name"] = player['athlete']['shortName']

                this_player_stats = {}
                if name in stat_dict:
                    this_player_stats = stat_dict[name]
                stat_dict[name] = this_player_stats
                for stat in player['statGroups']['stats']:
                    if stat['name'] in collect_pitching:
                        abbr = stat['abbreviation'];
                        if abbr in this_player_stats:
                            this_player_stats[abbr] = my_round( float(stat['displayValue']) + this_player_stats[abbr], 3)
                        else:
                            this_player_stats[abbr] = float(stat['displayValue'])

    print("Extracting data from splits")
    page = None
    with open(os.path.join(script_path, 'splits.txt'), "r") as text_file:
        page = text_file.read()

    start_index = page.index('{"app":')
    end_index = page.index('"user":{}}') + 10
    stats_json = page[start_index:end_index]

    y = json.loads(stats_json)
    group_tables = y["page"]["content"]["splits"]["teamStats"][0]["groupTables"]
    batting_stats_by_position = group_tables[5]

    headings = batting_stats_by_position['headings']
    heading_indexes = {}
    heading_index = 0
    for heading in headings:
        heading_indexes[heading['abbreviation']] = heading_index
        heading_index = heading_index + 1
    print(heading_indexes)
    by_position_rows = batting_stats_by_position['rows']

    rows_we_want = ["As 1B", "As 2B", "As 3B", "As SS", "As DH"]
    stat_dict['Mariners']['HomeRuns'] = {}
    stat_dict['Mariners']['HomeRuns']['ByPosition'] = {}
    for row in by_position_rows:
        if row[0] in rows_we_want:
            stat_dict['Mariners']['HomeRuns']['ByPosition'][row[0]] = {"HR": my_round(row[heading_indexes["HR"]], 0)}
    print(stat_dict['Mariners']['HomeRuns']['ByPosition'])

    # look up record from espn standings page
    print("Extracting stats from standings")
    time.sleep(SLEEP_TIME)
    page = None
    with open(os.path.join(script_path, 'standings.txt'), "r") as text_file:
        page = text_file.read()

    start_index = page.index('{"app":')
    end_index = page.index('"user":{}}') + 10
    stats_json = page[start_index:end_index]
    y = json.loads(stats_json)

    standings_json = y['page']['content']['standings']['groups']
    index = 0
    losses_index = -1
    wins_index = -1
    playoffseed_index = -1
    for header in standings_json['headers']:
        if header == 'losses':
            losses_index = index
        elif header == 'wins':
            wins_index = index
        elif header == 'playoffseed':
            playoffseed_index = index
        index = index + 1

    for group in standings_json['groups']:
        if group['name'] == 'American League':
            for division in group['children']:
                if division['name'] == 'West':
                    for place in division['standings']:
                        if place['team']['abbrev'] == 'SEA':
                            stat_dict['Mariners']['Wins'] = int(place['stats'][wins_index])
                            stat_dict['Mariners']['Losses'] = int(place['stats'][losses_index])
                            stat_dict['Mariners']['PlayoffSeed'] = int(place['stats'][playoffseed_index])

    for player in player_br:
        if player not in stat_dict:
            if player_br[player]['type'] == 'batting':
                stat_dict[player] = BASE_HITTER_STATS
            elif player_br[player]['type'] == 'pitching':
                stat_dict[player] = BASE_PITCHER_STATS

    # look up next game from espn team schedule page
    print("Extracting schedule json")
    time.sleep(SLEEP_TIME)
    page = None
    with open(os.path.join(script_path, 'schedule.txt'), "r") as text_file:
        page = text_file.read()

    start_index = page.index('{"app":')
    end_index = page.index('"user":{}}') + 10
    stats_json = page[start_index:end_index]
    y = json.loads(stats_json)

    stat_dict['Mariners']['NextGame'] = {"Opponent": "None", "Time": "", "GameCast": "None"}
    if stat_dict['Mariners']['Wins'] + stat_dict['Mariners']['Losses'] < 162:
        thing = y['page']['content']['scheduleData']['teamSchedule'][0]['events']['pre'][0]['group'][0]
        stat_dict['Mariners']['NextGame']['Opponent'] = thing['opponent']['displayName']
        stat_dict['Mariners']['NextGame']['Time'] = thing['time']['time']
        stat_dict['Mariners']['NextGame']['GameCast'] = thing['time']['link']

    return stat_dict


def my_round(value, places):
    if places == 0:
        return int(value)
    else:
        return round(float(value)*10**places)/10**places


def calculate_linear(item, games_played, offset=0):
    if games_played == 0:
        item["Projected"] = item["Current"]
    else:
        projected = (item["Current"] - offset) * 162 / games_played + offset
        if projected < offset:
            projected = offset
        item["Projected"] = projected


def calculate_copy_current(item, games_played):
    item["Projected"] = item["Current"]


def calculate_manual_list(stats, item):
    item["Current"] = len(item["Guys"])
    item["ToolTip"] = "&#10;".join(item["Guys"])


def calculate_accumulation(stats, item):
    total, tip = accumulate_group_stat(item, stats)
    item["Current"] = total
    item["ToolTip"] = tip


def calculate_negative_war(stats, item):
    result = 0
    for team in teams:
        for player in teams[team]:
            if stats[player[1]]["WAR"] < 0:
                result += 1

    item["Current"] = result


def calculate_infield_home_runs(stats, item):
    infield_homeruns, tool_tip = accumulate_group_stat(item, stats['Mariners']['HomeRuns']['ByPosition'])
    item["Current"] = infield_homeruns
    item["ToolTip"] = tool_tip


def maybe_bold(over_under, names, value, target):
    if over_under == "Under" and value < target:
        return "<b>" + ", ".join(names) + "</b>"
    elif over_under == "Over" and value > target:
        return "<b>" + ", ".join(names) + "</b>"
    else:
        return ", ".join(names)


def get_team_tables(new_stats, old_stats):
    print("Create Team Tables")
    team_tables = []
    team_number = 0
    for team in teams:
        team_number = team_number + 1
        total_war = 0
        table = "<div style='grid-column: {}; grid-row: 1;'><p class='team-text'>Team {}</p>\r\n<table class='team_table'>\r\n\t<thead><tr>\r\n\t\t<td>Pick</td>\r\n\t\t<td>Name</td>\r\n\t\t<td>WAR</td>\r\n\t\t<td></td>\r\n\t</tr></thead>".format(str(team_number), team)
        high_war = -10
        for player_stuff in teams[team]:
            player_key = player_stuff[1]
            war = new_stats[player_key]["WAR"]
            if war > high_war:
                high_war = war
        for player_stuff in teams[team]:
            draft = player_stuff[0]
            player_key = player_stuff[1]
            fragment = player_br[player_key]['Fragment']
            war = new_stats[player_key]["WAR"]
            try:
                old_war = old_stats[player_key]["WAR"]
            except Exception as e:
                old_war = 0
            total_war = total_war + war
            war_delta = war - old_war
            war_delta_text = "" if war_delta == 0 else "({:.1f})".format(war_delta)
            war_column_class = "normal"
            if war == high_war:
                war_column_class = "bold"
            player_html = "<a target='_blank' href='https://www.baseball-reference.com/players/{}/{}'>{}</a>".format(fragment[0].lower(), fragment, player_key)
            row = "\r\n\t<tr>\r\n\t\t<td>{}</td>\r\n\t\t<td>{}</td>\r\n\t\t<td class='{}' align='right'>{:.1f}</td><td>{}</td>\r\n\t</tr>".format(draft, player_html, war_column_class, war, war_delta_text)
            table = table + row

        new_stats["Mariners"][team] = {"TeamWAR": my_round(total_war, 2), "Points": 0.0, "PointContributors": []}
        war_delta = total_war - old_stats["Mariners"][team]["TeamWAR"]
        war_delta_text = "" if war_delta == 0 else "({:.1f})".format(war_delta)
        table = table + "</table>\r\n<p/>Total War: {:.1f} {}<p/></div>".format(total_war, war_delta_text)
        team_tables.append(table)

    return "<p/>".join(team_tables)


def get_projected_record_table(stats):
    print("Create Projected Record table")
    pythagorean_power = 1.83

    # lookup wins/losses
    wins = stats["Mariners"]["Wins"]
    losses = stats["Mariners"]["Losses"]

    # lookup runs scored/allowed
    runs_scored = stats["Mariners"]["RunsScored"]
    runs_allowed = stats["Mariners"]["RunsAllowed"]
    pythagorean_percent = runs_scored**pythagorean_power/(runs_scored**pythagorean_power + runs_allowed**pythagorean_power)
    projected_wins = wins + pythagorean_percent*(162-wins-losses)
    stats["Mariners"]["ProjectedWins"] = projected_wins
    return "<table class='team_table'>\r\n<tr>" \
           "<td>Wins</td>" \
           "<td>Losses</td>" \
           "<td>Runs Scored</td>" \
           "<td>Runs Allowed</td>" \
           "<td>Pythagorean Win %</td>" \
           "<td>Projected Wins</td>" \
           "</tr>\r\n<tr>" \
           "<td>{:.0f}</td>" \
           "<td>{:.0f}</td>" \
           "<td>{:.0f}</td>" \
           "<td>{:.0f}</td>" \
           "<td>{:.1f}%</td>" \
           "<td>{:.1f}</td><" \
           "/tr>\r\n</table>".format(wins, losses, runs_scored, runs_allowed, 100*pythagorean_percent, projected_wins)


def convert_innings_pitched(standard_ip):
    truncated = my_round(standard_ip, 0)
    outs = standard_ip - truncated
    return truncated + 10 * outs / 3


def add_points(stats, names, thing, points):
    if isinstance(names, str):
        names = [names]
    for name in names:
        stats["Mariners"][name]["Points"] = stats["Mariners"][name]["Points"] + points
        if points != 0:
            stats["Mariners"][name]["PointContributors"].append((thing, points))


def get_over_under_table(stats):
    print("Create Over/Under table")
    over_unders = {
        "OldHomers": {
            "Title": "Homers by Old Guys",
            "Value": 110.5,
            "Over": [GREGORY],
            "Under": [HANS, PAUL],
            "Rounding": (0, 1),
            "Guys": ["Jorge Polanco", "Dylan Moore", "Luke Raley", "Donovan Solano", "J.P. Crawford", "Randy Arozarena", "Rowdy Tellez", "Mitch Garver"],
            "Points": 1,
            "Stat": "HR",
            "Calculation": calculate_accumulation,
            "Projection": calculate_linear
        },
        "RodriguezOPS": {
            "Title": "Rodriguez OPS",
            "Value": 0.800,
            "Over": [GREGORY],
            "Under": [HANS, PAUL],
            "Rounding": (3, 3),
            "Points": 1,
            "Guys": ["Julio Rodriguez"],
            "Stat": "OPS",
            "Calculation": calculate_accumulation,
            "Projection": calculate_copy_current
        },
        "Wins": {
            "Title": "Wins",
            "Value": 85.5,
            "Over": [GREGORY, PAUL],
            "Under": [HANS],
            "Rounding": (0, 1),
            "Points": 2
        },
        "NegativeWAR": {
            "Title": "# With Negative WAR",
            "Value": 4.5,
            "Over": [HANS],
            "Under": [GREGORY, PAUL],
            "Rounding": (0, 1),
            "Points": 1,
            "Calculation": calculate_negative_war,
            "Projection": calculate_copy_current
        },
        "FourYoungPitcherWins": {
            "Title": "4 Young Pitcher Wins",
            "Value": 43.5,
            "Over": [HANS, PAUL],
            "Under": [GREGORY],
            "Rounding": (0, 1),
            "Points": 1,
            "Guys": ["Logan Gilbert", "Bryan Woo", "Bryce Miller", "George Kirby"],
            "Stat": "W",
            "Calculation": calculate_accumulation,
            "Projection": calculate_linear
        },
        "AllStars": {
            "Title": "All Stars",
            "Value": 2.5,
            "Over": [HANS],
            "Under": [GREGORY, PAUL],
            "Rounding": (0, 0),
            "Points": 1,
            "Guys": [],
            "Calculation": calculate_manual_list,
            "Projection": calculate_copy_current
        },
        "Released": {
            "Title": "Released/DFAed",
            "Value": 7.5,
            "Over": [HANS, PAUL],
            "Under": [GREGORY],
            "Rounding": (0, 1),
            "Points": 1,
            "Guys": ["Mitch Haniger"],
            "Calculation": calculate_manual_list,
            "Projection": calculate_linear,
            "ProjectionOffset": 5
        },
        "InfieldHomeRuns": {
            "Title": "Home Runs by the Infield",
            "Value": 88.5,
            "Over": [PAUL],
            "Under": [GREGORY, HANS],
            "Rounding": (0, 1),
            "Points": 1,
            "Guys": ["As 1B", "As 2B", "As 3B", "As SS", "As DH"],
            "Stat": "HR",
            "Calculation": calculate_infield_home_runs,
            "Projection": calculate_linear
        },
        "PositionPlayersUsed": {
            "Title": "Position Players Used",
            "Value": 24.5,
            "Under": [HANS],
            "Over": [GREGORY, PAUL],
            "Rounding": (0, 1),
            "Points": 1,
            "Guys": stats['Mariners']['PositionPlayersUsed'],
            "Calculation": calculate_manual_list,
            "Projection": calculate_linear,
            "ProjectionOffset": 14
        }
    }

    wins = stats["Mariners"]["Wins"]
    losses = stats["Mariners"]["Losses"]

    over_unders["Wins"]["Current"] = stats["Mariners"]["Wins"]
    over_unders["Wins"]["Projected"] = stats["Mariners"]["ProjectedWins"]

    row_template = "<td>{}</td><td>{}</td><td>{}</td><td>{}</td><td {}>{num1:.{places1}f}</td><td>{num2:.{places2}f}</td>"
    rows = []
    for over_under in over_unders:
        item = over_unders[over_under]

        if "Calculation" in item:
            item["Calculation"](stats, item)
        if "Projection" in item:
            if "ProjectionOffset" in item:
                item["Projection"](item, wins + losses, item["ProjectionOffset"])
            else:
                item["Projection"](item, wins + losses)

        tool_tip = ''
        if 'ToolTip' in item:
            tool_tip = 'title="{}"'.format(item['ToolTip'])

        rounding = item["Rounding"]
        row = row_template
        row = row.format(item["Title"], item["Value"],
                         maybe_bold("Over", item["Over"], item["Projected"], item["Value"]),
                         maybe_bold("Under", item["Under"], item["Projected"], item["Value"]),
                         tool_tip,
                         num1=item["Current"], places1=rounding[0], num2=item["Projected"], places2=rounding[1])
        rows.append(row)

    return over_unders, "<tr>" + "</tr>\r\n<tr>".join(rows) + "</tr>"


def get_other_table(stats):
    print("Create Other table")
    others = {
        "MakePlayoffs":{
            "Title": "Make the playoffs",
            "Yes": [HANS],
            "No": [PAUL, GREGORY],
            "Points": 0
        },
        "BestTeam": {
            "Title": "Team WAR"
        },
        "BestPlayer": {
            "Title": "Best Player WAR",
            "Points": 0
        },
        "WorstPlayer": {
            "Title": "Worst Player WAR",
            "Points": -1
        }
    }

    # Team WAR
    to_sort = [{"Name": x, "TeamWAR": stats["Mariners"][x]["TeamWAR"]} for x in teams.keys()]

    sorted_teams = sorted(to_sort, key=lambda x: x["TeamWAR"])

    if stats["Mariners"][HANS]["TeamWAR"] == stats["Mariners"][GREGORY]["TeamWAR"] and stats["Mariners"][GREGORY]["TeamWAR"] == stats["Mariners"][PAUL]["TeamWAR"]:
        # all three are tied
        others["BestTeam"]["Best"] = ", ".join(["Team " + x["Name"] for x in sorted_teams])
        others["BestTeam"]["Relevant"] = "{:.1f} WAR".format(sorted_teams[0]["TeamWAR"])
        others["BestTeam"]["Winner"] = ", ".join([x["Name"] for x in sorted_teams])
        add_points(stats, [x["Name"] for x in sorted_teams], "BestTeam", 4/3)
    elif sorted_teams[0]["TeamWAR"] == sorted_teams[1]["TeamWAR"]:
        # last two are tied
        others["BestTeam"]["Best"] = ", ".join(["Team " + x["Name"] for x in sorted_teams[0:2]])
        others["BestTeam"]["Relevant"] = "{:.1f} WAR".format(sorted_teams[2]["TeamWAR"])
        others["BestTeam"]["Winner"] = sorted_teams[-1]["Name"]
        add_points(stats, [sorted_teams[0]["Name"], sorted_teams[1]["Name"]], "BestTeam", 0.5)
        add_points(stats, sorted_teams[2]["Name"], "BestTeam", 3)
    elif sorted_teams[1]["TeamWAR"] == sorted_teams[2]["TeamWAR"]:
        # first two are tied
        others["BestTeam"]["Best"] = ", ".join(["Team " + x["Name"] for x in sorted_teams[1:2]])
        others["BestTeam"]["Relevant"] = "{:.1f} WAR".format(sorted_teams[2]["TeamWAR"])
        others["BestTeam"]["Winner"] = ", ".join([x["Name"] for x in sorted_teams[1:2]])
        add_points(stats, sorted_teams[0]["Name"], "BestTeam", 0)
        add_points(stats, [sorted_teams[1]["Name"], sorted_teams[2]["Name"]], "BestTeam", 2)
    else:
        others["BestTeam"]["Best"] = "Team " + sorted_teams[-1]["Name"];
        others["BestTeam"]["Relevant"] = "{:.1f} WAR".format(sorted_teams[2]["TeamWAR"])
        others["BestTeam"]["Winner"] = sorted_teams[-1]["Name"]
        add_points(stats, sorted_teams[0]["Name"], "BestTeam", 0)
        add_points(stats, sorted_teams[1]["Name"], "BestTeam", 1)
        add_points(stats, sorted_teams[2]["Name"], "BestTeam", 3)

    # Best Player(s)
    global_high_war = -10
    global_low_war = 100
    best_players = []
    worst_players = []
    best_player_winners = []
    worst_player_losers = []
    for team in teams:
        for player in teams[team]:
            if stats[player[1]]["WAR"] > global_high_war:
                best_players = [player[1]]
                global_high_war = stats[player[1]]["WAR"]
                best_player_winners = [team]
            elif stats[player[1]]["WAR"] == global_high_war:
                best_players.append(player[1])
                if team not in best_player_winners:
                    best_player_winners.append(team)

            if stats[player[1]]["WAR"] < global_low_war:
                worst_players = [player[1]]
                global_low_war = stats[player[1]]["WAR"]
                worst_player_losers = [team]
            elif stats[player[1]]["WAR"] == global_low_war:
                worst_players.append(player[1])
                if team not in worst_player_losers:
                    worst_player_losers.append(team)

    others["BestPlayer"]["Best"] = ", ".join(best_players)
    others["BestPlayer"]["Relevant"] = "{:.1f} WAR".format(global_high_war)
    others["BestPlayer"]["Winner"] = ", ".join(best_player_winners)

    others["WorstPlayer"]["Best"] = ", ".join(worst_players)
    others["WorstPlayer"]["Relevant"] = "{:.1f} WAR".format(global_low_war)
    others["WorstPlayer"]["Winner"] = ", ".join(worst_player_losers)
    add_points(stats, worst_player_losers, "WorstPlayer", -1/len(worst_player_losers))

    others["MakePlayoffs"]["Relevant"] = "Current Playoff Seed = {}".format(stats["Mariners"]["PlayoffSeed"])
    if stats["Mariners"]["PlayoffSeed"] <= 6:
        others["MakePlayoffs"]["Best"] = "Yes"
        others["MakePlayoffs"]["Winner"] = ""
    else:
        others["MakePlayoffs"]["Best"] = "No"
        others["MakePlayoffs"]["Winner"] = ", ".join([GREGORY, HANS, PAUL])
        add_points(stats, [GREGORY, HANS, PAUL], "MakePlayoffs", 0)

    row_template = "<td>{}</td><td>{}</td><td>{}</td><td class='bold'>{}</td>"
    rows = []
    for other in others:
        item = others[other]
        row = row_template
        row = row.format(item["Title"], item["Best"], item["Relevant"], item["Winner"])
        rows.append(row)

    return others, "<tr>" + "</tr>\r\n<tr>".join(rows) + "</tr>"


def calculate_scores(stats, over_unders, others):
    print("Calculate Scores")
    for item in over_unders:
        points = over_unders[item]["Points"]
        if over_unders[item]["Projected"] <= over_unders[item]["Value"]:
            add_points(stats, over_unders[item]["Under"], item, points)
        if over_unders[item]["Projected"] >= over_unders[item]["Value"]:
            add_points(stats, over_unders[item]["Over"], item, points)


def save_stats(stats):
    print("Save Today's Stats")
    gp = stats["Mariners"]["Wins"] + stats["Mariners"]["Losses"]
    daily_data_file_name = "{}.json".format(str(gp))
    daily_data_file_name = os.path.join(DATA_FILE_PATH, daily_data_file_name)
    stats_json = json.dumps(stats)
    stats_file = open(daily_data_file_name, "w")
    stats_file.write(stats_json)
    stats_file.close()


def get_previous_data(gp):
    attempt = 0
    stats = None
    while attempt < 163 and stats is None:
        attempt += 1
        file_num = gp-attempt
        if file_num < 0:
            file_num = 0
        file_name = "{}.json".format(str(file_num))
        previous_data_file_name = os.path.join(DATA_FILE_PATH, file_name)
        if os.path.exists(previous_data_file_name):
            with open(previous_data_file_name) as previous_data_file:
                stats = json.load(previous_data_file)
                return file_num, stats


def save_html(site_html):
    index_html_file = open(os.path.join(script_path, "white_board.html"), "w")
    index_html_file.write(site_html)
    index_html_file.close()


def upload_site():
    print("Upload Site")
    with open(os.path.join(script_path, "ftp_creds.json")) as ftp_creds_file:
        ftp_creds = json.load(ftp_creds_file)
        index_html_file = open(os.path.join(script_path, "white_board.html"), "rb")
        ftp = FTP(ftp_creds["FTP_Site"])
        try:
            ftp.login(ftp_creds["FTP_UserName"], ftp_creds["FTP_Password"])
            ftp.cwd("cakewood.net")
            ftp.cwd("2025BaseballOverUnder")
            ftp.sendcmd('TYPE A')
            ftp.storlines('STOR white_board.html', index_html_file)
        except Exception as e:
            print(e)
        finally:
            ftp.close()

        index_html_file.close()


def main(run_time, next_time):
    # get today's stats
    new_stats = get_stat_dict()

    # load previous stats from file
    games_played = new_stats["Mariners"]["Wins"] + new_stats["Mariners"]["Losses"]
    previous_games_played, old_stats = get_previous_data(games_played)

    html_base = None
    with open(os.path.join(script_path, 'white_board.template'), "r") as text_file:
        html_base = text_file.readlines()
    html_base = ''.join(html_base)
    html_text = html_base

    # set team tables
    team_tables = get_team_tables(new_stats, old_stats)
    html_text = html_text.replace("<TeamTables/>", team_tables)

    # win table
    record_table_html = get_projected_record_table(new_stats)
    html_text = html_text.replace("<RecordTable/>", record_table_html)

    # over/under table
    over_unders, row_html = get_over_under_table(new_stats)
    html_text = html_text.replace("<OverUnderRows/>", row_html)

    # other table
    others, row_html = get_other_table(new_stats)
    html_text = html_text.replace("<OtherRows/>", row_html)

    # put in totals
    calculate_scores(new_stats, over_unders, others)
    tool_tip = "&#10;".join(["{}: {}".format(x[0], x[1]) for x in new_stats["Mariners"][HANS]["PointContributors"]])
    html_text = html_text.replace("<Hans/>", str("<p title='{}'>Hans: {value:1.2f}</p>".format(tool_tip, value=new_stats["Mariners"][HANS]["Points"])))

    tool_tip = "&#10;".join(["{}: {}".format(x[0], x[1]) for x in new_stats["Mariners"][GREGORY]["PointContributors"]])
    html_text = html_text.replace("<Gregory/>", str("<p title='{}'>Gregory: {value:1.2f}</p>".format(tool_tip, value=new_stats["Mariners"][GREGORY]["Points"])))

    tool_tip = "&#10;".join(["{}: {}".format(x[0], x[1]) for x in new_stats["Mariners"][PAUL]["PointContributors"]])
    html_text = html_text.replace("<Paul/>", str("<p title='{}'>Paul: {value:1.2f}</p>".format(tool_tip, value=new_stats["Mariners"][PAUL]["Points"])))

    # saving these at the end because they get updated a couple of times throughout the process
    save_stats(new_stats)

    # set last updated and other header stuff
    html_text = html_text.replace("<LastUpdated/>", run_time.strftime("%m/%d/%Y, %H:%M:%S"))
    html_text = html_text.replace("<NextUpdateTime/>", next_time.strftime("%m/%d/%Y, %H:%M:%S"))
    html_text = html_text.replace("<GamesPlayed/>", str(games_played))
    html_text = html_text.replace("<PreviousGamesPlayed/>", str(previous_games_played))

    if games_played < 162:
        next_game = new_stats['Mariners']['NextGame']
        next_game_time = datetime.strptime(next_game['Time'], '%Y-%m-%dT%H:%MZ') + timedelta(hours=-7)
        next_game_day = DAYS[next_game_time.date().weekday()]
        html_text = html_text.replace('<NextGameTime/>', "{} at {}".format(next_game_day, next_game_time.strftime('%I:%M %p')))
        html_text = html_text.replace('<NextGameOpponent/>', next_game['Opponent'])
        if 'href' in next_game['GameCast']:
            html_text = html_text.replace('<NextGameLink/>', next_game['GameCast']['href'])
        else:
            html_text = html_text.replace('<NextGameLink/>', next_game['GameCast'])

    save_html(html_text)
    if not TEST:
        upload_site()


if __name__ == "__main__":
    if TEST or not RUN_ON_SCHEDULE:
        current_time = datetime.utcnow()
        next_time = current_time + timedelta(minutes=random.randint(27, 45))
        main(current_time, next_time)
    else:
        while True:
            current_time = datetime.utcnow()
            next_time = current_time + timedelta(minutes=random.randint(27, 45))
            current_hour = current_time.hour
            if 13 <= current_hour <= 16:
                if next_time.hour > 16:
                    truncated = next_time.replace(hour=0, minute=0, second=0, microsecond=0)
                    next_time = truncated + timedelta(days=1, hours=13, minutes=random.randint(15, 25))
                main(current_time, next_time)
            sleep_time = (next_time - datetime.utcnow()).total_seconds()
            time.sleep(sleep_time)
