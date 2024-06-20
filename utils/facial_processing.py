from PIL import Image
import numpy as np
import os 
import json
from mtcnn.mtcnn import MTCNN
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
from PIL import Image



class FacialProcessing():
    def __init__(self, required_size=(224,224)):
        self.img_size = required_size
        self.mtcnn_detector = MTCNN()
        self.model = VGGFace(model="resnet50", include_top=False,
                             pooling="avg")


    def face_extract(self, image_path):
        self.img = Image.open(self.image_path)
        self.img = self.img.convert("RGB")
        pixel = (self.img)
        
        faces = self.mtcnn_detector.detect_faces(pixel)

        if faces:
            num_face = len(faces)

            print(f"Found {num_face} face(s) in the image")

            x1, y1, width, height = faces[0]["box"]
            x2, y2 = x1+width, y1+height
            face = pixel[y1:y2, x1:x2]
            image = Image.fromarray(face)
            image = image.resize(self.img_size)
            face_array = np.asarray(image)

            return face_array
        else:
            return None

    def extract_embeddings(self, face_array):
        if face_array is not None:
            face = face_array.astype("float32")
            face = np.expand_dims(face, axis=0)
            face = preprocess_input(face, version=2)
            embeddings = self.model.predict(face)
            embeddings = np.squeeze(embeddings, axis=0)

            return embeddings
        
        else: 
            return None
        
    def process_user_images(self, file_directory):
        embeddings_dict = {}
        
        for filename in os.listdir(file_directory):
            path = os.path.join(file_directory, filename)
            face = self.face_extract(path)
            if face is not None:
                extracted_embedding = self.extract_embeddings(face)
                embeddings_dict[filename] = extracted_embedding.tolist()
            else:
                return None
            
        for filename, embedding in embeddings_dict.items():
             