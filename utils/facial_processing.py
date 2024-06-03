from PIL import Image
import numpy as np
from scipy.spatial.distance import cosine
from mtcnn.mtcnn import MTCNN
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
import matplotlib.pyplot as plt
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity


class FacialProcessing():
    def __init__(self, img_path, required_size=(224,224)):
        self.face_array = None
        self.image_path = img_path
        self.img_size = required_size
        self.model = VGGFace(model="resnet50", include_top=False,
                             pooling="avg")


    def face_extract(self):
        self.img = Image.open(self.image_path)
        self.img = self.img.convert("RGB")
        pixel = (self.img)
        
        mtcnn_detector = MTCNN()
        faces = mtcnn_detector.detect_faces(pixel)

        if faces:
            num_face = len(faces)

            print(f"Found {num_face} face(s) in the image")

            x1, y1, width, height = faces[0]["box"]
            x2, y2 = x1+width, y1+height
            face = pixel[y1:y2, x1:x2]
            image = Image.fromarray(face)
            image = image.resize(self.img_size)
            self.face_array = np.asarray(image)

            return self.face_array

        else:
            return None

    def extract_embeddings(self):
        if self.face_array is not None:
            face = self.face_array.astype("float32")
            face = np.expand_dims(face, axis=0)
            face = preprocess_input(face, version=2)
            embeddings = self.model.predict(face)
            embeddings = np.squeeze(embeddings, axis=0)

            return embeddings
        
        else: 
            return None
        
    def match_faces(self, new_embeddings, saved_embeddings):
        max_similarity = 0
        for filename, stored_embeddings in saved_embeddings.items():
            similarity = cosine_similarity(new_embeddings.reshape()