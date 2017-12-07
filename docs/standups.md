# Standups

## Standup 1

### Hobson

* Researched Watson for NLP and Grow for analytics. Researched time series forecasting and recruited a DS contractor.
* max count filter on objects seen, research knowledge graphs, data structure for storing "radar"
* no blockers

### Alex

* got streaming to openCV working by install ffmpeg
* working on docker container. considering installing anaconcda despite the double-containerism (reducndant namespacing)

### Ashwin

libstreaming library crashing on android emulator (android studio) faster pro emulator, and also fails on phone

### Parking lot

* knowledge graphs are NoSQL connections between facts. Any nosql database can store them. I'm using a dict of dicts for now.
* Alex decided to pursue the minimum viable docker container
* will work with Sujeeth and Bala to deploy the container to AWS


## Standup 2

### Alex

* Wowza working, pulling from the right Anaconda package. Pushed to master a version that takes a url working
* Jenkins build

### Ashwin

* stream is working on android except camera permissions, has dialog box from another app make that work
* finish camera permissions dialog box

## Sujeeth 

* help Ashwin integrate wowza streamer into the OCR app

### parking lot

* permissions problem only happens with first install of the app, not with each new release, so that's good
* RTSP server: link had `rtsp://prod*pemdosa*{servernum}:{port}/live/stream` example urls only have server num and port, 
* alex forgot to send link to gennymotion -- rapid android emulation
* talk about CI, sh scripts that call python scripts
* CICD apps released through bitrise 
