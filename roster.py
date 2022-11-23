from cs50 import SQL
import sys
import csv
import string

if len(sys.argv) != 2:
    sys.exit("Please only include house")

in_house = sys.argv[1]
db = SQL("sqlite:///students.db")

students_names = db.execute("SELECT DISTINCT first, middle, last, birth FROM students WHERE house=? ORDER BY last, first", in_house)
#print(students_names)
for person in students_names:
    first = person['first']
    middle = person['middle']
    last = person['last']
    birth = person['birth']

    if middle is not None:
        print(f"{first} {middle} {last}, born {birth}")
    if middle is None:
        print(f"{first} {last}, born {birth}")