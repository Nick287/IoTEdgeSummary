import logging
from PIL import Image, ImageDraw
import io
import numpy as np
# import cv2 as cv
import inferencing_pb2
import media_pb2
import extension_pb2

import json
import tensorflow as tf
import cv2
import numpy as np
# from tensorflow.compat.v1 import ConfigProto
from tensorflow.python.saved_model import tag_constants
from datetime import datetime
from ai_model_path import AI_Model_Path

class ProcessImages():

    def _get_class_names(self, obj_names_path):
        names = {}
        with open(obj_names_path, 'r') as data:
            for ID, name in enumerate(data):
                names[str(ID)] = name.strip('\n')
        return names



    def filter_boxes(self, box_xywh, scores, score_threshold=0.4, input_shape=tf.constant([416, 416])):
        scores_max = tf.math.reduce_max(scores, axis=-1)

        mask = scores_max >= score_threshold
        class_boxes = tf.boolean_mask(box_xywh, mask)
        pred_conf = tf.boolean_mask(scores, mask)
        class_boxes = tf.reshape(class_boxes, [tf.shape(scores)[0], -1, tf.shape(class_boxes)[-1]])
        pred_conf = tf.reshape(pred_conf, [tf.shape(scores)[0], -1, tf.shape(pred_conf)[-1]])

        box_xy, box_wh = tf.split(class_boxes, (2, 2), axis=-1)

        input_shape = tf.cast(input_shape, dtype=tf.float32)

        box_yx = box_xy[..., ::-1]
        box_hw = box_wh[..., ::-1]

        box_mins = (box_yx - (box_hw / 2.)) / input_shape
        box_maxes = (box_yx + (box_hw / 2.)) / input_shape
        boxes = tf.concat([
            box_mins[..., 0:1],  # y_min
            box_mins[..., 1:2],  # x_min
            box_maxes[..., 0:1],  # y_max
            box_maxes[..., 1:2]  # x_max
        ], axis=-1)
        # return tf.concat([boxes, pred_conf], axis=-1)
        return (boxes, pred_conf)
    
    def detect_object(self, opened_image):
        IOU = 0.5
        SCORE = 0.75
        results = []
        try:
            model_full_path = AI_Model_Path.Get_Model_Path()
            if(model_full_path == ""):
                logging.info("################ PLEASE SET AI MODEL FIRST")
                logging.info("############## ############## END ############## ##############")
                return results
            logging.info("############## AI MODEL PATH: " + model_full_path)
            if '.tflite' in model_full_path:
                interpreter = tf.lite.Interpreter(model_path=model_full_path)
                interpreter.allocate_tensors()
                input_details = interpreter.get_input_details()
                output_details = interpreter.get_output_details()
                print("############## input_details ##############")
                print(input_details)
                print("############## output_details ##############")
                print(output_details)
                print()
                input_shape = input_details[0]['shape']
                im = opened_image
                image_asarray = cv2.imdecode(im, cv2.IMREAD_COLOR)
                original_image = cv2.cvtColor(image_asarray, cv2.COLOR_BGR2RGB)
                im_rgb = cv2.resize(original_image, (input_shape[1], input_shape[2]))
                image_data = im_rgb / 255.
                images_data = []
                for i in range(1):
                    images_data.append(image_data)
                images_data = np.asarray(images_data).astype(np.float32)
                
                # input_data = np.expand_dims(im_rgb, axis=0)
                # input_data = np.asarray(input_data).astype(np.float32)

                print("############## input_data shape ##############")
                print(images_data.shape)
                print()

                interpreter.set_tensor(input_details[0]['index'], images_data)
                interpreter.invoke()


                pred = [interpreter.get_tensor(output_details[i]['index'])
                        for i in range(len(output_details))]

                boxes, pred_conf = self.filter_boxes(pred[0],
                                                pred[1],
                                                score_threshold=0.25,
                                                input_shape=tf.constant([input_shape[1], input_shape[2]]))

                boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
                    boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
                    scores=tf.reshape(
                        pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
                    max_output_size_per_class=50,
                    max_total_size=50,
                    iou_threshold=IOU,
                    score_threshold=SCORE
                )
                pred_bbox = [boxes.numpy(),
                            scores.numpy(),
                            classes.numpy(),
                            valid_detections.numpy()]

                class_names = self._get_class_names(AI_Model_Path.Get_Labelmap_Path())

                valid_detections = pred_bbox[3][0]
                while valid_detections > 0:
                    bounding_box = pred_bbox[0][0][valid_detections - 1]
                    class_name = pred_bbox[2][0][valid_detections - 1]
                    confidence = pred_bbox[1][0][valid_detections - 1]
                    class_name = class_names[str(class_name)[0:-2]]

                    now = datetime.now()
                    results.append({'class': class_name, 'confidence': confidence.item(), 'box': bounding_box.tolist(), 'timestamp': now.strftime("%d/%m/%Y %H:%M:%S")})
                    valid_detections -= 1

        except Exception as e:
            print ( "detect_object unexpected error %s " % e )
            raise

        # return results_json
        return json.dumps(results)
    
class BatchImageProcessor():
    def __init__(self):
        return

    def process_images(self, mediaStreamMessage, rawBytes, size):
        # Read image raw bytes
        im = Image.frombytes('RGB', size, rawBytes.tobytes())
        draw = ImageDraw.Draw(im)
        imgBuf = io.BytesIO()
        im.save(imgBuf, format='JPEG')
        imgBytes = np.frombuffer(imgBuf.getvalue(), dtype=np.uint8)
        
        logging.info("############## ############## Start Load AI Model ############## ##############")
        logging.info("############## Source image size: " + str(size))
        logging.info("############## tensorflow version is: " + tf.__version__ )

        resp = ProcessImages().detect_object(imgBytes)

        inference = mediaStreamMessage.media_sample.inferences.add()

        if resp == "[]":
            resp = "[{'result': 'no detect MS logo'}]"
            inference.subtype = 'None_MS_Logo_Detected'
            classification = inferencing_pb2.Classification(
                                            tag = inferencing_pb2.Tag(
                                                value = resp
                                                # confidence = 1.0,
                                            )
                                        )
            inference.classification.CopyFrom(classification)
        else:
            inference.subtype = 'MS_Logo_Detected'
            classification = inferencing_pb2.Classification(
                                            tag = inferencing_pb2.Tag(
                                                value = resp
                                                # confidence = 1.0,
                                            )
                                        )
            inference.classification.CopyFrom(classification)
             
        logging.info("############## detect result: " + resp)
        logging.info("############## ############## END ############## ##############")
        return mediaStreamMessage