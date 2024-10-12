#!/bin/bash

# Creates following dir tree
# actors-app
# ├── app
# │   ├── actors_app
# |   ├── pdf_app
# │   └── .venv
# ├── wsgi
# │   └── wsgi.py
# ├── static
# |   ├── favicon.ico
# |   └── pdf_app
# ├── .tmp
# │   └── ...
# ├── deps
# │   └── ...
# └── db
#     └── ... 


set -e

APACHE_PATH_TO_SITE=/var/www/actors-app
SCRIPT=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT")
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")

echo "Clearing content of ${APACHE_PATH_TO_SITE}..."
rm -rf $APACHE_PATH_TO_SITE

echo "Creating directories in ${APACHE_PATH_TO_SITE}..."
mkdir -p $APACHE_PATH_TO_SITE/app
mkdir -p $APACHE_PATH_TO_SITE/wsgi

echo "Copying files from ${PROJECT_ROOT} to ${APACHE_PATH_TO_SITE}"

STATIC_PATH=$PROJECT_ROOT/pdf_app/static
echo "${STATIC_PATH}..."
cp -r $STATIC_PATH $APACHE_PATH_TO_SITE

VENV_PATH=$PROJECT_ROOT/.venv
echo "${VENV_PATH}..."
cp -r $VENV_PATH $APACHE_PATH_TO_SITE/app

WSGI_PATH=$PROJECT_ROOT/actors_app/wsgi.py
echo "${WSGI_PATH}..."
cp $WSGI_PATH $APACHE_PATH_TO_SITE/wsgi/

ACTORS_APP_PATH=$PROJECT_ROOT/actors_app
echo "${ACTORS_APP_PATH}"
cp -r $ACTORS_APP_PATH $APACHE_PATH_TO_SITE/app

PDF_APP_PATH=$PROJECT_ROOT/pdf_app
echo "${PDF_APP_PATH}"
cp -r $PDF_APP_PATH $APACHE_PATH_TO_SITE/app

echo "Creating tmp and db dirs..."
mkdir -p $APACHE_PATH_TO_SITE/.tmp
mkdir -p $APACHE_PATH_TO_SITE/db

# TODO only temporary solution
echo "Copying database..."
cp /home/mateusz/projects/actors_app/.tmp/db.sqlite3 /var/www/actors-app/db
cp -r $PROJECT_ROOT/.db/* /var/www/actors-app/db/

echo "Copying deps..."
cp -r $PROJECT_ROOT/.deps /var/www/actors-app/deps

echo "Setting files permissions..."

chown -R mateusz $APACHE_PATH_TO_SITE
chgrp -R www-data $APACHE_PATH_TO_SITE
chmod -R 750 $APACHE_PATH_TO_SITE
chmod g+s $APACHE_PATH_TO_SITE
chmod -R g+w $APACHE_PATH_TO_SITE/.tmp
chmod -R g+w $APACHE_PATH_TO_SITE/db

echo "Restarting Apache service..."
systemctl restart apache2.service