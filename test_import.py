import sys
print("Python version:", sys.version)

# Try importing in different ways
try:
    import face_recognition_models
    print("✅ face_recognition_models imported")
    print("Location:", face_recognition_models.__path__)
except Exception as e:
    print("❌ face_recognition_models error:", e)

try:
    import face_recognition
    print("✅ face_recognition imported")
    print("Location:", face_recognition.__file__)
except Exception as e:
    print("❌ face_recognition error:", e)

try:
    import cv2
    print("✅ cv2 imported")
except Exception as e:
    print("❌ cv2 error:", e)