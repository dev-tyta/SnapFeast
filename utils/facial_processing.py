from PIL import Image
import numpy as np
from scipy.spatial.distance import cosine
from mtcnn.mtcnn import MTCNN
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
import matplotlib.pyplot as plt


class FacialProcessing():
    def __init__(self, img_path, required_size=(224,224)):
        self.face_array = []
        self.image_path = img_path
        self.img_size = required_size


    def face_extract(self):
        pixel = plt.imread(self.image_path)
        mtcnn_detector = MTCNN()
        faces = mtcnn_detector.detect_faces(pixel)

        for i in range(len(faces)):
            x1, y1, width, height = faces[i]["box"]
            x2, y2 = x1+width, y1+height
            face = pixel[y1:y2, x1:x2]
            image = Image.fromarray(face)
            image = image.resize(self.img_size)
            self.face_array.append(np.asarray(image))

        return self.face_array


    def extract_embeddings(self):
        pass