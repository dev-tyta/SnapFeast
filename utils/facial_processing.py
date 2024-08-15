import os
import requests
from django.core.cache import cache
from users.models import UserEmbeddings

class FacialProcessing:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FacialProcessing, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.api_url = os.getenv("FACE_RECOGNITION_API_URL")
    def extract_embeddings(self, image_path):
    
        try:
            with open(image_path, "rb") as image_file:
                files = {"file": image_file}
                response = requests.posts(self.api_url, files=files)
                response.raise_for_status()
                return response.json()['embeddings']
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def save_embeddings_to_db(self, user_id, embeddings):
        try:
            user_embeddings, created = UserEmbeddings.objects.update_or_create(
                user_id=user_id,
                defaults={"embeddings": embeddings}
            )
            cache.delete(f'user_embeddings_{user_id}')
            return created
        except Exception as e:
            print(f"Error saving embeddings: {e}")
            return False
        
    def process_user_images(self, images, user_id):
        results = []
        for image in images:
            embeddings = self.extract_embeddings(image)
            if embeddings is not None:
                created = self.save_embeddings_to_db(user_id, embeddings)
                results.append({
                    'image': image,
                    'status': 'success',
                    'message': 'Embeddings saved successfully'
                })
            else:
                results.append({
                    'image': image,
                    'status': 'error',
                    'message': 'Failed to extract embeddings'
                })
        return results
