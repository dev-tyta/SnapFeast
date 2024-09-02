from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from django.core.cache import cache
from users.models import UserEmbeddings
from .facial_processing import FacialProcessing

class FaceMatch:
    def __init__(self, image_file):
        self.image_file = image_file
        self.face = FacialProcessing()
        self.threshold = getattr(settings, 'FACE_RECOGNITION_THRESHOLD', 0.6)
        self.max_matches = 1
        self.embedding_shape = None

    def load_embeddings_from_db(self):
        embeddings_dict = cache.get('all_user_embeddings')
        if embeddings_dict is None:
            user_embeddings = UserEmbeddings.objects.all()
            embeddings_dict = {ue.user.id: np.array(ue.embeddings) for ue in user_embeddings}
            cache.set('all_user_embeddings', embeddings_dict, timeout=3600)  # Cache for 1 hour
        return embeddings_dict

    def validate_embedding(self, embedding):
        """
        Validates the shape of the embedding.
        """
        if self.embedding_shape is None:
            logger.warning("No reference embedding shape available")
            return False
        if np.array(embedding).shape != self.embedding_shape:
            logger.warning(f"Invalid embedding shape. Expected {self.embedding_shape}, got {np.array(embedding).shape}")
            return False
        return True


    def match_faces(self, new_embeddings, saved_embeddings):
        """
        Matches the new face embeddings with saved embeddings.
        """
        if not self.validate_embedding(new_embeddings):
            return None, 0

        new_embeddings = np.array(new_embeddings)
        similarities = []

        for user_id, stored_embeddings in saved_embeddings.items():
            similarity = cosine_similarity(new_embeddings.reshape(1, -1), stored_embeddings.reshape(1, -1))[0][0]
            similarities.append((user_id, similarity))

        # Sort similarities in descending order
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Check if the top match exceeds the threshold and if there's a significant gap to the second-best match
        if similarities and similarities[0][1] > self.threshold:
            if len(similarities) == 1 or similarities[0][1] - similarities[1][1] > 0.1:
                return similarities[0]

        return None, 0


    def new_face_matching(self):
        embeddings_dict = self.load_embeddings_from_db()
        if not embeddings_dict:
            return {'status': 'Error', 'message': 'No valid embeddings available in the database'}

        if not self.validate_embedding(new_embeddings):
            return {'status': 'Error', 'message': 'Invalid embedding shape'}

        new_embeddings = self.face.extract_embeddings_vgg(self.image_file)
        if not new_embeddings:
            return {'status': 'Error', 'message': 'Failed to extract embeddings from the image'}
        
        new_embeddings = np.array(new_embeddings)

        identity, similarity = self.match_faces(new_embeddings, embeddings_dict)
        if identity:
            return {
                'status': 'Success',
                'message': 'Match Found',
                'user_id': identity,
                'similarity': float(similarity)  # Convert numpy float to Python float
            }
        return {
            'status': 'Error',
            'message': 'No matching face found or multiple potential matches detected'
        }