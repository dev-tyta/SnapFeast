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
        pass  # Initialization not needed for API use

    def extract_embeddings(self, image_path):
        url = "https://testys-faceembeddings.hf.space/extract"
        try:
            with open(image_path, "rb") as image_file:
                files = {"file": image_file}
                response = requests.post(url, files=files)
                response.raise_for_status()
                return response.json()['embeddings']
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def save_embeddings_to_db(self, user_id, embeddings):
        user_embeddings, created = UserEmbeddings.objects.update_or_create(
            user_id=user_id,
            defaults={"embeddings": embeddings}
        )
        cache.delete(f'user_embeddings_{user_id}')
        return created

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


#testing the class
face_processor = FacialProcessing()
print(face_processor.extract_embeddings('../images/rasaq.jpeg'))

