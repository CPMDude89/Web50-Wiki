from cs50 import SQL
import sys
import csv
import string

if len(sys.argv) != 2:
    sys.exit("Please include only characters.csv")

in_file = sys.argv[1]
db = SQL("sqlite:///students.db")

with open(in_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        #---------------------names----------------------------
        name = row['name'].split()
        if len(name) == 2:
            first = name[0]
            middle = None
            last = name[1]

        if len(name) == 3:
            first = name[0]
            middle = name[1]
            last = name[2]

        #---------------------house-------------------------
        house = row['house']

        #---------------------birth year--------------------
        birth = row['birth']

        db.execute("INSERT INTO students (first, middle, last, house, birth) VALUES (?,?,?,?,?)", first, middle, last, house, birth)
