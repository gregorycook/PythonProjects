import csv


def merge_file(result, csv_file, column_names, key_field):
    for row in csv_file:
        append_dict = None

        # look up merge row with the key_field, create it if not already there
        key = row[key_field]
        if key in result:
            append_dict = result[key]
        else:
            append_dict = {}
            result[key] = append_dict

        # set all of the vaules on the merge row from the file row
        for column in row:
            append_dict[column] = row[column]

            # ensure this column name is in the list
            column_names[column] = None


key_field = 'Name'

file1 = open("mergefile1.csv")
csv_file1 = csv.DictReader(file1)

file2 = open("mergefile2.csv")
csv_file2 = csv.DictReader(file2)

# add rows from both files to dict
merged = {}
column_names = {}
merge_file(merged, csv_file1, column_names, key_field)
merge_file(merged, csv_file2, column_names, key_field)

# note: it is not clear in what order the columns will be
column_names = [column for column in column_names]

merge_file = open("merged.csv", "w")
merged_file_csv = csv.DictWriter(merge_file, column_names)
merged_file_csv.writeheader()

# write all of the rows to the output file
for key in merged:
    row = merged[key]
    merged_file_csv.writerow(row)
