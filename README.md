# Object-Detector-App

A real-time object recognition application using [Google's TensorFlow Object Detection API](https://github.com/tensorflow/models/tree/master/research/object_detection) and [OpenCV](http://opencv.org/).

## Getting Started

1. Install Anaconda according to the instructions [here](https://docs.anaconda.com/anaconda/install/).

2. Make sure your python package installer, `pip`, is updated to use the Anaconda version:

```bash
$ conda install pip
```

3. Clone the repo to your local machine in whatever folder you use to hold source code, like ~/src/

```bash
$ mkdir ~/src
$ cd ~/src
$ git clone https://github.com/aira/object_detector_app
$ cd object_detector_app
```

4. Create a new Anaconda environment on your machine to hold tensorflow, python 3.5, OpenCV, etc. This will take a while:

`conda env create -f environment.yml`

5. Check to make sure you're using the python that's in your conda environment

`which python` should have a path that indicates anaconda and the object-detection environment.

If it is not in a folder with your conda environment name (`object-detection` is the default), you need to activate your environment:

```markdown
    5.1 `head environment.yml` -- 1st line should say something like `name: object-detection`  
    5.2 `source activate object-detection` -- replace `object-detection` with your environment name   
    5.3 `which python` -- make sure this is now correctly pointing to your conda environment path  
```

6. Start the app!

```markdown
    6.1 `python object_detection_app.py --help` to see all the options   
    6.2 `python object_detection_app.py` to run it using your webcam but no GUI or verbalization
```

## Development

### Updating the environment

`conda env update -f environment.yml`

### Tests

```bash
$ pytest -vs utils/
$ python -m pytest
$ python -m unittest discover -s object_detection -p "*_test.py"
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

```javascript
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

```javascript
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

#### Example Chloe Response . **TODO:** Revise

Here is an example of a response for "say":

Topic: `dev/chloe/explorer/12345/response`

Payload:

```javascript
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

* Should be configured on dashboard.  
* Responses to the explorer should have a similar delay, whether they come from Chloe or the AI. The explorer should not be able to distinguish between human and machine.  
* Want to design intentional fallback from the AI to the Human agent. Thus, we need two buttons:

1. the random send (either AI or Human)
2. **SEND!** that forcibly sends the human response over the AI.  

## Copyright

See [LICENSE](LICENSE) for details.
