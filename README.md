# Object-Detector-App

A real-time object recognition application using [Google's TensorFlow Object Detection API](https://github.com/tensorflow/models/tree/master/research/object_detection) and [OpenCV](http://opencv.org/).

## Getting Started
1. `conda env create -f environment.yml`
2. `conda install pip`. If you already have pip, you will need to `source deactivate` first and then run `conda install pip`       to make sure there are no errors which will occur in the OS
2. To see where the source of your pyhton files that you are running are, use `which python`
3. If it is not where you have installed the conda environment, you need to change the source for python
    a. `vim environment.yml` and look at the first line of the file which should say something like `name: object-detection`.         We are interested in the object-detection part, so remember that.
    b. `source activate name` where name will be replaced with what was stated in your environment.yml file
    c. `which python` and this time the place where you installed conda will show up
3. `python object_detection_app.py`
    Optional arguments (default value):
    * Device index of the camera `--source=0`
    * Width of the frames in the video stream `--width=480`
    * Height of the frames in the video stream `--height=360`
    * Number of workers `--num-workers=2`
    * Size of the queue `--queue-size=5`

## Tests
```
pytest -vs utils/
```

## Requirements
- [Anaconda / Python 3.5](https://www.continuum.io/downloads)
- [TensorFlow 1.2](https://www.tensorflow.org/)
- [OpenCV 3.0](http://opencv.org/)

## Notes
- OpenCV 3.1 might crash on OSX after a while, so that's why I had to switch to version 3.0. See open issue and solution [here](https://github.com/opencv/opencv/issues/5874).
- Moving the `.read()` part of the video stream in a multiple child processes did not work. However, it was possible to move it to a separate thread.

## Copyright

See [LICENSE](LICENSE) for details.
Copyright (c) 2017 [Dat Tran](http://www.dat-tran.com/).