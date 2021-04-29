import mysql.connector
import csv
import sys, getopt

config = {
  'user': 'username',
  'password': 'password',
  'host': '127.0.0.1',
  'database': 'database',
}
	
add_payment = ("INSERT INTO payment "
					"(unit_id, opportunity_id, half_year_id, amount) "
					"VALUES (%(unit_id)s, %(opportunity_id)s, %(half_year_id)s, %(amount)s)")

def generate_late_letters(months):
	select = ("select u.directory_name, p.amount, p.amount - p1.amount - p2.amount "
                "from unit u, pledge p, payment p1, payment p2 "
               "where u.id = p.unit_id and u.id = p1.unit_id and u.id = p2.unit_id "
			     "and p1.opportunity_id = 1 and p1.half_year_id = 1 and p1.opportunity_id = 1 "
			     "and u.autopay = 0 and p2.half_year_id = 2 "
			     "and (p.amount - p1.amount - p2.amount)/p.amount > %s")
	
	cnx = mysql.connector.connect(**config)
	cursor = cnx.cursor()
	cursor.execute(select, ((12-months)/12.0,))

	for (directory_name, pledge, remaining) in cursor:
		print("{} needs to pay {} of {}".format(directory_name, remaining, pledge))
	cursor.close()
	cnx.close()

def initialize():
	cnx = mysql.connector.connect(**config)

	file = open("initial.csv")
	csv = csv.reader(file)

	cursor = cnx.cursor()

	add_unit = ("INSERT INTO unit "
				"(quickbooks_name, directory_name, mailing_name, address_line_1, city_state_zip, autopay) "
				"VALUES (%(quickbooks_name)s, %(directory_name)s, %(mailing_name)s, %(address_line_1)s, %(city_state_zip)s, %(autopay)s)")

	add_pledge = ("INSERT INTO pledge "
				"(unit_id, half_year_id, amount) "
				"VALUES (%(unit_id)s, %(half_year_id)s, %(amount)s)")

	is_first = True
	for row in csv:
		if is_first:
			is_first = False
		else:
			unit_data = {
				'quickbooks_name' : row[5],
				'directory_name' : row[0],
				'mailing_name' : row[7],
				'address_line_1' : row[8],
				'city_state_zip' : row[9],
				'autopay' : int(row[2])
			}
			cursor.execute(add_unit, unit_data)
			unit_id = cursor.lastrowid
			
			if len(row[1]) > 0:
				pledge = float(row[1])
				pledge_data = {
					'unit_id' : unit_id,
					'half_year_id' : 1,
					'amount' : pledge
				}
			
				cursor.execute(add_pledge, pledge_data)
				
				first_half_payment = float(row[4])
				second_half_payment = (pledge - first_half_payment) - float(row[6])

				payment_data = {
					'unit_id' : unit_id,
					'opportunity_id' : 1,
					'half_year_id' : 1,
					'amount' : first_half_payment
				}
				cursor.execute(add_payment, payment_data)

				payment_data = {
					'unit_id' : unit_id,
					'opportunity_id' : 1,
					'half_year_id' : 2,
					'amount' : second_half_payment
				}
				cursor.execute(add_payment, payment_data)
					
			cnx.commit()
			
	cursor.close()
	cnx.close()

def get_unit_id_from_qb_name(qb_name):
	select = ("select id from unit where quickbooks_name = %s")
	
	cnx = mysql.connector.connect(**config)
	cursor = cnx.cursor()
	cursor.execute(select, (qb_name,))
	
	id = None
	for row in cursor:
		id = row[0]
		break
	
	cursor.close()
	cnx.close()
	
	return id
	
def get_unit_id_from_dir_name(dir_name):
	select = ("select id from unit where directory_name = %s")
	
	cnx = mysql.connector.connect(**config)
	cursor = cnx.cursor()
	cursor.execute(select, (dir_name,))
	
	for row in cursor:
		id = row[0]
		break
	
	cursor.close()
	cnx.close()
	
	return id
	
def get_current_half_year():
	select = ("select id, year, part from half_year order by year, part")
	
	cnx = mysql.connector.connect(**config)
	cursor = cnx.cursor()
	cursor.execute(select)
	
	for (id, year, part) in cursor:
		current_half_year = {"id":id, "year":year, "part":part }
	
	cursor.close()
	cnx.close()
	
	return current_half_year
	
def update_pledge_paid(qb_csv_file, opportunity_id):
	half_year = get_current_half_year()
	
	cnx = mysql.connector.connect(**config)
	cursor = cnx.cursor()
	try:
		sql = "delete from payment where half_year_id={} and opportunity_id={}".format(half_year["id"], opportunity_id)
		cursor.execute(sql)
		cnx.commit()
	finally:
		cursor.close()
		cnx.close()
	
	if half_year["part"] == 2:
		sql = ("select pl.unit_id, pl.amount, pl.amount - pm.amount "
               "from half_year hy2, half_year hy1, pledge pl, payment pm "
               "where hy2.id = 2 and hy2.year = hy1.year + 1 and hy1.part = 2 and pl.half_year_id = hy1.id "
			   "and pm.half_year_id = hy1.id and pm.unit_id = pl.unit_id")
	elif half_year["part"] == 1:
		sql = ("select pl.unit_id, pl.amount, pl.amount - pm.amount "
               "from half_year hy2, half_year hy1, pledge pl, payment pm "
               "where hy2.id = 2 and hy2.year = hy1.year + 1 and hy1.part = 2 and pl.half_year_id = hy1.id "
			   "and pm.half_year_id = hy1.id and pm.unit_id = pl.unit_id")
	
	cnx = mysql.connector.connect(**config)
	cursor = cnx.cursor()
	try:
		cursor.execute(sql)
	
		dict = {}
		for unit_id, pledge, remaining in cursor:
			dict[unit_id] = (pledge, remaining)
	finally:
		cursor.close()
		cnx.close()
		
	file = open(qb_csv_file)
	rows = csv.reader(file)
	first = True
	for row in rows:
		if first:
			first = False
		else:
			unit_id = get_unit_id_from_qb_name(row[2])
			if unit_id in dict.keys():
				payment_data = {
					'unit_id' : int(unit_id),
					'opportunity_id' : int(opportunity_id),
					'half_year_id' : int(half_year["id"]),
					'amount' : float(dict[unit_id][1]) - float(row[3].replace(',', ''))
				}
				cnx = mysql.connector.connect(**config)
				cursor = cnx.cursor()
				try:
					cursor.execute(add_payment, payment_data)
					cnx.commit()
				finally:
					cursor.close()
					cnx.close()
			else:
				print "no pledge entry for", unit_id, row[2]

def list_opportunities():
	cnx = mysql.connector.connect(**config)
	cursor = cnx.cursor()
	try:
		sql = ("select * from opportunity")
		cursor.execute(sql)
		for id, name in cursor:
			print "{}: {}".format(id, name)
	finally:
		cursor.close()
		cnx.close()	
	
def main(argv):
	try:	
		opts, args = getopt.getopt(argv, "pf:o:", ["pledge", "file=", "opportunity=", "listopt", "pledge-letters="])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	
	update_pledge = False
	list_opts = False
	pledge_letters = False
	for opt, arg in opts:
		if opt in ("-f", "--file"):
			file_name = arg
		elif opt in ("-o", "--opportunity"):
			opportunity_id = arg
		elif opt in ("-p", "--pledge"):
			update_pledge = True
		elif opt in ("--listopt"):
			list_opts = True
		elif opt in ("--pledge-letters"):
			pledge_letters = True
			months = arg
			
	if update_pledge:
		update_pledge_paid(file_name, opportunity_id)
	elif list_opts:
		list_opportunities()
	elif pledge_letters:
		generate_late_letters(int(months))
		
if __name__ == "__main__":
    main(sys.argv[1:])

