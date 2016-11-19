#!/usr/bin/env bash

echo removed old db
rm /tmp/dev.db

echo removed old migrations
rm -r ~/Documents/code/new_blog/migrations

echo activating virtualenv
source ~/Documents/code/new_blog/new_blog_venv/bin/activate

echo setting up dev db
~/Documents/code/new_blog/manage.py db init

~/Documents/code/new_blog/manage.py db migrate -m "initial migration"

~/Documents/code/new_blog/manage.py db upgrade

~/Documents/code/new_blog/dev_refresh.py