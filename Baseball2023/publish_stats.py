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
    'Cache-Control': 'private, max-age=0, no-cache',
    "Pragma": "no-cache",
    "Expires": "Thu, 01 Jan 1970 00:00:00 GMT",
    "SessionId": str(session_id),
}

time.sleep(15)

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
SLEEP_TIME = 6

DATA_FILE_PATH = os.path.join(script_path, 'data')

BASE_PITCHER_STATS = {'SV': 0, 'IP': 0.0, 'ER': 0, 'WAR': 0.0, 'ERA': 0.00}
BASE_HITTER_STATS = {'HR': 0.0, 'OPS': 0.0, 'WAR': 0.0}

HANS = 'Hans'
GREGORY = 'Gregory'

# baseball reference keys
player_br = {
    "Rodriguez": {'Fragment': "rodriju01.shtml", 'type': "batting"},
    "Crawford": {'Fragment': "crawfjp01.shtml", 'type': "batting"},
    "Sewald": {'Fragment': "sewalpa01.shtml", 'type': "pitching"},
    "Gilbert": {'Fragment': "gilbelo01.shtml", 'type': "pitching"},
    "Ray": {'Fragment': "rayro02.shtml", 'type': "pitching"},
    "Kirby": {'Fragment': "kirbyge01.shtml", 'type': "pitching"},
    "Castillo": {'Fragment': "castilu02.shtml", 'type': "pitching"},
    "Wong": {'Fragment': "wongko01.shtml", 'type': "batting"},
    "Haggerty": {'Fragment': "haggesa01.shtml", 'type': "batting"},
    "Clase": {'Fragment': "clasejo01.shtml", 'type': "batting", "Name": "Jonatan Clase"},
    "Flexen": {'Fragment': "flexech01.shtml", 'type': "pitching"},
    "Murphy": {'Fragment': "murphto04.shtml", 'type': "batting"},
    "Raleigh": {'Fragment': "raleica01.shtml", 'type': "batting"},
    "Suarez": {'Fragment': "suareeu01.shtml", 'type': "batting"},
    "France": {'Fragment': "francty01.shtml", 'type': "batting"},
    "Kelenic": {'Fragment': "kelenja01.shtml", 'type': "batting"},
    "Gonzales": {'Fragment': "gonzama02.shtml", 'type': "pitching"},
    "Hernandez": {'Fragment': "hernate01.shtml", 'type': "batting"},
    "Munoz": {'Fragment': "munozan01.shtml", 'type': "pitching"},
    "Pollock": {'Fragment': "polloaj01.shtml", 'type': "batting"},
    "La Stella": {'Fragment': "lasteto01.shtml", 'type': "batting"},
    "Ford": {'Fragment': "fordmi01.shtml", 'type': "batting"},
    "Moore": {'Fragment': "mooredy01.shtml", 'type': "batting"},
    "Trammell": {'Fragment': "trammta01.shtml", 'type': "batting"},
}

teams = {
    GREGORY: [
        (2, "Castillo", "Luis Castillo"),
        (3, "Kirby", "George Kirby"),
        (6, "Wong", "Kolten Wong"),
        (7, "Crawford", "J.P. Crawford"),
        (10, "Suarez", "Eugenio Suárez"),
        (11, "Haggerty", "Sam Haggerty"),
        (14, "Kelenic", "Jarred Kelenic"),
        (15, "Sewald", "Paul Sewald"),
        (18, "Flexen", "Chris Flexen"),
        (19, "Clase", "Jonatan Clase"),
    ],
    HANS: [
        (1, "Rodriguez", "Julio Rodríguez"),
        (4, "France", "Ty France"),
        (5, "Gilbert", "Logan Gilbert"),
        (8, "Raleigh", "Cal Raleigh"),
        (9, "Hernandez", "Teoscar Hernández"),
        (12, "Ray", "Robbie Ray"),
        (13, "Munoz", "Andrés Muñoz"),
        (16, "Murphy", "Tom Murphy"),
        (17, "Pollock", "A.J. Pollock"),
        (20, "Gonzales", "Marco Gonzales"),
    ]
}


def accumulate_group_stat(guys, stats, local_name):
    total = 0
    tool_tip = ''
    for guy in guys:
        stat = stats[guy][local_name]
        total = total + stat
        if stat > 0:
            player = player_br[guy]["Name"]
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

    espn_page = 'https://www.espn.com/mlb/team/stats/_/name/sea'
    page = requests.get(espn_page, headers)
    start_index = page.text.index('{"app":')
    end_index = page.text.index('"user":{}}') + 10
    stats_json = page.text[start_index:end_index]

    y = json.loads(stats_json)

    # in this thing teamStats has runsScored and runsAllowed
    # playerStats has everything else that we currently want
    batting_stats = y['page']['content']['stats']
    team_stats = batting_stats['teamStats']['team'][0]['stats']
    for stat in team_stats:
        if stat['name'] == 'runs':
            stat_dict['Mariners']['RunsScored'] = int(stat['displayValue'])

    opponent_stats = batting_stats['teamStats']['opponent'][0]['stats']
    for stat in opponent_stats:
        if stat['name'] == 'runs':
            stat_dict['Mariners']['RunsAllowed'] = int(stat['displayValue'])

    player_stats = batting_stats['playerStats'][0]

    collect_batting = ['homeRuns', 'OPS', 'WARBR']
    for player in player_stats:
        name = player['athlete']['shortName'][player['athlete']['shortName'].index(' ') + 1:]
        this_player_stats = {}
        stat_dict[name] = this_player_stats
        for stat in player['statGroups']['stats']:
            if stat['name'] in collect_batting:
                this_player_stats[stat['abbreviation']] = float(stat['displayValue'])

    time.sleep(SLEEP_TIME)
    espn_page = 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/sea'
    page = requests.get(espn_page, headers)
    start_index = page.text.index('{"app":')
    end_index = page.text.index('"user":{}}') + 10
    stats_json = page.text[start_index:end_index]

    y = json.loads(stats_json)
    pitching_stats = y['page']['content']['stats']
    player_stats = pitching_stats['playerStats'][0]

    collect_pitching = ['saves', 'innings', 'earnedRuns', 'WARBR', 'ERA']
    for player in player_stats:
        if player['athlete']['shortName'] != 'D. Castillo' and player['athlete']['shortName'] != 'J. Rodriguez' and player['athlete']['shortName'] != 'M. Ford':
            name = player['athlete']['shortName'][player['athlete']['shortName'].index(' ') + 1:]
            this_player_stats = {}
            stat_dict[name] = this_player_stats
            for stat in player['statGroups']['stats']:
                if stat['name'] in collect_pitching:
                    this_player_stats[stat['abbreviation']] = float(stat['displayValue'])

    # look up record from espn standsing page
    time.sleep(SLEEP_TIME)
    espn_page = 'https://www.espn.com/mlb/standings'
    page = requests.get(espn_page, headers)
    start_index = page.text.index('{"app":')
    end_index = page.text.index('"user":{}}') + 10
    stats_json = page.text[start_index:end_index]
    y = json.loads(stats_json)

    standings_json = y['page']['content']['standings']['groups']
    index = 0
    losses_index = -1
    wins_index = -1
    for header in standings_json['headers']:
        if header == 'losses':
            losses_index = index
        elif header == 'wins':
            wins_index = index
        index = index + 1

    for group in standings_json['groups']:
        if group['name'] == 'American League':
            for division in group['children']:
                if division['name'] == 'West':
                    for place in division['standings']:
                        if place['team']['abbrev'] == 'SEA':
                            stat_dict['Mariners']['Wins'] = int(place['stats'][wins_index])
                            stat_dict['Mariners']['Losses'] = int(place['stats'][losses_index])

    for player in player_br:
        if player not in stat_dict:
            if player_br[player]['type'] == 'batting':
                stat_dict[player] = BASE_HITTER_STATS
            elif player_br[player]['type'] == 'pitching':
                stat_dict[player] = BASE_PITCHER_STATS

    # look up next game from espn team schedule page
    time.sleep(SLEEP_TIME)
    espn_team_schedule_page = 'https://www.espn.com/mlb/team/schedule/_/name/sea/seattle-mariners'
    page = requests.get(espn_team_schedule_page, headers)
    start_index = page.text.index('{"app":')
    end_index = page.text.index('"user":{}}') + 10
    stats_json = page.text[start_index:end_index]
    y = json.loads(stats_json)

    thing = y['page']['content']['scheduleData']['teamSchedule'][0]['events']['pre'][0]['group'][0]
    stat_dict['Mariners']['NextGame'] = {}
    stat_dict['Mariners']['NextGame']['Opponent'] = thing['opponent']['displayName']
    stat_dict['Mariners']['NextGame']['Time'] = thing['time']['time']
    stat_dict['Mariners']['NextGame']['GameCast'] = thing['time']['link']

    # look up player names from BaseballReference
    main_player_page = "https://www.baseball-reference.com/players/{}/{}"
    standard_stat_xpath = "string(//tr[@id='{}_{}.2023']/td[@data-stat='{}'])"

    for player_key in player_br:
        player = player_br[player_key]
        if TEST:
            player["Name"] = "Joe"
        else:
            page_fragment = player['Fragment']

            site = main_player_page.format(page_fragment[0], page_fragment)
            page = requests.get(site, headers)
            tree = html.fromstring(page.text)

            # grab player's name from page, all weird characters included!
            name = tree.xpath('//div[@id="info"]//span/text()')
            if len(name) > 0:
                player['Name'] = name[0]

            time.sleep(SLEEP_TIME)

    return stat_dict


def my_round(value, places):
    if places == 0:
        return int(value)
    else:
        return round(float(value)*10**places)/10**places


def maybe_bold(over_under, name, value, target):
    if over_under == "Under" and value < target:
        return "<b>" + name + "</b>"
    elif over_under == "Over" and value > target:
        return "<b>" + name + "</b>"
    else:
        return name


def get_team_tables(new_stats, old_stats):
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
            name = player_br[player_key]['Name']
            fragment = player_br[player_key]['Fragment']
            war = new_stats[player_key]["WAR"]
            old_war = old_stats[player_key]["WAR"]
            total_war = total_war + war
            war_delta = war - old_war
            war_delta_text = "" if war_delta == 0 else "({:.1f})".format(war_delta)
            war_column_class = "normal"
            if war == high_war:
                war_column_class = "bold"
            player_html = "<a target='_blank' href='https://www.baseball-reference.com/players/{}/{}'>{}</a>".format(fragment[0].lower(), fragment, name)
            row = "\r\n\t<tr>\r\n\t\t<td>{}</td>\r\n\t\t<td>{}</td>\r\n\t\t<td class='{}' align='right'>{:.1f}</td><td>{}</td>\r\n\t</tr>".format(draft, player_html, war_column_class, war, war_delta_text)
            table = table + row

        new_stats["Mariners"][team] = my_round(total_war, 2)
        war_delta = total_war - old_stats["Mariners"][team]
        war_delta_text = "" if war_delta == 0 else "({:.1f})".format(war_delta)
        table = table + "</table>\r\n<p/>Total War: {:.1f} {}<p/></div>".format(total_war, war_delta_text)
        team_tables.append(table)

    return "<p/>".join(team_tables)


def get_projected_record_table(stats):
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


def get_over_under_table(stats):
    over_unders = {
        "OldHomers": {
            "Title": "Homers by Old Guys",
            "Value": 57.5,
            "Over": HANS,
            "Under": GREGORY,
            "Rounding": (0, 1),
            "Guys": ["Suarez", "Hernandez", "Murphy", "Pollock", "Moore", "La Stella", "Ford", "Wong"],
            "Points": 1
        },
        "YoungHomers": {
            "Title": "Homers by Young Guys",
            "Value": 68.5,
            "Over": HANS,
            "Under": GREGORY,
            "Rounding": (0, 1),
            "Guys": ["Kelenic", "Rodriguez", "Clase", "Raleigh", "Trammell"],
            "Points": 1
        },
        "RodriguezOPS": {
            "Title": "Rodriguez OPS",
            "Value": 0.875,
            "Over": GREGORY,
            "Under": HANS,
            "Rounding": (3, 3),
            "Points": 1
        },
        "Wins": {
            "Title": "Wins",
            "Value": 89.5,
            "Over": GREGORY,
            "Under": HANS,
            "Rounding": (0, 1),
            "Points": 2
        },
        "KelenicOPS": {
            "Title": "Kelenic OPS",
            "Value": 0.75,
            "Under": GREGORY,
            "Over": HANS,
            "Rounding": (3, 3),
            "Points": 1
        },
        "GilbertKirbyERA": {
            "Title": "Gilbert/Kirby Combined ERA",
            "Value": 3.25,
            "Over": HANS,
            "Under": GREGORY,
            "Rounding": (2, 2),
            "Points": 1
        },
        "MunozSewaldCombinedSaves": {
            "Title": "Munoz/Sewald Combined Saves",
            "Value": 39.5,
            "Over": HANS,
            "Under": GREGORY,
            "Rounding": (0, 1),
            "Points": 1
        }
    }

    wins = stats["Mariners"]["Wins"]
    losses = stats["Mariners"]["Losses"]

    over_unders["Wins"]["Current"] = stats["Mariners"]["Wins"]
    over_unders["Wins"]["Projected"] = stats["Mariners"]["ProjectedWins"]

    # total_negative_war = get_total_negative_war(stats)
    # over_unders["NegativeWAR"]["Current"] = total_negative_war
    # over_unders["NegativeWAR"]["Projected"] = total_negative_war
    # html_text = html_text.replace("<NegativeWARCount/>", "{:.0f}".format(total_negative_war))

    # pitcher_count = stats["Mariners"]["PitcherCount"]
    # projected_pitcher_count = (pitcher_count-14) * (162 / (wins + losses)) + 14
    # if projected_pitcher_count < 14:
    #     projected_pitcher_count = 14
    # over_unders["PitcherCount"]["Current"] = pitcher_count
    # over_unders["PitcherCount"]["Projected"] = projected_pitcher_count

    rodriguez_ops = stats["Rodriguez"]["OPS"]
    over_unders["RodriguezOPS"]["Current"] = rodriguez_ops
    over_unders["RodriguezOPS"]["Projected"] = rodriguez_ops

    kelenic_ops = stats["Kelenic"]["OPS"]
    over_unders["KelenicOPS"]["Current"] = kelenic_ops
    over_unders["KelenicOPS"]["Projected"] = kelenic_ops

    old_guy_homers, tool_tip = accumulate_group_stat(over_unders["OldHomers"]["Guys"], stats, 'HR')
    over_unders["OldHomers"]["Current"] = old_guy_homers
    over_unders["OldHomers"]["Projected"] = 162 / (wins + losses) * old_guy_homers
    over_unders["OldHomers"]["ToolTip"] = tool_tip

    young_guy_homers, tool_tip = accumulate_group_stat(over_unders["YoungHomers"]["Guys"], stats, "HR")
    over_unders["YoungHomers"]["Current"] = young_guy_homers
    over_unders["YoungHomers"]["Projected"] = 162 / (wins + losses) * young_guy_homers
    over_unders["YoungHomers"]["ToolTip"] = tool_tip

    gilbert_ip = convert_innings_pitched(stats["Gilbert"]["IP"])
    kirby_ip = convert_innings_pitched(stats["Kirby"]["IP"])
    combined_era = 9*(stats["Gilbert"]["ER"] + stats["Kirby"]["ER"]) / (gilbert_ip + kirby_ip)
    over_unders["GilbertKirbyERA"]["Current"] = combined_era
    over_unders["GilbertKirbyERA"]["Projected"] = combined_era
    over_unders["GilbertKirbyERA"]['ToolTip'] = 'Kirby: IP={} ER={} ERA={}&#10;Gilbert: IP={} ER={} ERA={}'.format(my_round(kirby_ip, 2), my_round(stats["Kirby"]["ER"], 0), my_round(stats["Kirby"]["ERA"], 2), my_round(gilbert_ip, 2), my_round(stats["Gilbert"]["ER"], 0), my_round(stats["Gilbert"]["ERA"], 2))

    combined_saves = stats["Munoz"]["SV"] + stats["Sewald"]["SV"]
    over_unders["MunozSewaldCombinedSaves"]["Current"] = combined_saves
    over_unders["MunozSewaldCombinedSaves"]["Projected"] = 162 / (wins + losses) * combined_saves
    over_unders["MunozSewaldCombinedSaves"]['ToolTip'] = 'Munoz: {}&#10;Sewald: {}'.format(my_round(stats["Munoz"]["SV"], 0), my_round(stats["Sewald"]["SV"], 0))

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
    others = {
        "BestTeam": {
            "Title": "Team WAR",
            "Points": 3
        },
        "BestPlayer": {
            "Title": "Best Player WAR",
            "Points": 0
        },
        "WorstPlayer": {
            "Title": "Worst Player WAR",
            "Points": 1
        }
    }

    # Team WAR
    hans_team_war = stats["Mariners"][HANS]
    gregory_team_war = stats["Mariners"][GREGORY]
    if gregory_team_war > hans_team_war:
        others["BestTeam"]["Best"] = "Team {}".format(GREGORY)
        others["BestTeam"]["Relevant"] = "{:.1f} WAR".format(gregory_team_war)
        others["BestTeam"]["Winner"] = GREGORY
    elif hans_team_war > gregory_team_war:
        others["BestTeam"]["Best"] = "Team {}".format(HANS)
        others["BestTeam"]["Relevant"] = "{:.1f} WAR".format(hans_team_war)
        others["BestTeam"]["Winner"] = HANS
    else:
        others["BestTeam"]["Best"] = "Team {}, Team {}".format(HANS, GREGORY)
        others["BestTeam"]["Relevant"] = "{:.1f} WAR".format(hans_team_war)
        others["BestTeam"]["Winner"] = "{}, {}".format(HANS, GREGORY)


    # Best Player(s)
    global_high_war = -10
    global_low_war = 100
    best_players = []
    worst_players = []
    best_player_winners = []
    worst_player_winners = []
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
                worst_player_winners = [team]
            elif stats[player[1]]["WAR"] == global_low_war:
                worst_players.append(player[2])
                if team not in worst_player_winners:
                    worst_player_winners.append(team)

    others["BestPlayer"]["Best"] = ", ".join(best_players)
    others["BestPlayer"]["Relevant"] = "{:.1f} WAR".format(global_high_war)
    others["BestPlayer"]["Winner"] = ", ".join(best_player_winners)

    if len(worst_player_winners) == 1:
        if HANS in worst_player_winners:
            worst_player_winners = [GREGORY]
        else:
            worst_player_winners = [HANS]

    others["WorstPlayer"]["Best"] = ", ".join(worst_players)
    others["WorstPlayer"]["Relevant"] = "{:.1f} WAR".format(global_low_war)
    others["WorstPlayer"]["Winner"] = ", ".join(worst_player_winners)

    row_template = "<td>{}</td><td>{}</td><td>{}</td><td class='bold'>{}</td>"
    rows = []
    for other in others:
        item = others[other]
        row = row_template
        row = row.format(item["Title"], item["Best"], item["Relevant"], item["Winner"])
        rows.append(row)

    return others, "<tr>" + "</tr>\r\n<tr>".join(rows) + "</tr>"


def calculate_scores(over_unders, others):
    hans = 0
    gregory = 0
    for item in over_unders:
        over = over_unders[item]["Projected"] > over_unders[item]["Value"]
        points = over_unders[item]["Points"]
        if over and over_unders[item]["Over"] == "Hans":
            hans += points
        elif not over and over_unders[item]["Under"] == "Hans":
            hans += points
        else:
            gregory += points

    for item in others:
        points = others[item]["Points"]
        if HANS in others[item]["Winner"] and GREGORY in others[item]["Winner"]:
            hans += points/2
            gregory += points/2
        elif HANS in others[item]["Winner"]:
            hans += points
        elif GREGORY in others[item]["Winner"]:
            gregory += points

    return hans, gregory


def save_stats(stats):
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
        file_name = "{}.json".format(str(gp-attempt))
        previous_data_file_name = os.path.join(DATA_FILE_PATH, file_name)
        if os.path.exists(previous_data_file_name):
            with open(previous_data_file_name) as previous_data_file:
                stats = json.load(previous_data_file)
                return gp - attempt, stats


def save_html(site_html):
    index_html_file = open(os.path.join(script_path, "white_board.html"), "w")
    index_html_file.write(site_html)
    index_html_file.close()


def upload_site():
    with open(os.path.join(script_path, "ftp_creds.json")) as ftp_creds_file:
        ftp_creds = json.load(ftp_creds_file)
        index_html_file = open(os.path.join(script_path, "white_board.html"), "rb")
        ftp = FTP(ftp_creds["FTP_Site"])
        try:
            ftp.login(ftp_creds["FTP_UserName"], ftp_creds["FTP_Password"])
            ftp.cwd("cakewood.net")
            ftp.cwd("2023BaseballOverUnder")
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
    hans, gregory = calculate_scores(over_unders, others)
    html_text = html_text.replace("<Hans/>", str(hans))
    html_text = html_text.replace("<Gregory/>", str(gregory))

    # saving these at the end because they get updated a couple of times throughout the process
    save_stats(new_stats)

    # set last updated and other header stuff
    html_text = html_text.replace("<LastUpdated/>", run_time.strftime("%m/%d/%Y, %H:%M:%S"))
    html_text = html_text.replace("<NextUpdateTime/>", next_time.strftime("%m/%d/%Y, %H:%M:%S"))
    html_text = html_text.replace("<GamesPlayed/>", str(games_played))
    html_text = html_text.replace("<PreviousGamesPlayed/>", str(previous_games_played))

    # set next game stuff
    # <div>Next Game: <em><NextGameTime/></em> vs. <NextGameOpponent> /<a href="<NextGameLink>" target="_blank">Game Cast</a>)</p></div>
    #     stat_dict['Mariners']['NextGame']['Opponent'] = thing['opponent']['displayName']
    #     stat_dict['Mariners']['NextGame']['Time'] = thing['time']['time']
    #     stat_dict['Mariners']['NextGame']['GameCast'] = thing['time']['link']
    next_game = new_stats['Mariners']['NextGame']
    next_game_time = datetime.strptime(next_game['Time'], '%Y-%m-%dT%H:%MZ') + timedelta(hours=-7)
    next_game_day = DAYS[next_game_time.date().weekday()]
    html_text = html_text.replace('<NextGameTime/>', "{} at {}".format(next_game_day, next_game_time.strftime('%I:%M %p')))
    html_text = html_text.replace('<NextGameOpponent/>', next_game['Opponent'])
    html_text = html_text.replace('<NextGameLink/>', next_game['GameCast'])

    save_html(html_text)
    if not TEST:
        upload_site()


if __name__ == "__main__":
    if TEST:
        current_time = datetime.utcnow()
        next_time = current_time + timedelta(minutes=37)
        main(current_time, next_time)
    else:
        while True:
            current_time = datetime.utcnow()
            next_time = current_time + timedelta(minutes=37)
            current_hour = current_time.hour
            if 13 <= current_hour <= 17:
                if next_time.hour > 17:
                    truncated = next_time.replace(hour=0, minute=0, second=0, microsecond=0)
                    next_time = truncated + timedelta(days=1, hours=13, minutes=21)
                main(current_time, next_time)
            sleep_time = (next_time - datetime.utcnow()).total_seconds()
            time.sleep(sleep_time)
