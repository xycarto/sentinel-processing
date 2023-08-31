#!/bin/bash

# create snappy and python binding with snappy
/usr/local/snap/bin/snappy-conf /usr/bin/python3 2>&1 | while read -r line; do
    echo "$line"
    if [ "$line" = "or copy the 'snappy' module into your Python's 'site-packages' directory." ]
    then
      echo "Ok"
      sleep 2
      echo "Stopping Now"
      pkill -TERM -f java
    fi
done