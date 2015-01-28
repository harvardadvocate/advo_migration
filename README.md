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
Create a new database for your drupal import called advocate_old. 
```
mysql -u root -p
CREATE DATABASE advocate_old
quit
```
# Import the drupal advocate database

Download a copy of the drupal database from the Google Drive folder ```/Advocate Website/Database/advocate_drupal_old.sql```. To import it, navigate to the directory containing the file, and then run:

```
mysql -u root -p advocate_old < advocate_drupal_old.sql
```
This will take a while because it's a large file. 

# Run the migration script
Make sure you have a backup of your old database and that magazine app is on migration 0004. You can run ```./manage.py migrate magazine 0004``` just to be sure. Also make sure you're in your virtual env before running the migration script ```workon advocateonline```. 
```
python migration.py
```
# Errors
If you get the following error:
```
_mysql_exceptions.OperationalError: (1054, "Unknown column 'photo' in 'field list'")
```
Then you should do the following:
```
./manage.py migrate magazine 0003 --fake
./manage.py migrate magazine 0004
```
You will need to update the magazine_issues table because all the years and seasons are incorrect. 

