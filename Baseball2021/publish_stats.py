import uuid
from datetime import datetime
from ftplib import FTP
from lxml import html

import requests

session_id = uuid.uuid1()
headers = {
    'Cache-Control': 'private, max-age=0, no-cache',
    "Pragma": "no-cache",
    "Expires": "Thu, 01 Jan 1970 00:00:00 GMT",
    "SessionId": str(session_id)
}

# play baseball reference key
player_br = {
    "Seager": "seageky01.shtml",
    "Gonzales": "gonzama02.shtml",
    "Paxton": "paxtoja01.shtml",
    "Moore": "mooredy01.shtml",
    "France": "francty01.shtml",
    "White": "whiteev01.shtml",
    "Kelenic": "kelenja01.shtml",
    "Gilbert": "gilbelo01.shtml",
    "Flexen": "flexech01.shtml",
    "Kikuchi": "kikucyu01.shtml",
    "Lewis": "lewisky01.shtml",
    "Haniger": "hanigmi01.shtml",
    "Murphy": "murphto04.shtml",
    "Crawford": "crawfjp01.shtml",
    "Sheffield": "sheffju01.shtml",
    "Trammel": "trammta01.shtml",
    "Dunn": "dunnju01.shtml",
    "Fraley": "fraleja01.shtml",
    "Middleton": "middlke01.shtml",
    "Haggerty": "haggesa01.shtml"
}


def get_standard_stat(player, stat_name, stat_type):
    player_key = player_br[player]
    main_player_page = "https://widgets.sports-reference.com/wg.fcgi?css=1&site=br&url=%2Fplayers%2F{}%2F{}&div=div_{}_standard"
    standard_stat_xpath = "//tr[@id='{}_standard.2021']/td[@data-stat='{}']/text()"

    site = main_player_page.format(player_key[0], player_key, stat_type)
    page = requests.get(site, headers)
    tree = html.fromstring(page.text)
    value = tree.xpath(standard_stat_xpath.format(stat_type, stat_name))
    if len(value) > 0:
        return float(value[0])

    return 0


def get_value_stat(player, stat_name, stat_type):
    player_key = player_br[player]
    player_value_site = "https://widgets.sports-reference.com/wg.fcgi?css=1&site=br&url=%2Fplayers%2F{}%2F{}&div=div_{}_value"
    value_stat_xpath = '//tr[@id="{}_value.2021"]/td[@data-stat="{}"]/text()'

    site = player_value_site.format(player_key[0], player_key, stat_type)
    page = requests.get(site, headers)
    thing = []
    try:
        table_index = str.index(page.text, "<table")
        end_table_index = str.index(page.text, "</table")
        end_table_index = str.index(page.text, ">", end_table_index)
        table_element = page.text[table_index:end_table_index + 1]
        table_element = table_element.replace("&rsquo;", "")
        tree = html.fromstring(table_element)
        specific_xpath = value_stat_xpath.format(stat_type, stat_name)
        thing = tree.xpath(specific_xpath)
    except Exception as e:
        pass
    value = 0
    if len(thing) > 0:
        value = float(thing[0])

    return value


def get_pitcher_count():
    mariners_team_pitching_site = 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=br&url=%2Fteams%2FSEA%2F2021.shtml&div=div_team_pitching'
    mariners_pitcher_count_xpath = "count(//table[@id='team_pitching']//tr[number(td[@data-stat='IP']/text()) > 0])"
    site = mariners_team_pitching_site
    page = requests.get(site, headers)
    tree = html.fromstring(page.text)
    value = tree.xpath(mariners_pitcher_count_xpath)

    return value


def get_mariners_record():
    record_site = "https://www.baseball-reference.com/"
    record_xpath_wins = "//table[@id='standings_AL']//tr[th/@csk='SEA']//td[@data-stat='W']/text()"
    record_xpath_losses = "//table[@id='standings_AL']//tr[th/@csk='SEA']//td[@data-stat='L']/text()"

    # lookup wins/losses
    page = requests.get(record_site, headers)
    tree = html.fromstring(page.text)
    wins = int(tree.xpath(record_xpath_wins)[0])
    losses = int(tree.xpath(record_xpath_losses)[0])

    return wins, losses


def get_mariners_runs():
    baseball_reference_mariners_site = "https://www.baseball-reference.com/teams/SEA/2021.shtml"
    runs_scored_allowed_xpath = "//div[@data-template='Partials/Teams/Summary']//p[a/strong/text()='Pythagorean W-L:']/text()"

    # lookup runs scored/allowed
    page = requests.get(baseball_reference_mariners_site, headers)
    tree = html.fromstring(page.text)
    summary_text = tree.xpath(runs_scored_allowed_xpath)
    summary_list = summary_text[-1].split(",")
    runs_scored_text = summary_list[1]
    runs_allowed_text = summary_list[2]
    runs_scored = float(runs_scored_text[:runs_scored_text.index('Runs')])
    runs_allowed = float(runs_allowed_text[:runs_allowed_text.index('Runs')])

    return runs_scored, runs_allowed


def get_stat_dict():
    stat_dict = {"Seager": {}}

    stat_dict["Seager"]["HRs"] = get_standard_stat("Seager", "HR", "batting")
    stat_dict["Seager"]["WAR"] = get_value_stat("Seager", "WAR", "batting")

    stat_dict["Gonzales"] = {}
    stat_dict["Gonzales"]["ERA"] = get_standard_stat("Gonzales", "earned_run_avg", "pitching")
    stat_dict["Gonzales"]["WAR"] = get_value_stat("Gonzales", "WAR_pitch", "pitching")

    stat_dict["Paxton"] = {}
    stat_dict["Paxton"]["Starts"] = get_standard_stat("Paxton", "GS", "pitching")
    stat_dict["Paxton"]["WAR"] = get_value_stat("Paxton", "WAR_pitch", "pitching")

    stat_dict["Moore"] = {}
    stat_dict["Moore"]["WAR"] = get_value_stat("Moore", "WAR", "batting")

    stat_dict["France"] = {}
    stat_dict["France"]["WAR"] = get_value_stat("France", "WAR", "batting")

    stat_dict["White"] = {}
    stat_dict["White"]["WAR"] = get_value_stat("White", "WAR", "batting")

    stat_dict["Kelenic"] = {}
    stat_dict["Kelenic"]["OPS"] = get_standard_stat("Kelenic", "onbase_plus_slugging", "batting")
    stat_dict["Kelenic"]["WAR"] = get_value_stat("Kelenic", "WAR", "batting")

    stat_dict["Gilbert"] = {}
    stat_dict["Gilbert"]["WAR"] = get_value_stat("Gilbert", "WAR_pitch", "pitching")

    stat_dict["Flexen"] = {}
    stat_dict["Flexen"]["WAR"] = get_value_stat("Flexen", "WAR_pitch", "pitching")

    stat_dict["Kikuchi"] = {}
    stat_dict["Kikuchi"]["WAR"] = get_value_stat("Kikuchi", "WAR_pitch", "pitching")

    stat_dict["Lewis"] = {}
    stat_dict["Lewis"]["WAR"] = get_value_stat("Lewis", "WAR", "batting")

    stat_dict["Haniger"] = {}
    stat_dict["Haniger"]["HRs"] = get_standard_stat("Haniger", "HR", "batting")
    stat_dict["Haniger"]["WAR"] = get_value_stat("Haniger", "WAR", "batting")

    stat_dict["Murphy"] = {}
    stat_dict["Murphy"]["HRs"] = get_standard_stat("Murphy", "HR", "batting")
    stat_dict["Murphy"]["WAR"] = get_value_stat("Murphy", "WAR", "batting")

    stat_dict["Crawford"] = {}
    stat_dict["Crawford"]["WAR"] = get_value_stat("Crawford", "WAR", "batting")

    stat_dict["Sheffield"] = {}
    stat_dict["Sheffield"]["WAR"] = get_value_stat("Sheffield", "WAR_pitch", "pitching")

    stat_dict["Trammel"] = {}
    stat_dict["Trammel"]["WAR"] = get_value_stat("Trammel", "WAR", "batting")

    stat_dict["Dunn"] = {}
    stat_dict["Dunn"]["WAR"] = get_value_stat("Dunn", "WAR_pitch", "pitching")

    stat_dict["Fraley"] = {}
    stat_dict["Fraley"]["WAR"] = get_value_stat("Fraley", "WAR", "batting")

    stat_dict["Middleton"] = {}
    stat_dict["Middleton"]["WAR"] = get_value_stat("Middleton", "WAR_pitch", "pitching")

    stat_dict["Haggerty"] = {}
    stat_dict["Haggerty"]["WAR"] = get_value_stat("Haggerty", "WAR", "batting")

    stat_dict["Mariners"] = {}
    stat_dict["Mariners"]["PitcherCount"] = get_pitcher_count()
    stat_dict["Mariners"]["Wins"], stat_dict["Mariners"]["Losses"] = get_mariners_record()
    stat_dict["Mariners"]["RunsScored"], stat_dict["Mariners"]["RunsAllowed"] = get_mariners_runs()

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


teams = {
    "Hans": [
        (1, "Seager", "Kyle Seager"),
        (4, "Gonzales", "Marco Gonzales"),
        (5, "Paxton", "James Paxton"),
        (8, "Moore", "Dylan Moore"),
        (9, "France", "Ty France"),
        (12, "White", "Evan White"),
        (13, "Kelenic", "Jarred Kelenic"),
        (16, "Gilbert", "Logan Gilbert"),
        (17, "Flexen", "Chris Flexen"),
        (20, "Kikuchi", "Yusei Kikuchi"),
    ],
    "Gregory": [
        (2, "Lewis", "Kyle Lewis"),
        (3, "Haniger", "Mitch Haniger"),
        (6, "Crawford", "J.P. Crawford"),
        (7, "Sheffield", "Justus Sheffield"),
        (10, "Murphy", "Tom Murphy"),
        (11, "Trammel", "Taylor Trammel"),
        (14, "Dunn", "Justin Dunn"),
        (15, "Fraley", "Jake Fraley"),
        (18, "Middleton", "Keynan Middleton"),
        (19, "Haggerty", "Sam Haggerty"),
    ]
}

def get_team_tables(stats):
    team_tables = []
    team_number = 0
    for team in teams:
        team_number = team_number + 1
        total_war = 0
        table = "<div style='grid-column: {}; grid-row: 1;'><p class='team-text'>Team {}</p>\r\n<table class='team_table'>\r\n\t<thead><tr>\r\n\t\t<td>Pick</td>\r\n\t\t<td>Name</td>\r\n\t\t<td>WAR</td>\r\n\t</tr></thead>".format(str(team_number), team)
        high_war = -10
        for player in teams[team]:
            war = stats[player[1]]["WAR"]
            if war > high_war:
                high_war = war
        for player in teams[team]:
            war = stats[player[1]]["WAR"]
            total_war = total_war + war
            war_column_class = "normal"
            if war == high_war:
                war_column_class = "bold"
            player_html = "<a href='https://www.baseball-reference.com/players/{}/{}'>{}</a>".format(player[1][0].lower(),  player_br[player[1]], player[2])
            row = "\r\n\t<tr>\r\n\t\t<td>{}</td>\r\n\t\t<td>{}</td>\r\n\t\t<td class='{}'>{:.1f}</td>\r\n\t</tr>".format(player[0], player_html, war_column_class, war)
            table = table + row

        stats["Mariners"][team] = total_war
        table = table + "</table>\r\n<p/>Total War: {:.1f}<p/></div>".format(total_war)
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


def get_over_under_table(stats):
    over_unders = {
        "Wins": {
            "Title": "Wins",
            "Value": 78.5,
            "Over": "Hans",
            "Under": "Gregory",
            "Rounding": (0, 1)
        },
        "NegativeWAR": {
            "Title": "# of the 20 with negative WAR",
            "Value": 3.5,
            "Over": "Gregory",
            "Under": "Hans",
            "Rounding": (0, 0)
        },
        "PitcherCount": {
            "Title": "# of pitchers used",
            "Value": 32.5,
            "Over": "Gregory",
            "Under": "Hans",
            "Rounding": (0, 1)
        },
        "PaxtonStarts": {
            "Title": "Paxton Starts",
            "Value": 20.5,
            "Over": "Hans",
            "Under": "Gregory",
            "Rounding": (0, 1)
        },
        "MarcoERA": {
            "Title": "Marco ERA",
            "Value": 3.65,
            "Over": "Hans",
            "Under": "Gregory",
            "Rounding": (2, 2)
        },
        "KelenicOPS": {
            "Title": "Kelenic OPS",
            "Value": 0.800,
            "Over": "Gregory",
            "Under": "Hans",
            "Rounding": (3, 3)
        },
        "OldHomers": {
            "Title": "Homers by Old Guys",
            "Value": 52.5,
            "Over": "Hans",
            "Under": "Gregory",
            "Rounding": (0, 1)
        }
    }

    wins = stats["Mariners"]["Wins"]
    losses = stats["Mariners"]["Losses"]

    over_unders["Wins"]["Current"] = stats["Mariners"]["Wins"]
    over_unders["Wins"]["Projected"] = stats["Mariners"]["ProjectedWins"]

    total_negative_war = get_total_negative_war(stats)
    over_unders["NegativeWAR"]["Current"] = total_negative_war
    over_unders["NegativeWAR"]["Projected"] = total_negative_war
    # html_text = html_text.replace("<NegativeWARCount/>", "{:.0f}".format(total_negative_war))

    pitcher_count = stats["Mariners"]["PitcherCount"]
    projected_pitcher_count = 162 / (wins + losses) * (pitcher_count - 16) + 14
    if projected_pitcher_count < 14:
        projected_pitcher_count = 14
    over_unders["PitcherCount"]["Current"] = pitcher_count - 2
    over_unders["PitcherCount"]["Projected"] = projected_pitcher_count

    paxton_starts = stats["Paxton"]["Starts"]
    over_unders["PaxtonStarts"]["Current"] = paxton_starts
    over_unders["PaxtonStarts"]["Projected"] = 162 / (wins + losses) * paxton_starts

    marco_era = stats["Gonzales"]["ERA"]
    over_unders["MarcoERA"]["Current"] = marco_era
    over_unders["MarcoERA"]["Projected"] = marco_era

    kelenic_ops = stats["Kelenic"]["OPS"]
    over_unders["KelenicOPS"]["Current"] = kelenic_ops
    over_unders["KelenicOPS"]["Projected"] = kelenic_ops

    haniger_hrs = stats["Haniger"]["HRs"]
    seager_hrs = stats["Seager"]["HRs"]
    murphy_hrs = stats["Murphy"]["HRs"]
    over_unders["OldHomers"]["Current"] = haniger_hrs + seager_hrs + murphy_hrs
    over_unders["OldHomers"]["Projected"] = 162 / (wins + losses) * (
                haniger_hrs + seager_hrs + murphy_hrs)

    row_template = "<td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{num1:.{places1}f}</td><td>{num2:.{places2}f}</td>"
    rows = []
    for over_under in over_unders:
        item = over_unders[over_under]
        rounding = item["Rounding"]
        row = row_template
        row = row.format(item["Title"], item["Value"],
                         maybe_bold("Over", item["Over"], item["Projected"], item["Value"]),
                         maybe_bold("Under", item["Under"], item["Projected"], item["Value"]),
                         num1=item["Current"], places1=rounding[0], num2=item["Projected"], places2=rounding[1])
        rows.append(row)

    return "<tr>" + "</tr>\r\n<tr>".join(rows) + "</tr>"


def get_other_table(stats):
    others = {
        "Kyle": {
            "Title": "Best Kyle"
        },
        "BestTeam": {
            "Title": "High Team WAR"
        },
        "BestPlayer": {
            "Title": "High Player WAR"
        }
    }

    wins = stats["Mariners"]["Wins"]
    losses = stats["Mariners"]["Losses"]

    # Best Kyle
    lewis_war = stats["Lewis"]["WAR"]
    seager_war = stats["Seager"]["WAR"]
    if lewis_war > seager_war:
        others["Kyle"]["Thing"] = "Kyle Lewis"
        others["Kyle"]["Relevant"] = "{:.1f} WAR".format(lewis_war)
        others["Kyle"]["Winner"] = "Gregory"
    else:
        others["Kyle"]["Thing"] = "Kyle Seager"
        others["Kyle"]["Relevant"] = "{:.1f} WAR".format(seager_war)
        others["Kyle"]["Winner"] = "Hans"

    # Team WAR
    hans_team_war = stats["Mariners"]["Hans"]
    gregory_team_war = stats["Mariners"]["Gregory"]
    if gregory_team_war > hans_team_war:
        others["BestTeam"]["Thing"] = "Team Gregory"
        others["BestTeam"]["Relevant"] = "{:.1f} WAR".format(gregory_team_war)
        others["BestTeam"]["Winner"] = "Gregory"
    else:
        others["BestTeam"]["Thing"] = "Team Hans"
        others["BestTeam"]["Relevant"] = "{:.1f} WAR".format(hans_team_war)
        others["BestTeam"]["Winner"] = "Hans"

    # Best Player(s)
    global_high_war = -10
    best_players = []
    winners = []
    for team in teams:
        for player in teams[team]:
            if stats[player[1]]["WAR"] > global_high_war:
                best_players = [player[2]]
                global_high_war = stats[player[1]]["WAR"]
                winners = [team]
            elif stats[player[1]]["WAR"] == global_high_war:
                best_players.append(player[2])
                if team not in winners:
                    winners.append(team)

    others["BestPlayer"]["Thing"] = ", ".join(best_players)
    others["BestPlayer"]["Relevant"] = "{:.1f} WAR".format(global_high_war)
    others["BestPlayer"]["Winner"] = ", ".join(winners)

    row_template = "<td>{}</td><td>{}</td><td>{}</td><td class='bold'>{}</td>"
    rows = []
    for other in others:
        item = others[other]
        row = row_template
        row = row.format(item["Title"], item["Thing"], item["Relevant"], item["Winner"])
        rows.append(row)

    return "<tr>" + "</tr>\r\n<tr>".join(rows) + "</tr>"


def save_html(site_html):
    index_html_file = open("white_board.html", "w")
    index_html_file.write(site_html)
    index_html_file.close()


def upload_site():
    index_html_file = open("white_board.html", "rb")
    try:
        ftp = FTP("[ftp-site]")
        ftp.login("username", "password")
        ftp.cwd("[change to this directory]")
        ftp.cwd("[change to this directory]")
        ftp.sendcmd('TYPE A')
        ftp.storlines('STOR [put the file in as this name]', index_html_file)
    except Exception as e:
        print(e)
    finally:
        ftp.close()

    index_html_file.close()


stats = get_stat_dict()

html_base = None
with open('white_board.template', "r") as text_file:
    html_base = text_file.readlines()
html_base = ''.join(html_base)
html_text = html_base

# set last updated
html_text = html_text.replace("<LastUpdated/>", datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S"))

# set team tables
team_tables = get_team_tables(stats)
html_text = html_text.replace("<TeamTables/>", team_tables)

# win table
record_table_html = get_projected_record_table(stats)
html_text = html_text.replace("<RecordTable/>", record_table_html)

# over/under table
row_html = get_over_under_table(stats)
html_text = html_text.replace("<OverUnderRows/>", row_html)

# other table
row_html = get_other_table(stats)
html_text = html_text.replace("<OtherRows/>", row_html)

save_html(html_text)
upload_site()
