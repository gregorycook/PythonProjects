from lxml import html
from ftplib import FTP

import json
import requests

JOB_CRASH_B = 9490

JOB_ERGOMANIA = 9422
JOB_PITTSBURGH = 9419
JOB_ATLANTA = 9376
JOB_CHICAGO = 9421
JOB_TENNESSEE = 9423

regatta_names = {JOB_CRASH_B: 'Crash Bs',
                 JOB_ERGOMANIA: 'NW Ergomania',
                 JOB_PITTSBURGH: 'Pittsburgh',
                 JOB_ATLANTA: 'Atlanta',
                 JOB_CHICAGO: 'Chicago',
                 JOB_TENNESSEE: 'Tennessee'
}

MAIN_URL = "https://www.regattacentral.com/regatta/entries/competitors/?job_id={}&event_id={}"

RESULTS_XPATH = "//section[@class='content']/table/tbody"

events = [{'name': 'Crash Bs',
           'us': [
               {'name': 'Arlene', 'regattas': [(JOB_CRASH_B, 163)]},
               {'name': 'Gregory', 'regattas': [(JOB_CRASH_B, 153)]}]},
          {'name': 'US National Championships',
           'us': [
                {'name': 'Arlene', 'regattas': [(JOB_ERGOMANIA, 40), (JOB_PITTSBURGH, 114), (JOB_ATLANTA, 40), (JOB_CHICAGO, 40), (JOB_TENNESSEE, 40)]},
                {'name': 'Gregory', 'regattas': [(JOB_ERGOMANIA, 72), (JOB_PITTSBURGH, 146), (JOB_ATLANTA, 72), (JOB_CHICAGO, 72), (JOB_TENNESSEE, 72)]}]
            }]

html_template = "" \
                "<html><head>" \
                    "<title>Our 2025 Erg Races</title>" \
                    "<style>" \
                        "th, td {" \
                            "padding-top: 5px;" \
                            "padding-bottom: 10px;" \
                            "padding-left: 15px;" \
                            "padding-right: 20px; }" \
                        "table {" \
                            "border-spacing: 10px;" \
                            "font-size:120% }" \
                        "tr:nth-child(even) {" \
                            "background-color: #D6EEEE; }" \
                    "</style>" \
                "</head>" \
                "<body>" \
                "<EVENTS/><p><p>" \
                "<table><thead><tr><th>Regatta</th><th>Arlene</th><th>Gregory</th></tr></thead><tbody><LINKS/></tbody></table>" \
                "</body></html>"

event_html_template = "<b><NAME/></b><p><table><thead><tr><th>Event</th><th>Competitors</th></tr></thead><tbody><ROWS/></tbody></table>"

event_row_html_template = "<tr><td><NAME/></td><td><COMPETITORS/></td><tr>"

regatta_link_row_html_template = "<tr><td>{}</td><td><a href='{}'>link</a></td><td><a href='{}'>link</a></td><tr>"


def get_page_tree(page_url):
    page = requests.get(page_url)

    tree = html.fromstring(page.text)
    return tree


if __name__ == "__main__":
    links = {}
    for event in events:
        us = event['us']
        for person in us:
            person['competitors'] = []
            regattas = person['regattas']
            for regatta in regattas:
                job_id = regatta[0]
                event_id = regatta[1]
                page_url = MAIN_URL.format(job_id, event_id)
                page_tree = get_page_tree(page_url)
                rows = page_tree.xpath("//table[@id='table']/tbody/tr")

                if job_id not in links:
                    links[job_id] = {}

                links[job_id][person['name']] = page_url

                for row in rows:
                    gender = ""
                    name = ""
                    index = 0
                    for column in row:
                        span = column.find('span')
                        if span is not None:
                            name = span.get('title')

                        if name != '' and name is not None:
                            index = name.find('<br><br/>C')
                            if index > -1:
                                name = name[3:index]
                            else:
                                name = name[3:-4]

                            name_pieces = name.split(' ')
                            name = {"Name": name, "Last": name_pieces[-1], "Regatta": job_id}
                            person['competitors'].append(name)

    event_html_list = []
    for event in events:
        event_template = event_html_template
        us = event['us']
        rows = []
        for person in us:
            row_template = event_row_html_template
            row_template = row_template.replace("<NAME/>", person['name'])
            competitors = ", ".join(["{} ({})".format(x["Name"], regatta_names[x["Regatta"]]) for x in person['competitors']])
            row_template = row_template.replace("<COMPETITORS/>", competitors)
            rows.append(row_template)
        event_template = event_template.replace("<NAME/>", event['name'])
        event_template = event_template.replace("<ROWS/>", " ".join(rows))
        event_html_list.append(event_template)

    html_template = html_template.replace("<EVENTS/>", "<p><p>".join(event_html_list))

    link_rows = []
    for job_id in links:
        link_row = regatta_link_row_html_template.format(regatta_names[job_id], links[job_id]["Arlene"], links[job_id]["Gregory"])
        link_rows.append(link_row)

    html_template = html_template.replace("<LINKS/>", " ".join(link_rows))

    stats_file = open('2025ErgRaces.html', "w")
    stats_file.write(html_template)
    stats_file.close()

    with open('ftp_creds.json') as ftp_creds_file:
        ftp_creds = json.load(ftp_creds_file)
        index_html_file = open('2025ErgRaces.html', "rb")
        ftp = FTP(ftp_creds["FTP_Site"])
        try:
            ftp.login(ftp_creds["FTP_UserName"], ftp_creds["FTP_Password"])
            ftp.cwd("cakewood.net")
            ftp.cwd("Erg")
            ftp.sendcmd('TYPE A')
            ftp.storlines('STOR 2025ErgRaces.html', index_html_file)
        except Exception as e:
            print(e)
        finally:
            ftp.close()

        index_html_file.close()
