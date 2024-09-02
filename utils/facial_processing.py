import numpy as np
import os
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
import logging
from PIL import Image

logger = logging.getLogger(__name__)

class FacialProcessing:
    def __init__(self):
        os.environ['TORCH_HOME'] = '/tmp/.cache/torch'
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.mtcnn = MTCNN(keep_all=True, device=self.device)
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)

    def extract_embeddings_vgg(self, image_path):
        try:
            img = self.preprocess_image(image_path)
            if img is None:
                return None
                
            # Detect faces
            boxes, _ = self.mtcnn.detect(img)
            
            if boxes is None or len(boxes) == 0:
                logger.warning(f"No face detected in image: {image_path}")
                return None
            
            if len(boxes) > 1:
                logger.warning(f"Multiple faces detected in image: {image_path}")
                return None
            
            # Get the largest face
            largest_box = boxes[0]
            face = self.mtcnn(img, return_prob=False)
            
            if face is None:
                logger.warning(f"Failed to align face in image: {image_path}")
                return None
            
            # Extract embeddings
            with torch.no_grad():
                embeddings = self.resnet(face).cpu().numpy().flatten()
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"An error occurred while extracting embeddings: {e}")
            return None

    def preprocess_image(self, image_path):
        try:
            img = Image.open(image_path)
            img = img.convert('RGB')
            return img
        except Exception as e:
            logger.error(f"Error opening image: {e}")
            return None