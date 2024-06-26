import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .facial_processing import FacialProcessing
from ..users.models import UserEmbeddings



class FaceMatch:
    def __init__(self, image_file):
        self.image_file = image_file
        self.face = FacialProcessing() 


    def load_embeddings_from_db(self):
        try:
            user_embeddings = UserEmbeddings.objects.all()
            embeddings_dict = {ue.user.id: np.array(ue.embeddings) for ue in user_embeddings}
            return embeddings_dict
        except UserEmbeddings.DoesNotExist:
            return None


    def match_faces(self, new_embeddings, saved_embeddings):
        max_similarity = 0
        identity = None

        for user_id, stored_embeddings in saved_embeddings.items():
            similarity = cosine_similarity(new_embeddings.reshape(1, -1), stored_embeddings.reshape(1,-1))[0][0]
            if similarity > max_similarity:
                max_similarity = similarity
                identity = user_id
        
        return identity, max_similarity

    def new_face_matching(self):
        new_face = self.face.face_extract(self.image_file)
        if new_face is not None:
            new_embeddings = self.face.extract_embeddings(new_face)
            embeddings_dic = self.load_embeddings_from_db()

            if embeddings_dic:
                identity, similarity = self.match_faces(new_embeddings, embeddings_dic)
                if identity:
                    return {'status': 'Success', 'message':'Match Found', 'user_id':identity, 'similarity':similarity}
                else:
                        return {'status': 'error', 'message': 'No matching face found'}
            else:
                return {'status': 'error', 'message': 'No embeddings available'}
        else:
            return {'status': 'error', 'message': 'No face detected in the image'}
