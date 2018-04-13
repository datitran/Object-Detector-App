import time
import argparse
import multiprocessing

import numpy as np
import cv2
import tensorflow as tf

from utils.app_utils import FPS, WebcamVideoStream
from multiprocessing import Queue, Pool
from object_detection.utils import visualization_utils as vis_util
from nlp import describe_scene, say, update_state
from nlp.dispatch import mqttc, dispatcher
from nlp.command import DescribeScene, DescribeObjectColor


from object_detection.constants import CATEGORY_INDEX, PATH_TO_CKPT


def detect_objects(image_np, sess, detection_graph, _state_q, voice_on=False):
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

    # Each box represents a part of the image where a particular object was detected.
    boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

    # Each score represent how level of confidence for each of the objects.
    # Score is shown on the result image, together with the class label.
    scores = detection_graph.get_tensor_by_name('detection_scores:0')
    classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    # Actual detection.
    (boxes, scores, classes, num_detections) = sess.run(
        [boxes, scores, classes, num_detections],
        feed_dict={image_tensor: image_np_expanded})

    # Visualization of the results of a detection.
    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        CATEGORY_INDEX,
        use_normalized_coordinates=True,
        line_thickness=8)

    # Describe the image
    object_vectors = update_state(image=image_np, boxes=np.squeeze(boxes),
                                  classes=np.squeeze(classes).astype(np.int32),
                                  scores=np.squeeze(scores), category_index=CATEGORY_INDEX)

    # Persists image state (list of object vectors for that image) in a queue
    _state_q.put(object_vectors)

    # FIXME: this should not be happening here, but should be happening in the commands.py executive logic
    description = describe_scene(object_vectors)
    if voice_on:
        say(description)
    return image_np


detect_objects.state = []  # poor man's class/object


def worker(input_q, output_q, state_q, voice_on=False):
    # Load a (frozen) Tensorflow model into memory.
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

        sess = tf.Session(graph=detection_graph)

    fps = FPS().start()

    while True:
        fps.update()
        frame = input_q.get()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if state_q.full():
            state_q.get()
            state_q.get()

        output_q.put(detect_objects(frame_rgb, sess, detection_graph, state_q, voice_on=voice_on))

    fps.stop()
    sess.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-src', '--source', dest='video_source', type=int,
                        default=0, help='Device index of the camera.')
    parser.add_argument('-u', '--url', dest='video_stream_source', type=str,
                        help='Url for rtsp stream. Don\'t use with `-src` argument')
    parser.add_argument('-wd', '--width', dest='width', type=int,
                        default=480, help='Width of the frames in the video stream.')
    parser.add_argument('-ht', '--height', dest='height', type=int,
                        default=360, help='Height of the frames in the video stream.')
    parser.add_argument('-num-w', '--num-workers', dest='num_workers', type=int,
                        default=2, help='Number of workers.')
    parser.add_argument('-q-size', '--queue-size', dest='queue_size', type=int,
                        default=5, help='Size of the queue.')
    parser.add_argument('-g', '--gui', action='store_true', default=False, dest='gui',
                        help='Show a GUI/Graphics, or run headless.')
    parser.add_argument('-s', '--say', action='store_true', default=False, dest='voice_on',
                        help='Say commands on local computer (for debugging)')
    parser.add_argument('-sq-size', '--state-queue-size', dest='state_queue_size', type=int,
                        default=5, help='Size of the object detection state queue size.')
    args = parser.parse_args()

    logger = multiprocessing.log_to_stderr()
    logger.setLevel(multiprocessing.SUBDEBUG)

    input_q = Queue(maxsize=args.queue_size)
    output_q = Queue(maxsize=args.queue_size)
    state_q = Queue(maxsize=args.state_queue_size)

    dispatcher['color'] = DescribeObjectColor(state_q)
    dispatcher['describe'] = DescribeScene(state_q)

    pool = Pool(args.num_workers, worker, (input_q, output_q, state_q, args.voice_on))

    disp_graphics = args.gui
    source = args.video_stream_source

    if source is None:
        source = args.video_source

    video_capture = WebcamVideoStream(src=source,
                                      width=args.width,
                                      height=args.height).start()
    fps = FPS().start()

    rc = 0  # mqtt client status. Error if not zero
    while True:  # fps._numFrames < 120

        t = time.time()

        if video_capture.stream.isOpened():
            frame = video_capture.read()

            if frame is None:
                continue

            input_q.put(frame)

            output_rgb = cv2.cvtColor(output_q.get(), cv2.COLOR_RGB2BGR)
            if disp_graphics:
                cv2.imshow('Video', output_rgb)
            fps.update()
        else:
            video_capture.stream.open(source)

        print('[INFO] elapsed time: {:.2f}'.format(time.time() - t))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if rc is 0:
            rc = mqttc.loop()
        else:
            print('[ERROR] MQTT Connection error!')

    fps.stop()
    print('[INFO] elapsed time (total): {:.2f}'.format(fps.elapsed()))
    print('[INFO] approx. FPS: {:.2f}'.format(fps.fps()))

    pool.terminate()
    video_capture.stop()
    if disp_graphics:
        cv2.destroyAllWindows()
