import cv2
import numpy as np
import tensorflow as tf
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

class EmotionRecognitionSystem:
    """
    Emotion recognition system implemented using OpenCV and TensorFlow
    Capable of recognizing children's facial expressions and adjusting interaction strategies based on emotions
    """
    
    def __init__(self, model_path="models/emotion_model.h5"):
        """Initialize emotion recognition system"""
        self.model_path = model_path
        self.model = None
        self.emotion_categories = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
        
        try:
            self.face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self._load_model()
        except Exception as e:
            print(f"Failed to initialize emotion recognition system: {str(e)}")
    
    def _load_model(self):
        """Load pre-trained emotion recognition model"""
        try:
            # If model file exists, load the model
            import os
            if os.path.exists(self.model_path):
                self.model = tf.keras.models.load_model(self.model_path)
                print("Emotion recognition model loaded successfully")
            else:
                print(f"Emotion recognition model file does not exist: {self.model_path}")
                self._create_simple_model()  # Create a simple model as a substitute
        except Exception as e:
            print(f"Failed to load emotion recognition model: {str(e)}")
            self._create_simple_model()  # Create a simple model as a substitute
    
    def _create_simple_model(self):
        """Create a simple emotion recognition model as a substitute"""
        try:
            # Create a simple CNN model
            model = tf.keras.Sequential([
                tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(48, 48, 1)),
                tf.keras.layers.MaxPooling2D((2, 2)),
                tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                tf.keras.layers.MaxPooling2D((2, 2)),
                tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dense(7, activation='softmax')
            ])
            
            model.compile(optimizer='adam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
            
            self.model = model
            print("Simple emotion recognition model created successfully")
        except Exception as e:
            print(f"Failed to create simple emotion recognition model: {str(e)}")
            self.model = None
    
    def detect_emotion(self, image):
        """
        Detect emotions in faces within the image
        
        Args:
            image: Image in OpenCV format
            
        Returns:
            List of emotion dictionaries, each containing emotion category, confidence, and face position
        """
        if self.model is None:
            return []
        
        try:
            # Convert to grayscale
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_detector.detectMultiScale(
                gray_image,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            emotion_results = []
            
            # Perform emotion recognition for each detected face
            for (x, y, w, h) in faces:
                # Extract face region
                face_region = gray_image[y:y+h, x:x+w]
                
                # Resize to model input size
                resized_face = cv2.resize(face_region, (48, 48))
                
                # Normalize
                normalized_face = resized_face / 255.0
                
                # Prepare model input
                model_input = normalized_face.reshape(1, 48, 48, 1)
                
                # Predict emotion
                prediction = self.model.predict(model_input)
                emotion_index = np.argmax(prediction[0])
                emotion_category = self.emotion_categories[emotion_index]
                confidence = float(prediction[0][emotion_index])
                
                emotion_results.append({
                    "emotion": emotion_category,
                    "confidence": confidence,
                    "position": (x, y, w, h)
                })
            
            return emotion_results
        
        except Exception as e:
            print(f"Emotion detection failed: {str(e)}")
            return []
    
    def draw_emotion_results(self, image, emotion_results):
        """
        Draw emotion recognition results on the image
        
        Args:
            image: Image in OpenCV format
            emotion_results: Results returned by detect_emotion method
            
        Returns:
            Annotated image
        """
        result_image = image.copy()
        
        for result in emotion_results:
            x, y, w, h = result["position"]
            emotion = result["emotion"]
            confidence = result["confidence"]
            
            # Draw rectangle
            cv2.rectangle(result_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Draw emotion label
            label = f"{emotion}: {confidence:.2f}"
            cv2.putText(result_image, label, (x, y-10),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        return result_image


class EmotionRecognitionThread(QThread):
    """Emotion recognition background processing thread"""
    
    # Custom signals
    emotion_recognition_result_signal = pyqtSignal(list)
    processed_image_signal = pyqtSignal(QImage)
    
    def __init__(self, camera_index=0):
        """Initialize emotion recognition thread"""
        super().__init__()
        
        self.camera_index = camera_index
        self.running_flag = False
        
        # Initialize emotion recognition system
        self.recognition_system = EmotionRecognitionSystem()
        
        # Initialize camera
        self.camera = None
    
    def run(self):
        """Run emotion recognition thread"""
        self.running_flag = True
        
        # Open camera
        self.camera = cv2.VideoCapture(self.camera_index)
        
        # Set camera resolution
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        while self.running_flag and self.camera.isOpened():
            try:
                # Read a frame
                success, frame = self.camera.read()
                
                if not success:
                    print("Unable to read image from camera")
                    break
                
                # Detect emotions
                emotion_results = self.recognition_system.detect_emotion(frame)
                
                # Emit emotion recognition result signal
                if emotion_results:
                    self.emotion_recognition_result_signal.emit(emotion_results)
                
                # Draw emotion results
                result_image = self.recognition_system.draw_emotion_results(frame, emotion_results)
                
                # Convert OpenCV image to Qt image
                height, width, channels = result_image.shape
                bytes_per_line = channels * width
                qt_image = QImage(result_image.data, width, height, bytes_per_line, QImage.Format_BGR888)
                
                # Emit processed image signal
                self.processed_image_signal.emit(qt_image)
                
                # Control processing frequency
                self.msleep(30)  # About 30 frames/second
            
            except Exception as e:
                print(f"Emotion recognition processing exception: {str(e)}")
                self.msleep(100)  # Pause for a while when exception occurs
        
        # Release camera
        if self.camera:
            self.camera.release()
    
    def stop(self):
        """Stop emotion recognition thread"""
        self.running_flag = False
        self.wait()


class EmotionDisplayWindow(QWidget):
    """Emotion recognition result display window"""
    
    def __init__(self, parent=None):
        """Initialize emotion display window"""
        super().__init__(parent)
        
        # Set window title and size
        self.setWindowTitle("Children Emotion Recognition")
        self.resize(800, 600)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create image display label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setStyleSheet("border: 2px solid #E0E0E0; background-color: black;")
        
        # Create emotion information label
        self.emotion_info_label = QLabel("Waiting for emotion recognition...")
        self.emotion_info_label.setAlignment(Qt.AlignCenter)
        self.emotion_info_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4A148C; margin: 10px;")
        
        # Add components to layout
        layout.addWidget(self.image_label)
        layout.addWidget(self.emotion_info_label)
        
        # Create and start emotion recognition thread
        self.recognition_thread = EmotionRecognitionThread()
        self.recognition_thread.emotion_recognition_result_signal.connect(self.update_emotion_info)
        self.recognition_thread.processed_image_signal.connect(self.update_image)
        
        # Don't start thread immediately, wait until window is shown
    
    def showEvent(self, event):
        """Window show event"""
        super().showEvent(event)
        # Start recognition thread after window is shown
        self.recognition_thread.start()
    
    def closeEvent(self, event):
        """Window close event"""
        # Stop recognition thread
        self.recognition_thread.stop()
        super().closeEvent(event)
    
    def update_image(self, image):
        """Update image display"""
        pixmap = QPixmap.fromImage(image)
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
    def update_emotion_info(self, emotion_results):
        """Update emotion information display"""
        if not emotion_results:
            self.emotion_info_label.setText("No emotion detected")
            return
        
        # Select the emotion result with highest confidence
        best_result = max(emotion_results, key=lambda x: x["confidence"])
        
        emotion = best_result["emotion"]
        confidence = best_result["confidence"]
        
        # Update emotion information label
        self.emotion_info_label.setText(f"Detected emotion: {emotion} (confidence: {confidence:.2f})")
        
        # Set different colors for different emotions
        if emotion == "Happy":
            self.emotion_info_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; margin: 10px;")
        elif emotion == "Sad":
            self.emotion_info_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3; margin: 10px;")
        elif emotion == "Angry":
            self.emotion_info_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #F44336; margin: 10px;")
        elif emotion == "Surprise":
            self.emotion_info_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FF9800; margin: 10px;")
        else:
            self.emotion_info_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4A148C; margin: 10px;")
        
        # Send emotion result to main system for corresponding processing
        if hasattr(self.parent(), "process_emotion_result"):
            self.parent().process_emotion_result(emotion, confidence)
