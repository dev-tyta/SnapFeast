from django.http import JSONResponse
from django.contrib.auth import login
from ...utils.match_face import FaceMatch

match_face = FaceMatch()

def facial_login(request):
    if request.method == "POST" and request.FILES["face_image"]:
        face_image = request.FILES["face_image"]
        user = match_face.new_face_matching(face_image)
        if user is not None:
            login(request, user)
            return JSONResponse({'status':'success', 'message':'Logged in Successfully'})
        else:
            return JSONResponse({'status':'failed', 'message':'Facial Recognition failed, No User Recognized'})
        
    else:
        return JSONResponse({'status':'error', 'message':'Invalid Request'})
