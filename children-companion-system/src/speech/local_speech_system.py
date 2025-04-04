import asyncio
import edge_tts
import speech_recognition as sr
from PyQt5.QtCore import QObject, pyqtSignal

class LocalSpeechSystem(QObject):
    """使用本地语音识别和Edge TTS进行语音合成的系统"""
    
    # 信号定义
    recognition_result_signal = pyqtSignal(dict)
    volume_change_signal = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        
    def start_recording(self):
        """开始录音并识别"""
        print("开始录音...")
        try:
            with sr.Microphone() as source:
                # 调整麦克风的环境噪声
                self.recognizer.adjust_for_ambient_noise(source)
                # 监听麦克风
                audio = self.recognizer.listen(source, timeout=5)
                
                try:
                    # 尝试识别语音
                    text = self.recognizer.recognize_google(audio, language="zh-CN")
                    print(f"识别结果: {text}")
                    
                    # 发送识别成功信号
                    self.recognition_result_signal.emit({
                        "success": True,
                        "result": text
                    })
                    
                except sr.UnknownValueError:
                    print("无法识别语音")
                    self.recognition_result_signal.emit({
                        "success": False,
                        "error_msg": "无法识别语音"
                    })
                    
                except sr.RequestError as e:
                    print(f"Google语音识别服务请求失败: {e}")
                    self.recognition_result_signal.emit({
                        "success": False,
                        "error_msg": f"语音识别服务请求失败: {e}"
                    })
        
        except Exception as e:
            print(f"录音过程中出错: {e}")
            self.recognition_result_signal.emit({
                "success": False,
                "error_msg": f"录音过程中出错: {e}"
            })
        
        print("录音结束")
    
    def synthesize_speech(self, text):
        """合成语音"""
        try:
            # 使用 edge-tts 进行语音合成
            import edge_tts
            import asyncio
            import tempfile
            import os
            
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_path = temp_file.name
            temp_file.close()
            
            async def generate_speech():
                communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
                await communicate.save(temp_path)
            
            # 运行异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(generate_speech())
            
            # 读取生成的音频文件
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # 清理临时文件
            os.unlink(temp_path)
            
            return {
                "success": True,
                "audio_data": audio_data
            }
            
        except Exception as e:
            print(f"语音合成失败: {str(e)}")
            return {
                "success": False,
                "error_msg": str(e)
            }
