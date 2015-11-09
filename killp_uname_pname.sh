#!/bin/bash

# author : Pik-Mai Hui (huip@indiana.edu)
# usage  : ./killp_uname_pname.sh username process_name
# example: ./killp_uname_pname.sh huip python
# purpose: terminate all processes with process_name owned by username

ps aux | \ # list all running processes
    grep "$1" | \ # grep process by name
    grep -e "$2\t*" | \ # grep only process by the specified user by name
    awk '{print $2}' | \ # select only the pid column
    xargs kill -15 # pip arguments into kill command with term signal
