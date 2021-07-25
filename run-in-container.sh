#!/bin/sh
docker run --rm -eDISPLAY=$DISPLAY \
-v /tmp/.X11-unix:/tmp/.X11-unix \
--network=host \
open-command-and-control:dev \
/bin/bash