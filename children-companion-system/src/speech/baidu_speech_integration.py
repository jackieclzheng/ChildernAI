import os
import json
import base64
import time
import wave
import pyaudio
import requests
import numpy as np
from threading import Thread
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer

class BaiduSpeechService:
    """Baidu speech recognition and synthesis API wrapper"""
    
    def __init__(self, app_id, api_key, secret_key):
        """Initialize Baidu speech API"""

        # self.APP_ID = app_id
        self.APP_ID = "6632791"
        # self.API_KEY = api_key
        self.API_KEY = "u3Rn2MPnawYg6y1GvxDtuAPk"
        # self.SECRET_KEY = secret_key
        self.SECRET_KEY = "v3bvbSHK3hLmsKnoMkPTk8ApqlPBvPtB"
        self.access_token = None
        self.token_expiry = None
        self.get_access_token()
        print(f"baidu init{self.APP_ID }")
        print(f"baidu init{self.API_KEY}")
        print(f"baidu init{self.SECRET_KEY}")

        # "app_id": "6632791",
        # "api_key": "u3Rn2MPnawYg6y1GvxDtuAPk",
        # "secret_key": "v3bvbSHK3hLmsKnoMkPTk8ApqlPBvPtB"
    
    def get_access_token(self):
        """Get Baidu API access token"""
        # If already have valid token, return directly
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token
        
        # Get new token
        token_url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.API_KEY,
            "client_secret": self.SECRET_KEY
        }
        
        try:
            response = requests.post(token_url, params=params)
            response.raise_for_status()  # Check if request was successful
            result = response.json()
            
            self.access_token = result["access_token"]
            # Set token expiry time, expire 1 hour earlier than actual to ensure safety
            expires_in_seconds = result["expires_in"] - 3600  
            self.token_expiry = datetime.now().fromtimestamp(time.time() + expires_in_seconds)
            
            return self.access_token
        except Exception as e:
            print(f"Failed to1 get access token: {str(e)}")
            return None
    
    def recognize_speech(self, audio_data, format="pcm", sample_rate=16000):
        """Use Baidu API for speech recognition"""
        # Ensure valid token
        access_token = self.get_access_token()
        if not access_token:
            return {"error": "Unable to get access token"}
        
        # Prepare request
        url = f"https://vop.baidu.com/server_api?dev_pid=1537&cuid=children_companion_system"
        headers = {
            "Content-Type": "application/json"
        }
        
        # Encode audio data
        speech_data = base64.b64encode(audio_data).decode('utf-8')
        
        data = {
            "format": format,
            "rate": sample_rate,
            "channel": 1,
            "token": access_token,
            "speech": speech_data,
            "len": len(audio_data)
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()
            
            if result["err_no"] == 0:
                # Recognition successful
                return {
                    "success": True,
                    "result": result["result"][0],
                    "raw_result": result
                }
            else:
                # Recognition failed
                return {
                    "success": False,
                    "error_code": result["err_no"],
                    "error_msg": result["err_msg"]
                }
                
        except Exception as e:
            print(f"Speech recognition request failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def synthesize_speech(self, text, volume=5, speed=5, pitch=5, voice=0):
        """Use Baidu API for speech synthesis"""
        # Ensure valid token
        access_token = self.get_access_token()
        if not access_token:
            return {"error": "Unable to get access token"}
        
        # Prepare request
        url = f"https://tsn.baidu.com/text2audio"
        params = {
            "tex": text,
            "tok": access_token,
            "cuid": "children_companion_system",
            "ctp": 1,
            "lan": "zh",
            "spd": speed,
            "pit": pitch,
            "vol": volume,
            "per": voice,  # Voice selection: 0-female, 1-male, 3-emotional synthesis-Xiao Yao, 4-emotional synthesis-Ya Ya
            "aue": 3        # Audio format: 3-mp3, 4-pcm-16k, 5-pcm-8k, 6-wav
        }
        
        try:
            response = requests.get(url, params=params)
            
            # Check if audio data is returned
            if response.headers["Content-Type"] == "audio/mp3":
                # Return success with audio data
                return {
                    "success": True, 
                    "audio_data": response.content
                }
            else:
                # Return error information
                result = response.json()
                return {
                    "success": False,
                    "error_code": result.get("err_no"),
                    "error_msg": result.get("err_msg")
                }
                
        except Exception as e:
            print(f"Speech synthesis request failed: {str(e)}")
            return {"success": False, "error": str(e)}


class RecordingThread(QThread):
    """Background recording thread"""
    
    # Custom signals
    recording_completed_signal = pyqtSignal(bytes)
    volume_change_signal = pyqtSignal(float)
    
    def __init__(self, chunk_size=1024, format=pyaudio.paInt16, channels=1, sample_rate=16000, threshold=500, min_recording_duration=1):
        super().__init__()
        
        self.chunk_size = chunk_size
        self.format = format
        self.channels = channels
        self.sample_rate = sample_rate
        self.threshold = threshold          # Volume threshold for detecting speech start and end
        self.min_recording_duration = min_recording_duration  # Minimum recording time in seconds
        
        self.is_recording = False
        self.pause_recording = False
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
    
    def run(self):
        """Run recording thread"""
        self.is_recording = True
        
        # Create audio stream
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        self.frames = []
        
        # Variables for silence detection
        speech_detected = False
        silence_counter = 0
        max_silence_count = int(self.sample_rate / self.chunk_size * 2)  # 2 seconds of silence
        start_time = time.time()
        
        print("Starting recording...")
        
        try:
            while self.is_recording:
                if self.pause_recording:
                    time.sleep(0.1)
                    continue
                
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.frames.append(data)
                
                # Calculate volume
                volume = self._calculate_volume(data)
                self.volume_change_signal.emit(volume)
                
                # Detect speech start and end
                if volume > self.threshold:
                    speech_detected = True
                    silence_counter = 0
                elif speech_detected:
                    silence_counter += 1
                
                # If minimum recording duration is reached and enough silence is detected, consider speech ended
                current_duration = time.time() - start_time
                if speech_detected and current_duration >= self.min_recording_duration and silence_counter >= max_silence_count:
                    break
            
            # If content was recorded and not exited due to stop command, send recording completed signal
            if self.frames and speech_detected:
                audio_data = b''.join(self.frames)
                self.recording_completed_signal.emit(audio_data)
        
        finally:
            # Clean up resources
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            
            print("Recording ended")
    
    # def _calculate_volume(self, data):
    #     """Calculate volume of audio data"""
    #     # Convert binary data to numpy array
    #     data_array = np.frombuffer(data, dtype=np.int16)
    #     # Calculate root mean square as volume indicator
    #     rms = np.sqrt(np.mean(np.square(data_array)))
    #     return rms

    def _calculate_volume(self, data):
        """计算音频数据的音量"""
        # 将二进制数据转换为numpy数组
        data_array = np.frombuffer(data, dtype=np.int16)

        # 如果数据为空或全为0，返回0
        if len(data_array) == 0 or np.all(data_array == 0):
            return 0.0

        # 计算均方根作为音量指标
        rms = np.sqrt(np.mean(np.square(data_array.astype(float))))
        return rms
    
    def stop(self):
        """Stop recording"""
        self.is_recording = False
        self.wait()
    
    def pause(self):
        """Pause recording"""
        self.pause_recording = True
    
    def resume(self):
        """Resume recording"""
        self.pause_recording = False


class PlaybackThread(QThread):
    """Background audio playback thread"""
    
    # Custom signals
    playback_completed_signal = pyqtSignal()
    
    def __init__(self, audio_data=None, file_path=None):
        super().__init__()
        
        self.audio_data = audio_data
        self.file_path = file_path
        self.is_playing = False
        self.pause_playback = False
        self.audio = pyaudio.PyAudio()
        self.stream = None
    
    def run(self):
        """Run playback thread"""
        self.is_playing = True
        
        try:
            # If file path is provided, read from file
            if self.file_path and os.path.exists(self.file_path):
                with wave.open(self.file_path, 'rb') as wf:
                    self._play_from_waveform(wf)
            
            # If audio data is provided, save it to temporary file and play
            elif self.audio_data:
                temp_file_path = "temp_audio.wav"
                with open(temp_file_path, 'wb') as f:
                    f.write(self.audio_data)
                
                with wave.open(temp_file_path, 'rb') as wf:
                    self._play_from_waveform(wf)
                
                # Delete temporary file
                try:
                    os.remove(temp_file_path)
                except:
                    pass
        
        finally:
            # Playback completed, emit signal
            self.playback_completed_signal.emit()
            self.is_playing = False
    
    def _play_from_waveform(self, waveform):
        """Play audio from waveform object"""
        # Open audio stream
        self.stream = self.audio.open(
            format=self.audio.get_format_from_width(waveform.getsampwidth()),
            channels=waveform.getnchannels(),
            rate=waveform.getframerate(),
            output=True
        )
        
        # Read data and play
        data = waveform.readframes(1024)
        
        while data and self.is_playing:
            # If paused, wait for resume
            if self.pause_playback:
                time.sleep(0.1)
                continue
            
            self.stream.write(data)
            data = waveform.readframes(1024)
        
        # Clean up resources
        self.stream.stop_stream()
        self.stream.close()
    
    def stop(self):
        """Stop playback"""
        self.is_playing = False
        self.wait()
    
    def pause(self):
        """Pause playback"""
        self.pause_playback = True
    
    def resume(self):
        """Resume playback"""
        self.pause_playback = False


class SpeechInteractionManager(QObject):
    """Class for managing speech recognition and synthesis"""
    
    # Custom signals
    recognition_result_signal = pyqtSignal(dict)
    synthesis_result_signal = pyqtSignal(dict)
    recording_status_signal = pyqtSignal(str)
    volume_change_signal = pyqtSignal(float)
    
    def __init__(self, app_id, api_key, secret_key):
        super().__init__()

        print(f"app_id:{app_id}")
        # Initialize Baidu speech API
        self.speech_api = BaiduSpeechService(app_id, api_key, secret_key)
        
        # Recording and playback threads
        self.recording_thread = None
        self.playback_thread = None
        
        # Status variables
        self.is_recording = False
        self.is_playing = False
    
    def start_recording(self):
        """Start recording"""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.recording_status_signal.emit("Recording started")
        
        # Create recording thread
        self.recording_thread = RecordingThread()
        self.recording_thread.recording_completed_signal.connect(self.handle_recording_completed)
        self.recording_thread.volume_change_signal.connect(self.volume_change_signal)
        self.recording_thread.start()
    
    def end_recording(self):
        """Manually end recording"""
        if not self.is_recording or not self.recording_thread:
            return
        
        self.recording_status_signal.emit("Recording ended")
        self.recording_thread.stop()
        self.is_recording = False
    
    def handle_recording_completed(self, audio_data):
        """Handle recording completion, send to speech recognition API"""
        self.is_recording = False
        self.recording_status_signal.emit("Recording completed")
        
        # Save recording to temporary file
        temp_file = f"temp_recording_{int(time.time())}.pcm"
        with open(temp_file, 'wb') as f:
            f.write(audio_data)
        
        # Use Baidu API for recognition
        try:
            recognition_result = self.speech_api.recognize_speech(audio_data)
            self.recognition_result_signal.emit(recognition_result)
        except Exception as e:
            self.recognition_result_signal.emit({"success": False, "error": str(e)})
        
        # Delete temporary file
        try:
            os.remove(temp_file)
        except:
            pass
    
    def synthesize_speech(self, text, volume=5, speed=5, pitch=5, voice=0):
        """Synthesize speech and play"""
        if not text:
            return
        
        # Use Baidu API to synthesize speech
        try:
            synthesis_result = self.speech_api.synthesize_speech(text, volume, speed, pitch, voice)
            self.synthesis_result_signal.emit(synthesis_result)
            
            # If synthesis successful, play audio
            if synthesis_result.get("success") and synthesis_result.get("audio_data"):
                self.play_audio(synthesis_result["audio_data"])
        except Exception as e:
            self.synthesis_result_signal.emit({"success": False, "error": str(e)})
    
    def play_audio(self, audio_data=None, file_path=None):
        """Play audio"""
        if self.is_playing:
            self.stop_playback()
        
        self.is_playing = True
        
        # Create playback thread
        self.playback_thread = PlaybackThread(audio_data, file_path)
        self.playback_thread.playback_completed_signal.connect(self.handle_playback_completed)
        self.playback_thread.start()
    
    def stop_playback(self):
        """Stop current playback"""
        if not self.is_playing or not self.playback_thread:
            return
        
        self.playback_thread.stop()
        self.is_playing = False
    
    def handle_playback_completed(self):
        """Handle playback completion"""
        self.is_playing = False
    
    def release_resources(self):
        """Release all resources"""
        if self.is_recording:
            self.end_recording()
        
        if self.is_playing:
            self.stop_playback()
