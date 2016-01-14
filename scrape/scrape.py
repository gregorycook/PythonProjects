from lxml import html
import requests

page = requests.get("http://www.teamoarsome.com/challenge/")
tree = html.fromstring(page.text)

table = tree.xpath('//table[@id="archiveTable"]//tr/@class')

challenge_id = 1
for x in table:
	subpage = requests.get("http://www.teamoarsome.com" + x)
	challenge_tree = html.fromstring(subpage.text)
	chart = challenge_tree.xpath('//table[@id="mainChart"]')
	if len(chart) == 0:
		chart = challenge_tree.xpath('//table[@class="chart"]')
	if len(chart) == 1:
		title_path = '//table[@id="archiveTable"]//tr[@class="'+x+'"]//td[@class="piece"]/text()'
		title = challenge_tree.xpath(title_path)
		print str(challenge_id) + "," + x + ',"' + "".join([s for s in title[0] if ord(s) < 128 and ord(s) != 34]) + '"'
		for row in chart[0]:
			if str(row[3].text) != "None":
				nice = str(challenge_id) + "," + ",".join(str(column.text) for column in row)
				print nice
		challenge_id += 1
			

			