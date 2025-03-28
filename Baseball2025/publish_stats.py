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
    "Rodriguez": {'Fragment': "rodriju01.shtml", 'type': "batting"},
    "Miller": {'Fragment': "millebr04.shtml", 'type': "pitching"},
    "Raley": {'Fragment': "raleylu01.shtml", 'type': "batting"},
    "Woo": {'Fragment': "woobr01.shtml", 'type': "pitching"},
    "Munoz": {'Fragment': "munozan01.shtml", 'type': "pitching"},
    "Solano": {'Fragment': "solando01.shtml", 'type': "batting"},
    "Shenton": {'Fragment': "shentau01.shtml", 'type': "batting"},
    "Brash": {'Fragment': "brashma01.shtml", 'type': "pitching"},


    "Raleigh": {'Fragment': "raleica01.shtml", 'type': "batting"},
    "Gilbert": {'Fragment': "gilbelo01.shtml", 'type': "pitching"},
    "Crawford": {'Fragment': "crawfjp01.shtml", 'type': "batting"},
    "Arozarena": {'Fragment': "arozara01.shtml", 'type': "batting"},
    "Bliss": {'Fragment': "blissry01.shtml", 'type': "batting"},
    "Tellez": {'Fragment': "tellero01.shtml", 'type': "batting"},
    "Young": {'Fragment': "youngco01.shtml", 'type': "batting", "Name": "Cole Young"},
    "Santos": {'Fragment': "santogr01.shtml", 'type': "pitching"},


    "Kirby": {'Fragment': "kirbyge01.shtml", 'type': "pitching"},
    "Robles": {'Fragment': "roblevi01.shtml", 'type': "batting"},
    "Moore": {'Fragment': "mooredy01.shtml", 'type': "batting"},
    "Castillo": {'Fragment': "castilu02.shtml", 'type': "pitching"},
    "Polanco": {'Fragment': "polanjo01.shtml", 'type': "batting"},
    "Thornton": {'Fragment': "thorntr01.shtml", 'type': "pitching"},
    "Ford": {'Fragment': "fordha01.shtml", 'type': "batting", "Name": "Harry Ford"},
    "Bazardo": {'Fragment': "bazared01.shtml", 'type': "pitching"},

    "Garver": {'Fragment': "garvemi01.shtml", 'type': "batting"},
}

teams = {
    GREGORY: [
        (1, "Rodriguez", "Julio Rodriguez"),
        (6, "Miller", "Bryce Miller"),
        (7, "Raley", "Luke Raley"),
        (12, "Woo", "Bryan Woo"),
        (13, "Munoz", "Andres Munoz"),
        (18, "Solano", "Donovan Solano"),
        (19, "Shenton", "Austin Shenton"),
        (24, "Brash", "Matt Brash"),
    ],
    HANS: [
        (2, "Raleigh", "Cal Raleigh"),
        (5, "Gilbert", "Logan Gilbert"),
        (8, "Crawford", "J.P. Crawford"),
        (11, "Arozarena", "Randy Arozarena"),
        (14, "Bliss", "Ryan Bliss"),
        (17, "Tellez", "Rowdy Tellez"),
        (20, "Young", "Cole Young"),
        (23, "Santos", "Gregory Santos"),
    ],
    PAUL: [
        (3, "Kirby", "George Kirby"),
        (4, "Robles", "Victor Robles"),
        (9, "Moore", "Dylan Moore"),
        (10, "Castillo", "Luis Castillo"),
        (15, "Polanco", "Jorge Polanco"),
        (16, "Thornton", "Trent Thornton"),
        (21, "Ford", "Harry Ford"),
        (22, "Bazardo", "Eduard Bazardo"),
    ]
}


def accumulate_group_stat(item, stats, names=None):
    local_name = item["Stat"]
    guys = item["Guys"]
    total = 0
    tool_tip = ''
    sorted_guys = sorted(guys, key=lambda x: -stats[x][local_name])
    for guy in sorted_guys:
        stat = stats[guy][local_name]
        total = total + stat
        if stat > 0:
            player = guy
            if names is not None:
                player = names[guy]["Name"]
            tool_tip = "{}&#10;{}: {}".format(tool_tip, player, my_round(stat, 0))

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

    collect_batting = ['homeRuns', 'OPS', 'WARBR', 'stolenBases']
    for player in player_stats:
        name = player['athlete']['shortName'][player['athlete']['shortName'].index(' ') + 1:]
        if name in player_br:
            player_br[name]["Name"] = player['athlete']['name']
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
            player_br[player_key]['Name'] = player_stuff[2]
            if war > high_war:
                high_war = war
        for player_stuff in teams[team]:
            draft = player_stuff[0]
            player_key = player_stuff[1]
            name = player_br[player_key]['Name']
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
            player_html = "<a target='_blank' href='https://www.baseball-reference.com/players/{}/{}'>{}</a>".format(fragment[0].lower(), fragment, name)
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


def get_total_negative_war(stats):
    result = 0
    for team in teams:
        for player in teams[team]:
            if stats[player[1]]["WAR"] < 0:
                result += 1

    return result


def convert_innings_pitched(standard_ip):
    truncated = my_round(standard_ip, 0)
    outs = standard_ip - truncated
    return truncated + 10 * outs / 3


def add_points(stats, name, thing, points):
    stats["Mariners"][name]["Points"] = stats["Mariners"][name]["Points"] + points
    if points > 0:
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
            "Guys": ["Polanco", "Moore", "Raley", "Solano", "Crawford", "Arozarena", "Tellez", "Garver"],
            "Points": 1,
            "Stat": "HR"
        },
        "RodriguezOPS": {
            "Title": "Rodriguez OPS",
            "Value": 0.800,
            "Over": [GREGORY],
            "Under": [HANS, PAUL],
            "Rounding": (3, 3),
            "Points": 1
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
            "Points": 1
        },
        "FourYoungPitcherWins": {
            "Title": "4 Young Pitcher Wins",
            "Value": 43.5,
            "Over": [HANS, PAUL],
            "Under": [GREGORY],
            "Rounding": (0, 1),
            "Points": 1,
            "Guys": ["Gilbert", "Woo", "Miller", "Kirby"],
            "Stat": "W"
        },
        "AllStars": {
            "Title": "All Stars",
            "Value": 2.5,
            "Over": [HANS],
            "Under": [GREGORY, PAUL],
            "Rounding": (0, 0),
            "Points": 1,
            "Guys": []
        },
        "Released": {
            "Title": "Released/DFAed",
            "Value": 7.5,
            "Over": [HANS, PAUL],
            "Under": [GREGORY],
            "Rounding": (0, 0),
            "Points": 1,
            "Guys": ["Mitch Haniger"]
        },
        "InfieldHomeRuns": {
            "Title": "Home Runs by the Infield",
            "Value": 88.5,
            "Over": [PAUL],
            "Under": [GREGORY, HANS],
            "Rounding": (0, 1),
            "Points": 1,
            "Guys": ["As 1B", "As 2B", "As 3B", "As SS", "As DH"],
            "Stat": "HR"
        }
    }

    wins = stats["Mariners"]["Wins"]
    losses = stats["Mariners"]["Losses"]

    over_unders["Wins"]["Current"] = stats["Mariners"]["Wins"]
    over_unders["Wins"]["Projected"] = stats["Mariners"]["ProjectedWins"]

    total_negative_war = get_total_negative_war(stats)
    over_unders["NegativeWAR"]["Current"] = total_negative_war
    over_unders["NegativeWAR"]["Projected"] = total_negative_war

    # pitcher_count = stats["Mariners"]["PitcherCount"]
    # projected_pitcher_count = (pitcher_count-14) * (162 / (wins + losses)) + 14
    # if projected_pitcher_count < 14:
    #     projected_pitcher_count = 14
    # over_unders["PitcherCount"]["Current"] = pitcher_count
    # over_unders["PitcherCount"]["Projected"] = projected_pitcher_count

    rodriguez_ops = stats["Rodriguez"]["OPS"]
    over_unders["RodriguezOPS"]["Current"] = rodriguez_ops
    over_unders["RodriguezOPS"]["Projected"] = rodriguez_ops

    old_guy_homers, tool_tip = accumulate_group_stat(over_unders["OldHomers"], stats, player_br)
    over_unders["OldHomers"]["Current"] = old_guy_homers
    if wins + losses > 0:
        over_unders["OldHomers"]["Projected"] = 162 / (wins + losses) * old_guy_homers
    else:
        over_unders["OldHomers"]["Projected"] = 0
    over_unders["OldHomers"]["ToolTip"] = tool_tip

    young_pitcher_wins, tool_tip = accumulate_group_stat(over_unders["FourYoungPitcherWins"], stats, player_br)
    over_unders["FourYoungPitcherWins"]["Current"] = young_pitcher_wins
    if wins + losses > 0:
        over_unders["FourYoungPitcherWins"]["Projected"] = 162 / (wins + losses) * young_pitcher_wins
    else:
        over_unders["FourYoungPitcherWins"]["Projected"] = 0
    over_unders["FourYoungPitcherWins"]["ToolTip"] = tool_tip

    infield_homeruns, tool_tip = accumulate_group_stat(over_unders["InfieldHomeRuns"], stats['Mariners']['HomeRuns']['ByPosition'])
    over_unders["InfieldHomeRuns"]["Current"] = infield_homeruns
    if wins + losses > 0:
        over_unders["InfieldHomeRuns"]["Projected"] = 162 / (wins + losses) * young_pitcher_wins
    else:
        over_unders["InfieldHomeRuns"]["Projected"] = 0
    over_unders["InfieldHomeRuns"]["ToolTip"] = tool_tip

    over_unders["AllStars"]["Current"] = len(over_unders["AllStars"]["Guys"])
    over_unders["AllStars"]["Projected"] = 1

    over_unders["Released"]["Current"] = len(over_unders["Released"]["Guys"])
    if wins + losses > 0:
        over_unders["Released"]["Projected"] = 162 / (wins + losses) * over_unders["Released"]["Current"]
    else:
        over_unders["Released"]["Projected"] = 0
    over_unders["Released"]["Projected"] = over_unders["Released"]["Current"]
    over_unders["Released"]["ToolTip"] = "&#10;".join(over_unders["Released"]["Guys"])

    row_template = "<td>{}</td><td>{}</td><td>{}</td><td>{}</td><td {}>{num1:.{places1}f}</td><td>{num2:.{places2}f}</td>"
    rows = []
    for over_under in over_unders:
        item = over_unders[over_under]

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
        others["BestTeam"]["Best"] = ", ".join(["Team " + x["Name"] for x in sorted_teams]);
        others["BestTeam"]["Relevant"] = "{:.1f} WAR".format(sorted_teams[0]["TeamWAR"])
        others["BestTeam"]["Winner"] = ", ".join([x["Name"] for x in sorted_teams])
        add_points(stats, sorted_teams[0]["Name"], "BestTeam", 1.3333)
        add_points(stats, sorted_teams[1]["Name"], "BestTeam", 1.3333)
        add_points(stats, sorted_teams[2]["Name"], "BestTeam", 1.3333)
    elif sorted_teams[0]["TeamWAR"] == sorted_teams[1]["TeamWAR"]:
        # last two are tied
        others["BestTeam"]["Best"] = ", ".join(["Team " + x["Name"] for x in sorted_teams[0:2]]);
        others["BestTeam"]["Relevant"] = "{:.1f} WAR".format(sorted_teams[2]["TeamWAR"])
        others["BestTeam"]["Winner"] = sorted_teams[-1]["Name"]
        add_points(stats, sorted_teams[0]["Name"], "BestTeam", 0.5)
        add_points(stats, sorted_teams[1]["Name"], "BestTeam", 0.5)
        add_points(stats, sorted_teams[2]["Name"], "BestTeam", 3)
    elif sorted_teams[1]["TeamWAR"] == sorted_teams[2]["TeamWAR"]:
        # first two are tied
        others["BestTeam"]["Best"] = ", ".join(["Team " + x["Name"] for x in sorted_teams[1:2]])
        others["BestTeam"]["Relevant"] = "{:.1f} WAR".format(sorted_teams[2]["TeamWAR"])
        others["BestTeam"]["Winner"] = ", ".join([x["Name"] for x in sorted_teams[1:2]])
        add_points(stats, sorted_teams[0]["Name"], "BestTeam", 0)
        add_points(stats, sorted_teams[1]["Name"], "BestTeam", 2)
        add_points(stats, sorted_teams[2]["Name"], "BestTeam", 2)
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
                best_players = [player[2]]
                global_high_war = stats[player[1]]["WAR"]
                best_player_winners = [team]
            elif stats[player[1]]["WAR"] == global_high_war:
                best_players.append(player[2])
                if team not in best_player_winners:
                    best_player_winners.append(team)

            if stats[player[1]]["WAR"] < global_low_war:
                worst_players = [player[2]]
                global_low_war = stats[player[1]]["WAR"]
                worst_player_losers = [team]
            elif stats[player[1]]["WAR"] == global_low_war:
                worst_players.append(player[2])
                if team not in worst_player_losers:
                    worst_player_losers.append(team)

    others["BestPlayer"]["Best"] = ", ".join(best_players)
    others["BestPlayer"]["Relevant"] = "{:.1f} WAR".format(global_high_war)
    others["BestPlayer"]["Winner"] = ", ".join(best_player_winners)

    worst_player_winners = [GREGORY, HANS, PAUL]
    for team in worst_player_losers:
        worst_player_winners.remove(team);

    others["WorstPlayer"]["Best"] = ", ".join(worst_players)
    others["WorstPlayer"]["Relevant"] = "{:.1f} WAR".format(global_low_war)
    others["WorstPlayer"]["Winner"] = ", ".join(worst_player_winners)

    others["MakePlayoffs"]["Relevant"] = "Current Playoff Seed = {}".format(stats["Mariners"]["PlayoffSeed"])
    if stats["Mariners"]["PlayoffSeed"] <= 6:
        others["MakePlayoffs"]["Best"] = "Yes"
        others["MakePlayoffs"]["Winner"] = ""
    else:
        others["MakePlayoffs"]["Best"] = "No"
        others["MakePlayoffs"]["Winner"] = ", ".join([GREGORY, HANS, PAUL])
        add_points(stats, HANS, "MakePlayoffs", 0)
        add_points(stats, GREGORY, "MakePlayoffs", 0)
        add_points(stats, PAUL, "MakePlayoffs", 0)

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
            for name in over_unders[item]["Under"]:
                add_points(stats, name, item, points)
        if over_unders[item]["Projected"] >= over_unders[item]["Value"]:
            for name in over_unders[item]["Over"]:
                add_points(stats, name, item, points)


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
