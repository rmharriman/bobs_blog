#!/usr/bin/env bash

echo removed old db
rm /tmp/dev.db

echo removed old migrations
rm -r $MIGRATIONS

echo activating virtualenv
source $BLOG_VENV/bin/activate

echo setting up dev db
$BLOG_HOME/manage.py db init

$BLOG_HOME/manage.py db migrate -m "initial migration"

$BLOG_HOME/manage.py db upgrade

$BLOG_HOME/dev_refresh.py