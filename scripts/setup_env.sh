#!/bin/bash

set -e

SCRIPT=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT")
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")
VENV_PATH=$PROJECT_ROOT/.venv

echo "Creating venv in $VENV_PATH..."
if [ -d $VENV_PATH ]; then
  read -p "'$VENV_PATH' already exists. Do you want to override it? (Y/n): " confirm && [[ $confirm == [yY] ]] || exit 1
fi

rm -rf $VENV_PATH
python3.11 -m venv $VENV_PATH
$VENV_PATH/bin/python -m pip install -r $PROJECT_ROOT/requirements.txt

DB_PATH=$PROJECT_ROOT/.db
echo "Creating database dirs in $DB_PATH"
if [ -d $DB_PATH ]; then
  read -p "'$DB_PATH' already exists. Do you want to override it? (Y/n): " confirm && [[ $confirm == [yY] ]] || exit 1
fi

rm -rf $DB_PATH
mkdir -p $DB_PATH/pickled_scenarios

echo "Setting up piper..."
DEPS_PATH=$PROJECT_ROOT/.deps
rm -rf $DEPS_PATH

PIPER_TMP_PATH=/tmp/piper
rm -rf $PIPER_TMP_PATH
mkdir -p $PIPER_TMP_PATH
PIPER_DOWNLOAD_SRC=https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz
PIPER_TAR=$PIPER_TMP_PATH/package.tar.gz
wget -O $PIPER_TAR $PIPER_DOWNLOAD_SRC

ACTUAL_MD5_SUM=$(md5sum -b $PIPER_TAR)
EXPECTED_MD5_SUM="18b676a612911cd8c0cb7ff5dbad6421 *$PIPER_TAR"
if [[ $ACTUAL_MD5_SUM != $EXPECTED_MD5_SUM ]]; then
    echo -e "MD5 sum of file downloaded from $PIPER_DOWNLOAD_SRC doesn't match expected checksum!"
    exit 1
fi

tar -xf $PIPER_TAR -C $PIPER_TMP_PATH
mkdir -p $DEPS_PATH
cp -r $PIPER_TMP_PATH/piper $DEPS_PATH/piper

echo "Making migrations..."
$VENV_PATH/bin/python manage.py migrate
