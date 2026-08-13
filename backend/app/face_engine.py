import numpy as np
from insightface.app import FaceAnalysis

_face_app = None


def get_face_app():
    '''Lazily load only the detection + recognition models (not landmarks/genderage) to keep memory usage low.'''
    global _face_app
    if _face_app is None:
        _face_app = FaceAnalysis(name='buffalo_l', allowed_modules=['detection', 'recognition'])
        _face_app.prepare(ctx_id=-1, det_size=(640, 640))
    return _face_app


def detect_and_embed(image_bgr: np.ndarray):
    '''
    Runs RetinaFace detection + ArcFace embedding on an image.
    Returns a list of dicts, one per detected face:
        {'bbox': [x1, y1, x2, y2], 'det_score': float, 'embedding': np.ndarray(512,)}
    '''
    app = get_face_app()
    faces = app.get(image_bgr)

    results = []
    for face in faces:
        results.append({
            'bbox': face.bbox.tolist(),
            'det_score': float(face.det_score),
            'embedding': face.normed_embedding,
        })
    return results
