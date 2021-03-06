import os

import cv2
cv2.setNumThreads(0)
cv2.ocl.setUseOpenCL(False)
import numpy as np

from .eval import Evaluator


class FullImageEvaluator(Evaluator):
    def __init__(self, *args, **kwargs):
        if 'step_callback' in kwargs:
            self.step_callback = kwargs['step_callback']
            del kwargs['step_callback']
        else:
            self.step_callback = None
        super().__init__(*args, **kwargs)

    def process_batch(self, predicted, model, data, prefix=""):
        names = data['image_name']
        for i in range(len(names)):
            self.on_image_constructed(names[i], predicted[i,...], prefix)

    def save(self, name, prediction, prefix=""):
        if self.test:
            input_path = os.path.join(self.config.dataset_path, self.ds.fn_mapping['images'](name))
        else:
            input_path = os.path.join(self.config.dataset_path, 'images_all', name)
        input_image = cv2.imread(input_path, 0)
        rows, cols = input_image.shape[:2]
        prediction = prediction[0:rows, 0:cols,...]
        if prediction.shape[2] < 3:
            zeros = np.zeros((rows, cols), dtype=np.float32)
            prediction = np.dstack((prediction[...,0], prediction[...,1], zeros))
        else:
            prediction = cv2.cvtColor(prediction, cv2.COLOR_RGB2BGR)
        if self.test:
            name = os.path.split(name)[-1]
        
        save_path = os.path.join(self.config.dataset_path, self.ds.fn_mapping['masks'](name)) # os.path.join(self.save_dir + prefix, self.ds.fn_mapping['masks'](name))

        print('saving to ',  save_path)
        folder, _ = os.path.split(save_path)
        if not os.path.exists(folder):
            os.makedirs(folder)

        img = (prediction * [255,255,0]).astype(np.uint8)
        img = cv2.resize(img, (cols, rows))
        cv2.imwrite(save_path, img)

        self.step_callback({'output_path': save_path, 'input_path': input_path, 'name': name})
