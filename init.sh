#!/bin/sh

cd ~/mitrejse
nohup python mitrejse.py 1414  > $( mktemp /tmp/mitrejse.XXXX ) &
