import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from facial_processing import FacialProcessing



class FaceMatch:
    def __init__(self, image_path, embeddings_json):
        self.image_path = image_path
        self.face = FacialProcessing()
        self.json_file = embeddings_json 


    def load_embeddings(self, embeddings_file):
        with open(embeddings_file, "r") as file:
            embeddings_dict = json.load(file)

        for key in embeddings_dict:
            embeddings_dict[key] = np.asarray(embeddings_dict[key])

        return embeddings_dict


    def match_faces(self, new_embeddings, saved_embeddings):
        max_similarity = 0
        identity = None

        for filename, stored_embeddings in saved_embeddings.items():
            similarity = cosine_similarity(new_embeddings.reshape(1, -1), stored_embeddings.reshape(1,-1))
            if similarity > max_similarity:
                max_similarity = similarity
                identity = filename
        
        return identity, max_similarity

    def new_face_matching(self, image_path, ):
        embeddings = self.load_embeddings()
        new_face = self.face.face_extract(image_path)
        if new_face is not None:
            new_embeddings = self.face.extract_embeddings(new_face)
            embeddings_dic = self.load_embeddings(self.json_file)

            identity, similarity = self.match_faces(new_embeddings, embeddings_dic)
            if identity:
                return identity, similarity
            else:
                return None, 0.0
        else:
            return None, 0.0
        