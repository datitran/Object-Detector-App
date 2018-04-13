#!/usr/bin/env bash


source activate object-detection

date &>> log.txt
python object_detection_app.py -u=rtsp://52.39.224.108:1935/live/myStream &>> log.txt
