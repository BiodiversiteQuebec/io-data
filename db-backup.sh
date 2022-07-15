#/bin/bash
#
# PostgreSQL backup script
#
# Use cron to schedule this script to run as frequently as you want.
###################################################################################


# User with SELECT, SHOW VIEW, EVENT, and TRIGGER, or... root

# Archive path
ARCHIVE_PATH="/db-backups"

# Archive filename
ARCHIVE_FILE="coleo-db_`date +%F_%H-%M-%S`.tbz2"

# Archives older than this will be deleted
ARCHIVE_DAYS="30"

# Set or override config variables here
if [ -e $SYSCONFIG ]; then
        . $SYSCONFIG
fi

# Change working directory
cd $ARCHIVE_PATH

# Get all of the databases
# Use Nice to dump the database
#sudo su postgres
nice pg_dump -U postgres coleo > coleo-db.sql

# Use Nice to create a tar compressed with bzip2
nice tar -cjf $ARCHIVE_FILE *.sql

# Remove the SQL files
nice rm -rf *.sql

# Remove old archive files
nice find *.tbz2 -mtime +$ARCHIVE_DAYS -exec rm {} \;

# copy files to S3 storage
s3cmd sync /db-backups/ s3://bq-sql-backup/coleo/
