from PIL import Image
import numpy as np
from scipy.spatial.distance import cosine
from mtcnn.mtcnn import MTCNN
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
import matplotlib.pyplot as plt

def face_extract(img_path, required_size=(224,224)):
    pixel = plt.imread(img_path)
    mtcnn_detector = MTCNN()
    faces = mtcnn_detector.detect_faces(pixel)

    face_array
