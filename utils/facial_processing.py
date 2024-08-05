import os
import numpy as np
import face_recognition
from PIL import Image
from users.models import UserEmbeddings
from django.core.cache import cache
import gc

class FacialProcessing:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FacialProcessing, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        pass  # No need to initialize models as face_recognition doesn't require it

    def face_extract(self, image):
        img = face_recognition.load_image_file(image)
        face_locations = face_recognition.face_locations(img)
        if face_locations:
            return face_locations
        return None

    def extract_embeddings(self, image, face_location):
        img = face_recognition.load_image_file(image)
        face_encoding = face_recognition.face_encodings(img, [face_location])[0]
        return face_encoding

    def save_embeddings_to_db(self, user_id, embeddings):
        user_embeddings, created = UserEmbeddings.objects.update_or_create(
            user_id=user_id,
            defaults={"embeddings": embeddings.tolist()}
        )
        if created or not created:
            cache.delete(f'user_embeddings_{user_id}')
        return created

    def process_user_images(self, images, user_id):
        results = []
        for image in images:
            try:
                face_locations = self.face_extract(image)
                if face_locations:
                    # We'll use the first detected face
                    face_location = face_locations[0]
                    embeddings = self.extract_embeddings(image, face_location)
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
                            'message': 'Embeddings cannot be extracted'
                        })
                else:
                    results.append({
                        'image': image,
                        'status': 'error',
                        'message': 'No face detected in the image'
                    })
            except Exception as e:
                results.append({
                    'image': image,
                    'status': 'error',
                    'message': f'Processing failed: {str(e)}'
                })
            finally:
                # Explicitly invoke garbage collection to free up memory
                gc.collect()
        return results