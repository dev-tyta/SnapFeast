from PIL import Image
import numpy as np
import requests
from io import BytesIO
import torch
from facenet_pytorch import InceptionResnetV1, MTCNN as FacenetMTCNN
from users.models import UserEmbeddings



class FacialProcessing():
    def __init__(self, required_size=(160,160)):
        self.img_size = required_size
        self.mtcnn_detector = FacenetMTCNN(image_size=self.img_size[0], thresholds=[0.6, 0.7, 0.7])
        self.model = InceptionResnetV1(pretrained='vggface2').eval()


    def face_extract(self, image_url):
        response = requests.get(image_url)
        self.img = Image.open(BytesIO(response.content))
        self.img = self.img.convert("RGB")
        
        faces = self.mtcnn_detector(self.img)

        if faces:
            face_array = faces.numpy()

            return face_array
        else:
            return None

    def extract_embeddings(self, face_array):
        if face_array is not None:
            face_tensor = torch.tensor(face_array).unsqueeze(0)  # Add batch dimension
            with torch.no_grad():
                embeddings = self.model(face_tensor).numpy()
            embeddings = np.squeeze(embeddings, axis=0)
            return embeddings
        else: 
            return None
        
    def save_embeddings_to_db(self, user_id, embeddings):
        user_embeddings, created = UserEmbeddings.objects.update_or_create(user_id=user_id,
                                                                        defaults={"embeddings": embeddings.tolist()})

        return created
        

    def process_user_images(self, image_urls, user_id):
        results = []
        for image_url in image_urls:
            try:
                face_array = self.face_extract(image_url)
                if face_array is not None:
                    embeddings = self.extract_embeddings(face_array)
                    if embeddings is not None:
                        created = self.save_embeddings_to_db(user_id, embeddings)
                        if created:
                            results.append({'image': image_url, 'status': 'success', 'message': 'Embeddings saved successfully'})
                        else:
                            results.append({'image': image_url, 'status': 'error', 'message': 'Failed to save embeddings'})
                    else:
                        results.append({'image': image_url, 'status': 'error', 'message': 'Embeddings cannot be extracted'})
                else:
                    results.append({'image': image_url, 'status': 'error', 'message': 'No face detected in the image'})
            except Exception as e:
                results.append({'image': image_url, 'status': 'error', 'message': f'Processing failed: {str(e)}'})

        return results