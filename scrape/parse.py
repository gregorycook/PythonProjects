import csv

file = open("scrape.csv")
csv = csv.reader(file)

sql = list()

rowers = list()
current_id = 0
skipped_one = False
challenges = list()

challenge = list()
for row in csv:
	this_id = int(row[0])
	if this_id != current_id:
		current_id = this_id
		skipped_one = False
		challenge = row
		challenge.append([])
		challenges.append(challenge)
	elif not skipped_one:
		skipped_one = True
	else:
		attempt = row
		rower = attempt[2]
		if rower not in rowers:
			rowers.append(rower)
		challenge[-1].append(attempt)

athletes = dict()
athletes["GregC"] = {"Name":"Gregory", "Id":1}
athletes["Arlene"] = {"Name":"Arlene", "Id":2}
athletes["Lee"] = {"Name":"Lee", "Id":14}
athletes["DaveC"] = {"Name":"Dave C", "Id":4}
athletes["Adrian"] = {"Name":"Adrian", "Id":5}
athletes["Rocky"] = {"Name":"Rocky", "Id":6}
athletes["AndyB"] = {"Name":"Andy B", "Id":7}
athletes["Larry"] = {"Name":"Larry", "Id":8}
athletes["Kay"] = {"Name":"Kay", "Id":9}
athletes["Si"] = {"Name":"Si", "Id":11}
athletes["NavHaz"] = {"Name":"Navigation Hazard", "Id":12}
athletes["DaveS"] = {"Name":"Dave Speed", "Id":13}
athletes["stupe"] = {"Name":"Stupefaction", "Id":15}

def athlete_sql(id, name):
	return "insert into athlete(Id, Name, Gender) values (" + str(id) + ", '" + name + "', 'M');"

athlete_id = 16
for rower in rowers:
	if rower not in athletes:
		athletes[rower] = {"Name":rower, "Id":athlete_id}
		sql.append(athlete_sql(athlete_id, rower))
		athlete_id += 1

def challenge_sql(id, name, month, year, type, description, distance, time):
	return "insert into challenge(Id, Name, Month, Year, Type, Description, Distance, Time) values (%d, '%s', %d, %d, '%s', '%s', %s, %s);"%(id, name.replace("'", "''"), month, year, type, description.replace("'", "''"), distance, time)
	
def attempt_sql(athlete_id, challenge_id, distance, spm, time, weight):
	return "insert into attempt(AthleteId, ChallengeId, Distance, SPM, Time, Weight) values (%d, %d, %s, %d, %s, '%s');"%(athlete_id, challenge_id, distance, spm, time, weight)
		
challenge_id = 39
for challenge in challenges:
	## 1,None,Rocket,1:53.9,7903,20,-0.6,12,12,24,98,81,179,None
	distance = "NULL"
	time = "NULL"
	if challenge[5] == "T":
		time = challenge[6]
	else:
		distance = challenge[6]
	sql.append(challenge_sql(challenge_id, challenge[2], int(challenge[4]), int(challenge[3]), challenge[5], challenge[2], distance, time))
	
	for attempt in challenge[-1]:
		athlete = athletes[attempt[2]]
		attempt_distance = 0
		attempt_time = 0
		if distance == "NULL":
			attempt_distance = attempt[4]
			attempt_time = int(time)
		else:
			ftr = [3600,60,1]
			x = attempt[4]
			while x.count(":") < 2:
				x = "0:" + x
			attempt_time = sum([a*b for a,b in zip(ftr, map(float,x.split(':')))])
			attempt_distance = int(distance)
		spm = attempt[5]
		if spm == "None":
			spm = 0
		else:
			spm = int(spm)
		sql.append(attempt_sql(athlete["Id"], challenge_id, attempt_distance, spm, attempt_time, "H"))
	challenge_id += 1
	
for statement in sql:
	print statement