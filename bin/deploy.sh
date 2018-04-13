#!/usr/bin/env bash

/bin/bash ./bin/shutdown.sh

git pull origin master

/bin/bash ./bin/update_env.sh

/bin/bash ./bin/run.sh &
