This script migrates the contents of the advocate drupal database (advocate_old) to the
advocate django database. This is only guaranteed to work if content app is on migration 0004. The first thing this script does is drop django tables, so make sure you have a backup of your database on hand. This script assumes that your django database name is advocate.

# Clone the repo
```
git clone https://github.com/harvardadvocate/advo_migration
```
Once you've cloned the repo, go to the bottom of the file ```migration.py``` to line 228 and edit the settings to match your local settings. 
```
con = MySQLdb.connect('localhost', 'root', '', 'advocate_old')
```
Create a new database for your drupal import called advocate_old and a database for your new django database
```
mysql -u root -p
CREATE DATABASE advocate_old
CREATE DATABASE advocate
quit
```
# Import the drupal advocate database

Download a copy of the drupal database from the Google Drive folder ```/Advocate Website/Database/advocate_drupal_old.sql```. To import it, navigate to the directory containing the file, and then run:

```
mysql -u root -p advocate_old < advocate_drupal_old.sql
```
This will take a while because it's a large file. 

# Make sure the magazine app is on migration 0004. 
```
./manage.py syncdb
./manage.py migrate magazine 0001
./manage.py migrate magazine 0003 --fake
./manage.py migrate magazine 0004
```

# Run the migration script
Make sure you're in your virtual env before running the migration script ```workon advocateonline```. 
```
python migration.py
```
Be sure to delete your database password after you run the migration script. 

# Errors

You will need to update the magazine_issues table because all the years and seasons are incorrect. The updated magazine_issues table is also in Google Drive, in the same database advocate_old is uploaded to.

 