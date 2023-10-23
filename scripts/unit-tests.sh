#! /bin/bash

# fail on first error
set -e
# This script runs python unit tests
#
APPLICATION_DIR=application
APPLICATION_UTIL_DIR=application-utils
APPLICATION_TEST_DIR='tests/unit'

#  now clear down copied test code after testing
for path in "$APPLICATION_DIR"/*/ ; do
    dirs=$(echo "$path" | tr "\/" '\n')
    for dir in $dirs
        do
            if [ -d $APPLICATION_DIR/"$dir"/test/ ]; then
                echo "Clearing down temp test files for $dir"
                rm -rf $APPLICATION_DIR/"$dir"/test
                rm -rf $APPLICATION_DIR/"$dir"/chalicelib/common
            fi
        done
done

# find each directory under application
# if test code exists copy it in prep for running it
# TODO get second element of the array
pip install -r $APPLICATION_TEST_DIR/requirements.txt
for path in "$APPLICATION_DIR"/*/ ; do
    dirs=$(echo "$path" | tr "\/" '\n')
    for dir in $dirs
        do
            if ! [ "$dir" == $APPLICATION_DIR ] ; then
                echo "Preparing tests for $dir"
                mkdir $APPLICATION_DIR/"$dir"/test
                mkdir $APPLICATION_DIR/"$dir"/chalicelib/common
                if [ -d $APPLICATION_TEST_DIR/"$dir" ]; then
                    echo "Copying tests for $dir"
                    cp $APPLICATION_TEST_DIR/"$dir"/* $APPLICATION_DIR/"$dir"/test/
                    cp -r $APPLICATION_UTIL_DIR/* $APPLICATION_DIR/"$dir"/chalicelib/
                    coverage run -a --source=$APPLICATION_DIR/"$dir"  -m pytest $APPLICATION_DIR/"$dir"
                fi
            fi
        done
done

#  use requirements defined for tests/unit
#pip install -r $APPLICATION_TEST_DIR/requirements.txt
#coverage run --source=$APPLICATION_DIR  -m pytest $APPLICATION_DIR/*
coverage report
coverage html

#  now clear down copied test code after testing
for path in "$APPLICATION_DIR"/*/ ; do
    dirs=$(echo "$path" | tr "\/" '\n')
    for dir in $dirs
        do
            if [ -d $APPLICATION_DIR/"$dir"/test/ ]; then
                echo "Clearing down temp test files for $dir"
                rm -rf $APPLICATION_DIR/"$dir"/test
                rm -rf $APPLICATION_DIR/"$dir"/chalicelib/common
            fi
        done
done

