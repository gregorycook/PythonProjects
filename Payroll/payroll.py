import mysql.connector
import csv
import sys, getopt

config = {
  'user': 'payroll',
  'password': '12xuxu12',
  'host': 'localhost',
  'database': 'payroll',
  'port': '8889'
}

delete_current = ( "DELETE FROM current_period" )
insert_current_period = ("INSERT INTO current_period "
							"(month, year) "
						 "VALUES (%(month)s, %(year)s)")
delete_current_month_hours = ("DELETE FROM monthly_input "
                               "WHERE input_type='HOURS'")
		
select_employees = ( "SELECT * "
                       "FROM employee e, "
                            "profile p, "
                            "landi_value lv, "
                            "current_period cp "
 					  "WHERE e.id = p.employee_id "
   							"and p.landi_category = lv.category "
   							"and lv.year = cp.year " )
   							
delete_current_input = ( "DELETE FROM monthly_input "
                           "WHERE employee_id=%(employee_id)s AND "
                                "input_type=%(input_type)s" )

insert_current_input = ( "INSERT INTO monthly_input "
							"(employee_id, input_type, value) "
							"VALUES "
							"(%(employee_id)s, %(input_type)s, %(value)s)")
							
select_employee_inputs = ("select mi.employee_id, "
                                 "mi.input_type, "
                                 "mi.value "
                            "from monthly_input mi "
                           "where employee_id = %(employee_id)s")
                           
employees = {}
results = {}

def build_employee_dict():
	cnx = mysql.connector.connect(**config)
	cursor = cnx.cursor()
	cnx2 = mysql.connector.connect(**config)
	cursor2 = cnx2.cursor()
	cursor.execute(select_employees)
	
	for row in cursor:
		cursor2.execute(select_employee_inputs, {'employee_id': row[0]})
		employees[row[0]] = {
			'id':row[0], 
			'name':row[1],
			'landiType': row[3],
			'landiValue': row[8],
			'employeeType': row[4],
			'rate': row[5],
			'hours': row[6], 
			'inputs':[{'type':i[1], 'value':i[2]} for i in cursor2] }
	
	cursor.close()
	cnx.close()
	cursor2.close()
	cnx2.close()

def set_current_period(month, year):
	cnx = mysql.connector.connect(**config)
	cursor = cnx.cursor()
	
	try:
		cursor.execute(delete_current)
		cursor.execute(delete_current_month_hours)
		current_period_data = {
			'month' : month,
			'year' : year
		}
		
		cursor.execute(insert_current_period, current_period_data)
		cnx.commit()
	finally:
		cursor.close()
		cnx.close()

def set_current_input(employee_id, input_type, value):
	cnx = mysql.connector.connect(**config)
	cursor = cnx.cursor()
	
	try:
		cursor.execute(delete_current_input, {'employee_id': employee_id, 'input_type': input_type})
		
		insert_current_input_data = {
			'employee_id' : employee_id,
			'input_type' : input_type,
			'value': value
		}
		
		cursor.execute(insert_current_input, insert_current_input_data)
		cnx.commit()
	finally:
		cursor.close()
		cnx.close()
		
def validate_employee_dict():
	for e in employees.itervalues():
		inputs = e['inputs']
		for i in inputs:
			if i['type'] == 'HOURS':
				e['hours'] = float(i['value'])
		

def calculate_current():
	validate_employee_dict()

def main(argv):
	try:	
		opts, args = getopt.getopt(argv, "cli:m:t:y:v:", ["calculate-current", "list", "id=", "input-type=", "month=", "year=", "value=" ])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	
	id = 0
	month = 0
	year = 0
	value = 0
	input_type = ""
	for opt, arg in opts:
		if opt in ("-l", "--list"):
			build_employee_dict()
			print employees
			return
		elif opt in ("-c", "--calcuilate-current"):
			build_employee_dict()
			calculate_current()
			print employees
			return
		elif opt in ("-i", "--id"):
			id = int(arg)
		elif opt in ("-y", "--year"):
			year = int(arg)
		elif opt in ("-m", "--month"):
			month = int(arg)
		elif opt in ("-v", "--value"):
			value = float(arg)
		elif opt in ("-t", "--input-type"):
			input_type = arg
	
	if (year > 0 and month > 0):
		print month
		print year
		set_current_period(month, year)
	elif (len(input_type) > 0 and id > 0):
		set_current_input(id, input_type, value)
	else:
		print "Usage:"
		print "  --list (-l), list employees"
		print "  --calculate-current (-c)"
		print "  --month (-m) [01-12] --year (-y) [year], set month and year for current period"
		print "  --id (-i) [id] --input-type (-t) ['FB' (FICA Bonus) | 'RW' (Retirement Witholding) | 'HOURS' | 'S' (SICK LEAVE USED) | 'MIW' (Medical Insurance Witholding)] --value [value]"
		
if __name__ == "__main__":
	main(sys.argv[1:])

