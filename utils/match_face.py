from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from django.core.cache import cache
from users.models import UserEmbeddings
from utils.facial_processing import FacialProcessing

class FaceMatch:
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.face_processor = FacialProcessing()  # This now gets the singleton instance

    def load_embeddings_from_db(self):
        embeddings_dict = cache.get('all_user_embeddings')
        if embeddings_dict is None:
            user_embeddings = UserEmbeddings.objects.all()
            embeddings_dict = {ue.user.id: np.array(ue.embeddings) for ue in user_embeddings}
            cache.set('all_user_embeddings', embeddings_dict, timeout=3600)  # Cache for 1 hour
        return embeddings_dict

    def match_faces(self, saved_embeddings, threshold=0.6):
        max_similarity = 0
        identity = None

        for user_id, stored_embeddings in saved_embeddings.items():
            similarity = cosine_similarity(self.embeddings.reshape(1, -1), stored_embeddings.reshape(1, -1))[0][0]
            if similarity > max_similarity:
                max_similarity = similarity
                identity = user_id

        return identity, max_similarity if max_similarity > threshold else (None, 0)

    def new_face_matching(self):
        embeddings_dict = self.load_embeddings_from_db()
        if not embeddings_dict:
            return {'status': 'Error', 'message': 'No embeddings available'}

        identity, similarity = self.match_faces(embeddings_dict)
        if identity:
            return {
                'status': 'Success',
                'message': 'Match Found',
                'user_id': identity,
                'similarity': similarity
            }
        return {
            'status': 'Error',
            'message': 'No matching face found'
        }
    