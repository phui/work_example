#!/bin/bash

# author: Pik-Mai Hui (huip@indiana.edu)
# usage: ./index_edgelist.sh network.edgelist node.index
# This script takes an edgelist and index all node_id inside
# This is useful if network analysis tool force you to use
#   signed integer node id instead of string, since in that
#   case it is likely that integer overflow will happen

cat "$1" | \
    awk '{print $1}; {print $2}' | \
    sort -n | \
    uniq | \
    awk '{print NR "\t" $0}' \
    > "$2"
