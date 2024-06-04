import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np



class FaceMatch:
    def __init__(self, image_path, embeddings_json):
        self.image_path = image_path
        self.max_similarity = 0
        self.identity = None
        self.json_file = embeddings_json 


    def load_embeddings(self, embeddings_file):
        with open(embeddings_file, "r") as file:
            embeddings_dict = json.load(file)

        for key in embeddings_dict:
            embeddings_dict[key] = np.asarray(embeddings_dict[key])

        return embeddings_dict


    def match_faces(self, new_embeddings, saved_embeddings):
            for filename, stored_embeddings in saved_embeddings.items():
                similarity = cosine_similarity(new_embeddings.reshape(1, -1), stored_embeddings.reshape(1,-1))
                if similarity > self.max_similarity:
                    self.max_similarity = similarity
                    self.identity = filename
            
            return self.identity, self.max_similarity

    def new_face_matching(self):
        embeddings = self.load_embeddings()