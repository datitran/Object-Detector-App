# Object-Detector-App

A real-time object recognition application using [Google's TensorFlow Object Detection API](https://github.com/tensorflow/models/tree/master/research/object_detection) and [OpenCV](http://opencv.org/).

## Getting Started
1. `conda env create -f environment.yml`
2. `conda install pip`. 
    *If you already have pip, you will need to `source deactivate` first and then run `conda install pip` to make sure there        are no errors which will occur in the OS
3. To see where the source of your pyhton files that you are running are, use `which python`
4. If it is not where you have installed the conda environment, you need to change the source for python
    * `vim environment.yml` and look at the first line of the file which should say something like `name: object-detection`.         We are interested in the name of the file.
    * `source activate name` where name will be replaced with what was stated in your environment.yml file
    * `which python` and this time the place where you installed conda will show up
5. `python object_detection_app.py`
    Optional arguments (default value):
    * Show all commands `--help`
    * Device index of the camera `--source=0`
    * Width of the frames in the video stream `--width=480`
    * Height of the frames in the video stream `--height=360`
    * Number of workers `--num-workers=2`
    * Size of the queue `--queue-size=5`
    * URL for video stream `--url=<rstp://...>`
    * Turn on GUI (defaulted to run headless) `--gui`
    * Turn on vocal commands on MacOS (defaulted to silent) `--say`
    * State Buffer Size, how many "states" to capture `--state-queue-size=5`

## Development
### Updating the environment
`conda env update -f environment.yml`

### Tests
```
pytest -vs utils/
python -m pytest
python -m unittest discover -s object_detection -p "*_test.py"
```

### Requirements
- [Anaconda / Python 3.5](https://www.continuum.io/downloads)
- [TensorFlow 1.2](https://www.tensorflow.org/)
- [OpenCV 3.0](http://opencv.org/)

### API 
Our API is accessible via the MQTT protocol.

#### Android --> Chloe `dev/chloe/explorer/<userid>/statement`
We subscribe to a topic coming from an Android client. Incoming messages should be encoded as JSON objects that match
the following format: 

```json
{
  "messageId": 123,
  "serviceId": 53453,
  "userId": 4823942,
  "timestamp": 1234123412341234,
  "statement": "describe what is going on around me" 
  //...
}
```


#### Any --> Explorer `dev/chloe/explorer/<userid>/response`

Messages should be encoded as JSON objects in the following format: 

```json
{
  "messageId": 124, // ID for the current payload
  "statementId": 123, // ID of statement payload (payload this is in response to, see above)
  "timestamp": 1234123412341234,

  // Was the service successful?
  "status": {
    "code": "ch-vis-000", // <project code>-<module code>-<error/status code>
    "message": "success" 
  },
  
  "action": "say",
  "args": ["arg1", "arg2", "arg3"], // **Prefer kwargs to args**
  "kwargs": {
    "confidence": 0.87,  // argument that should always be present
    "source": "chloe" // or "human", should always be present
    "key1": 1,
    "key2": "kwarg2"
  },
  
  //...
}
```

TODO(Alex) Revise
Here is an example of a response for "say":
Topic: `dev/chloe/explorer/12345/response`
Payload: 
```json
{
  "messageId": 124, 
  "statementId": 123,
  "timestamp": 1234123412341234,
  "status": {
    "code": "ch-vis-000",
    "message": "success" 
  },
  "action": "say",
  "args": [], 
  "kwargs": {
    "confidence": 0.87,
    "source": "chloe"
    "text": "there is 1 person and a chair around you",
    "wordsPerMin": 200,
    "voiceGender": "Female"
  }
}
```
#### Chloe --> Test Harness/Agent `dev/chloe/agent/<userid>/response`
The test harness gets the same message as the above section.

### Agent-Chloe Experiment Configuration Discussion
- Should be configured on dashboard. 
- Response to explorer should have a delay, whether they come from Chloe or the AI. The explorer should not be able to distinguish between human and machine. 
- Want to design intentional fallback from the AI to the Human agent. Thus, we need two buttons: the random send (either AI or Human), and a **SEND!** that forcibly sends the human response over the AI. 

## Notes
- ~~OpenCV 3.1 might crash on OSX after a while, so that's why I had to switch to version 3.0. See open issue and solution [here](https://github.com/opencv/opencv/issues/5874).~~
- Moving the `.read()` part of the video stream in a multiple child processes did not work. However, it was possible to move it to a separate thread.

## Copyright
See [LICENSE](LICENSE) for details.
