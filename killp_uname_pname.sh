#!/bin/bash

# author : Pik-Mai Hui (huip@indiana.edu)
# usage  : ./killp_uname_pname.sh username process_name
# example: ./killp_uname_pname.sh huip python
# purpose: terminate all processes with process_name owned by username

/bin/ps aux | \
    grep "$1" | \
    grep -e "$2\t*" | \
    /bin/awk '{print $2}' | \
    /usr/bin/xargs kill -15
