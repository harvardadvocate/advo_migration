import MySQLdb
import urllib

db = MySQLdb.connect(host="localhost",user="root",
                  passwd="",db="advocate")


db.query("""SELECT * FROM magazine_image""")
foo = db.use_result()
while True:

  row = foo.fetch_row()
  # print row[0]
  if not row:
    break
  # The problem is the one that start with images are incorrect
  # if "images" in row[0][1]:
  #   print row[0][1]
  #   word =  row[0][1].split("_")[1]
  #   site = "sites/default/files/" + word
  #   print site

  if row[0]
    urllib.urlretrieve("http://www.theharvardadvocate.com/"+row[0][1], row[0][1])



