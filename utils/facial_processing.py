import os
import numpy as np
import torch
from PIL import Image
from facenet_pytorch import InceptionResnetV1, MTCNN
from users.models import UserEmbeddings
from django.core.cache import cache
import gc

class FacialProcessing:
    _model = None  # Class variable to store the model

    def __init__(self, required_size=(160, 160)):
        self.img_size = required_size
        self.mtcnn_detector = MTCNN(image_size=self.img_size[0], thresholds=[0.6, 0.7, 0.7])
        if FacialProcessing._model is None:
            FacialProcessing._model = InceptionResnetV1(pretrained='vggface2').eval()

    def face_extract(self, image):
        img = Image.open(image).convert("RGB")
        faces = self.mtcnn_detector(img)
        return faces.numpy() if faces is not None else None

    def extract_embeddings(self, face_array):
        if face_array is not None:
            face_tensor = torch.tensor(face_array).unsqueeze(0)
            with torch.no_grad():
                embeddings = FacialProcessing._model(face_tensor).numpy()
            return np.squeeze(embeddings, axis=0)
        return None

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
                face_array = self.face_extract(image)
                if face_array is not None:
                    embeddings = self.extract_embeddings(face_array)
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
