#

## AI Capabilities

One of the most popular Edge scenarios is the artificial intelligence (AI) on Edge (Image Classification, Object Detection, Body, Face & Gesture Analysis, Image Manipulation, ETC ... ). Azure IoT Edge can certainly support these scenarios, These AI ability can also be improve over the model update, but in some scenarios the Edge device network environment is not good, Especially for some manufacturing equipment such as wind power or oil exploitation which equipment in the desert/sea or  extreme environment.

## TensorFlow model enable on Edge device

1. AI Model File: *.tflite its pre-trained AI model which download from [TensorFlow.org - Download starter model with Metadata](https://www.tensorflow.org/lite/examples/object_detection/overview) and its a generic AI model format that can be used in cross-platform applications such as IOS and Android. And about more information about Metadata and associated fields (eg: labels.txt) see [Read the metadata from models](https://www.tensorflow.org/lite/convert/metadata#read_the_metadata_from_models)
2. Model description： An object detection model is trained to detect the presence and location of multiple classes of objects. For example, a model might be trained with images that contain various pieces of fruit, along with a label that specifies the class of fruit they represent (e.g. an apple, a banana, or a strawberry), and data specifying where each object appears in the image.

    When an image is subsequently provided to the model, it will output a list of the objects it detects, the location of a bounding box that contains each object, and a score that indicates the confidence that detection was correct.
3. In case of if you want to build or customize tuning an AI Model please see [TensorFlow Lite Model Maker](https://www.tensorflow.org/lite/guide/model_maker)
4. More free pre-trained detection models with a variety of latency and precision characteristics can be found in the [Detection Zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf1_detection_zoo.md#mobile-models). Each one of them follows the input and output signatures described in the following sections.

Here I have made an example of Edge Module code for reference how to use Python to call TensorFlow *. Tflite format Model on Edge.

[az-iotedge-ai-model-loader](https://github.com/Nick287/az-iotedge-ai-model-loader/tree/main/AIModelLoader/modules/TensorFlowLoader)

```python

    def detect_object(self, imgBytes):

        results = []
        try:
            model_full_path = AI_Model_Path.Get_Model_Path()
            if(model_full_path == ""):
                logging.info("################ PLEASE SET AI MODEL FIRST")
                logging.info("############## ############## END ############## ##############")
                raise Exception ("PLEASE SET AI MODEL FIRST")
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

                # bytes to numpy.ndarray
                im_arr = np.frombuffer(imgBytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
                img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)

                im_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                im_rgb = cv2.resize(im_rgb, (input_shape[1], input_shape[2]))
                input_data = np.expand_dims(im_rgb, axis=0)
                # input_data = np.asarray(input_data).astype(np.float32)
                print("############## input_data shape ##############")
                print(input_data.shape)
                print()

                interpreter.set_tensor(input_details[0]['index'], input_data)
                interpreter.invoke()
                output_data = interpreter.get_tensor(output_details[0]['index'])
                print("############## output_data shape ##############")
                print(output_data.shape)
                print()
                detection_boxes = interpreter.get_tensor(output_details[0]['index'])
                detection_classes = interpreter.get_tensor(output_details[1]['index'])
                detection_scores = interpreter.get_tensor(output_details[2]['index'])
                num_boxes = interpreter.get_tensor(output_details[3]['index'])

                label_names = [line.rstrip('\n') for line in open(AI_Model_Path.Get_Labelmap_Path())]
                label_names = np.array(label_names)
                new_label_names = list(filter(lambda x : x != '???', label_names))

                for i in range(int(num_boxes[0])):
                    if detection_scores[0, i] > .5:
                        class_id = int(detection_classes[0, i])
                        class_name = new_label_names[class_id]
                        # top,	left,	bottom,	right
                        results_json = "{'Class': '%s','Score': '%s','Location': '%s'}" % (class_name, detection_scores[0, i],detection_boxes[0, i])
                        results.append(results_json)
                        print(results_json)
        except Exception as e:
            print ( "detect_object unexpected error %s " % e )
            raise

        # return results
        return json.dumps(results)
```

## Open Neural Network Exchange (ONNX)

Open Neural Network Exchange (ONNX) is an open standard format for representing machine learning models. ONNX is supported by a community of partners who have implemented it in many frameworks and tools.

1. ONNX supports a variety of tools to Build and deploy models and Frameworks & Converters [Build / Deploy Model](https://onnx.ai/supported-tools.html)
2. You can use ONNX runtime run ONNX Pre-Trained Models [ONNX Model Zoo](https://github.com/onnx/models) for implementation Vision Language Other AI features
3. In this sample i used model of [Object Detection & Image Segmentation - Tiny YOLOv3](https://github.com/onnx/models/tree/master/vision/object_detection_segmentation/tiny-yolov3)

[Edge ONNX loader](https://github.com/Nick287/az-iotedge-ai-model-loader/tree/main/AIModelLoader/modules/ONNXLoader)

```python

    def letterbox_image(self, image, size):
        '''resize image with unchanged aspect ratio using padding'''
        iw, ih = image.size
        w, h = size
        scale = min(w/iw, h/ih)
        nw = int(iw*scale)
        nh = int(ih*scale)

        image = image.resize((nw,nh), Image.BICUBIC)
        new_image = Image.new('RGB', size, (128,128,128))
        new_image.paste(image, ((w-nw)//2, (h-nh)//2))
        return new_image

    def preprocess(self, img):
        model_image_size = (416, 416)
        boxed_image = self.letterbox_image(img, tuple(reversed(model_image_size)))
        image_data = np.array(boxed_image, dtype='float32')
        image_data /= 255.
        image_data = np.transpose(image_data, [2, 0, 1])
        image_data = np.expand_dims(image_data, 0)
        return image_data

    def detect_object(self, imgBytes):
        results = []
        try:
            model_full_path = AI_Model_Path.Get_Model_Path()
            if(model_full_path == ""):
                logging.info("################ PLEASE SET AI MODEL FIRST")
                logging.info("############## ############## END ############## ##############")
                raise Exception ("PLEASE SET AI MODEL FIRST")
            logging.info("############## AI MODEL PATH: " + model_full_path)
            if '.onnx' in model_full_path:

                # input
                image_data = self.preprocess(imgBytes)
                image_size = np.array([imgBytes.size[1], imgBytes.size[0]], dtype=np.float32).reshape(1, 2)

                labels_file = open(AI_Model_Path.Get_Labelmap_Path())
                labels = labels_file.read().split("\n")

                # Loading ONNX model
                print("loading Tiny YOLO...")
                start_time = time.time()
                sess = rt.InferenceSession(model_full_path)
                print("loaded after", time.time() - start_time, "s")

                input_name00 = sess.get_inputs()[0].name
                input_name01 = sess.get_inputs()[1].name
                pred = sess.run(None, {input_name00: image_data,input_name01:image_size})
 
                boxes = pred[0]
                scores = pred[1]
                indices = pred[2]

                results = []
                out_boxes, out_scores, out_classes = [], [], []
                for idx_ in indices[0]:
                    out_classes.append(idx_[1])
                    out_scores.append(scores[tuple(idx_)])
                    idx_1 = (idx_[0], idx_[2])
                    out_boxes.append(boxes[idx_1])
                    results_json = "{'Class': '%s','Score': '%s','Location': '%s'}" % (labels[idx_[1]], scores[tuple(idx_)],boxes[idx_1])
                    results.append(results_json)
                    print(results_json)

        except Exception as e:
            print ( "detect_object unexpected error %s " % e )
            raise

        # return results
        return json.dumps(results)
```

The above is the key code of how to enable the AI function in the Edge client. Of course, in the whole AI solution, we also need to consider much more such how to  update of AI model. Therefore, I have a [complete sample code](https://github.com/Nick287/az-iotedge-ai-model-loader) of using AI model on Edge.

So in this sample, the dynamically loaded AI model base on the features of IoT Edge module Twin, the architecture please refer below and it work steps like this

1. Upload Pre-Trained AI Models to public Blob storage (Or any other Web service, just for the Edge Module can access this resource and download to edge device later)
2. The IoT Hub will sync device module twins automatically with AI Models information, the sync will be done even if IoT Edge offline for some time.
3. The Loader Module monitors the updates of module twins via SDK. Through this way, it can get the ML model SAS token, and then download the AI model.
4. The Loader Module saves the AI model in the shared local storage of the IoT Edge Module. The local storage needs to be configured in the IoT Edge deployment JSON file.
5. The Loader Module load the AI model from the local storage by TensorFlow/ONNX SDK.
6. The Loader Module starts a Web API that receives the binary photo via post request and returns results in json file

In case for update AI model we can upload new AI model to blob storage and sync device module twins again instead of update whole IoT Edge module image, so this is the AI model incremental updates.

![image](/img/edgeai.png)
