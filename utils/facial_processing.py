from PIL import Image
import numpy as np
import requests
from io import BytesIO
from mtcnn.mtcnn import MTCNN
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
from ..src.users.models import UserEmbeddings



class FacialProcessing():
    def __init__(self, required_size=(224,224)):
        self.img_size = required_size
        self.mtcnn_detector = MTCNN()
        self.model = VGGFace(model="resnet50", include_top=False,
                             pooling="avg")


    def face_extract(self, image_url):
        response = requests.get(image_url)
        self.img = Image.open(BytesIO(response.content))
        self.img = self.img.convert("RGB")
        pixel = np.asarray(self.img)
        
        faces = self.mtcnn_detector.detect_faces(pixel)

        if faces:
            num_face = len(faces)

            print(f"Found {num_face} face(s) in the image")

            x1, y1, width, height = faces[0]["box"]
            x2, y2 = x1+width, y1+height
            face = pixel[y1:y2, x1:x2]
            image = Image.fromarray(face)
            image = image.resize(self.img_size)
            face_array = np.asarray(image)

            return face_array
        else:
            return None

    def extract_embeddings(self, face_array):
        if face_array is not None:
            face = face_array.astype("float32")
            face = np.expand_dims(face, axis=0)
            face = preprocess_input(face, version=2)
            embeddings = self.model.predict(face)
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