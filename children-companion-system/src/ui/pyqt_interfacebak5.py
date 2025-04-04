import sys
import os
import tempfile
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QGridLayout, QFrame, QScrollArea, QProgressBar, QTextEdit, QDialog)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QColor, QPalette
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, QThread
from PyQt5.QtMultimedia import QSound
# from src.speech.speech_interface import SpeechInterface  # 导入路径可能需要调整

# 导入语音模块
from src.speech.baidu_speech_integration import BaiduSpeechService
import numpy as np
from src.speech.local_speech_system import LocalSpeechSystem

class ChildrenMainInterface(QMainWindow):
    """儿童伴侣系统主界面"""

    # Define signals
    speech_interaction_request = pyqtSignal(bool)  # True to start, False to stop

    def __init__(self):
        super().__init__()

        # Set window basic properties
        self.setWindowTitle("智能儿童伴侣系统")
        self.setMinimumSize(800, 600)

        # Current active section
        self.current_section = "首页"

        # 初始化语音服务 - 使用正确的API密钥
        self.speech_service = BaiduSpeechService(
            "6632791",
            "u3Rn2MPnawYg6y1GvxDtuAPk",
            "v3bvbSHK3hLmsKnoMkPTk8ApqlPBvPtB"
        )

        # 初始化语音缓存
        self.voice_cache = {}
        # 预先缓存常用提示音
        self.cache_common_prompts()

        # Set central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.initialize_interface()

    def cache_common_prompts(self):
        """缓存常用提示音"""
        common_prompts = ["进入首页", "进入故事", "进入儿歌", "进入游戏", "进入学习"]
        for prompt in common_prompts:
            result = self.speech_service.synthesize_speech(prompt)
            if result.get("success"):
                self.voice_cache[prompt] = result["audio_data"]

    def initialize_interface(self):
        """Initialize all interface elements"""
        self.create_header_bar()
        self.create_content_area()
        self.create_bottom_navigation()

        # Initialize multimodal interaction system
        # self.multimodal_system = MultimodalInteractionSystem()

    def create_header_bar(self):
        """Create application top header bar"""
        header_frame = QFrame()
        header_frame.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8E44AD, stop:1 #9B59B6); border-radius: 10px;")
        header_frame.setMinimumHeight(80)
        header_frame.setMaximumHeight(80)

        header_layout = QHBoxLayout(header_frame)

        # Virtual avatar container
        avatar_container = QFrame()
        avatar_container.setStyleSheet("background-color: white; border-radius: 25px;")
        avatar_container.setMinimumSize(50, 50)
        avatar_container.setMaximumSize(50, 50)

        # Title label
        title_label = QLabel("智能伴侣")
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")

        # 添加语音助手按钮
        voice_assistant_button = QPushButton()
        voice_assistant_button.setIcon(QIcon("icons/mic.png"))
        voice_assistant_button.setIconSize(QSize(30, 30))
        voice_assistant_button.setStyleSheet("background-color: white; border-radius: 15px;")
        voice_assistant_button.setMinimumSize(30, 30)
        voice_assistant_button.setMaximumSize(30, 30)
        voice_assistant_button.setToolTip("语音助手")
        voice_assistant_button.clicked.connect(self.start_speech_interaction)

        # Settings button
        settings_button = QPushButton()
        settings_button.setIcon(QIcon("icons/settings.png"))  # Replace with real icon path in actual project
        settings_button.setIconSize(QSize(30, 30))
        settings_button.setStyleSheet("background-color: white; border-radius: 15px;")
        settings_button.setMinimumSize(30, 30)
        settings_button.setMaximumSize(30, 30)
        settings_button.setToolTip("设置")

        # Add to header layout
        header_layout.addWidget(avatar_container)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(voice_assistant_button)
        header_layout.addWidget(settings_button)

        self.main_layout.addWidget(header_frame)

    def create_content_area(self):
        """Create main content display area"""
        self.content_stacked_widget = QStackedWidget()

        # Create each section page
        self.main_page = self.create_main_page()
        self.story_page = self.create_story_page()
        self.children_song_page = self.create_children_song_page()
        self.game_page = self.create_game_page()
        self.learning_page = self.create_learning_page()
        self.habit_page = self.create_habit_page()

        # Add pages to stacked widget
        self.content_stacked_widget.addWidget(self.main_page)
        self.content_stacked_widget.addWidget(self.story_page)
        self.content_stacked_widget.addWidget(self.children_song_page)
        self.content_stacked_widget.addWidget(self.game_page)
        self.content_stacked_widget.addWidget(self.learning_page)
        self.content_stacked_widget.addWidget(self.habit_page)

        # Default to show main page
        self.content_stacked_widget.setCurrentIndex(0)

        self.main_layout.addWidget(self.content_stacked_widget)

    def create_main_page(self):
        """Create application main page"""
        page = QWidget()
        layout = QGridLayout(page)

        # Feature button data
        feature_list = [
            {"name": "故事", "color": "#AED581", "icon": "icons/book.png"},
            {"name": "儿歌", "color": "#FFD54F", "icon": "icons/music.png"},
            {"name": "游戏", "color": "#4FC3F7", "icon": "icons/game.png"},
            {"name": "学习", "color": "#FF8A65", "icon": "icons/learn.png"},
            {"name": "习惯养成", "color": "#BA68C8", "icon": "icons/habits.png"},
            {"name": "视频通话", "color": "#F06292", "icon": "icons/video.png"}
        ]

        # Create feature buttons
        row, column = 0, 0
        for feature in feature_list:
            button = self.create_feature_button(feature["name"], feature["color"], feature["icon"])
            layout.addWidget(button, row, column)

            column += 1
            if column > 1:
                column = 0
                row += 1

        return page

    def create_story_page(self):
        """创建故事页面"""
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("故事")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #689F38;")

        # Add story content in actual project
        layout.addWidget(title)
        layout.addWidget(QLabel("这里将显示故事内容"))

        return page

    def create_children_song_page(self):
        """创建儿歌页面"""
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("儿歌")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFA000;")

        # Add children songs content in actual project
        layout.addWidget(title)
        layout.addWidget(QLabel("这里将显示儿歌内容"))

        return page

    def create_game_page(self):
        """创建游戏页面"""
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("游戏")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0288D1;")

        # Add game content in actual project
        layout.addWidget(title)
        layout.addWidget(QLabel("这里将显示游戏内容"))

        return page

    def create_learning_page(self):
        """创建学习页面"""
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("学习中心")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #D32F2F;")

        button_layout = QGridLayout()

        learning_categories = ["识字", "算术", "英语", "科学", "阅读理解"]

        row, column = 0, 0
        for category in learning_categories:
            learning_button = QPushButton(category)
            learning_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFCDD2;
                    color: #D32F2F;
                    border-radius: 10px;
                    padding: 20px;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background-color: #EF9A9A;
                }
            """)
            learning_button.setMinimumHeight(100)

            button_layout.addWidget(learning_button, row, column)

            column += 1
            if column > 1:
                column = 0
                row += 1

        layout.addWidget(title)
        layout.addLayout(button_layout)
        layout.addStretch()

        return page

    def create_habit_page(self):
        """创建习惯养成页面"""
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("我的习惯")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #6A1B9A;")

        habit_list = QScrollArea()
        habit_list.setWidgetResizable(True)
        habit_container = QWidget()
        habit_list_layout = QVBoxLayout(habit_container)

        habit_data = [
            {"name": "按时起床", "time": "7:00", "completed": True},
            {"name": "刷牙", "time": "7:30", "completed": True},
            {"name": "阅读时间", "time": "20:00", "completed": False},
            {"name": "整理玩具", "time": "20:30", "completed": False}
        ]

        for habit in habit_data:
            habit_frame = QFrame()
            habit_frame.setStyleSheet("""
                QFrame {
                    background-color: #E1BEE7;
                    border-radius: 8px;
                    margin: 5px;
                }
            """)

            habit_layout = QHBoxLayout(habit_frame)

            habit_name = QLabel(habit["name"])
            habit_name.setStyleSheet("font-weight: bold; font-size: 14px;")

            habit_time = QLabel(habit["time"])

            complete_button = QPushButton("Completed" if habit["completed"] else "Complete")
            complete_button.setStyleSheet("""
                QPushButton {
                    background-color: #8E24AA;
                    color: white;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #6A1B9A;
                }
            """)

            habit_layout.addWidget(habit_name)
            habit_layout.addWidget(habit_time)
            habit_layout.addWidget(complete_button)

            habit_list_layout.addWidget(habit_frame)

        habit_list.setWidget(habit_container)

        new_habit_button = QPushButton("Add New Habit")
        new_habit_button.setStyleSheet("""
            QPushButton {
                background-color: #8E24AA;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #6A1B9A;
            }
        """)

        layout.addWidget(title)
        layout.addWidget(habit_list)
        layout.addWidget(new_habit_button)

        return page

    def create_bottom_navigation(self):
        """Create bottom navigation bar"""
        bottom_navigation_bar = QFrame()
        bottom_navigation_bar.setStyleSheet("background-color: white; border-top: 1px solid #E0E0E0;")
        bottom_navigation_bar.setMinimumHeight(60)
        bottom_navigation_bar.setMaximumHeight(60)

        navigation_layout = QHBoxLayout(bottom_navigation_bar)
        navigation_layout.setSpacing(0)

        # Navigation item data
        navigation_item_list = [
            {"name": "首页", "icon": "icons/home.png"},
            {"name": "故事", "icon": "icons/book.png"},
            {"name": "儿歌", "icon": "icons/music.png"},
            {"name": "游戏", "icon": "icons/game.png"},
            {"name": "学习", "icon": "icons/learn.png"}
        ]

        # Create navigation buttons
        for navigation_item in navigation_item_list:
            navigation_button = QPushButton(navigation_item["name"])
            navigation_button.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 10px;
                    text-align: center;
                    color: #757575;
                }
                QPushButton:hover {
                    background-color: #F5F5F5;
                }
            """)

            # Add icon in actual project
            # navigation_button.setIcon(QIcon(navigation_item["icon"]))
            # navigation_button.setIconSize(QSize(24, 24))

            navigation_button.clicked.connect(lambda checked, name=navigation_item["name"]: self.switch_page(name))
            navigation_layout.addWidget(navigation_button)

        self.main_layout.addWidget(bottom_navigation_bar)

    def check_api_quota(self):
        """检查 API 配额"""
        # 这个简单实现始终返回False，表示不使用百度API
        return False

    def play_voice_prompt(self, text):
        """整合多种TTS方案的语音提示播放功能"""
        # 首先检查是否已缓存该提示音
        if text in self.voice_cache:
            try:
                audio_data = self.voice_cache[text]

                temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)

                temp_file_path = os.path.join(temp_dir, f"voice_cache_{int(time.time())}.mp3")
                with open(temp_file_path, 'wb') as temp_file:
                    temp_file.write(audio_data)

                # 直接使用pygame播放
                try:
                    from pygame import mixer
                    mixer.init()
                    mixer.music.load(temp_file_path)
                    mixer.music.play()

                    # 保存引用以防止垃圾回收
                    self.current_sound = mixer

                    # 等待播放完成
                    while mixer.music.get_busy():
                        time.sleep(0.1)

                    print(f"使用缓存播放: {text}")

                    # 添加定时器删除临时文件
                    def delete_temp_file():
                        try:
                            if os.path.exists(temp_file_path):
                                os.remove(temp_file_path)
                                print(f"临时文件已删除: {temp_file_path}")
                        except Exception as e:
                            print(f"删除临时文件时出错: {str(e)}")

                    QTimer.singleShot(1000, delete_temp_file)
                    return True
                except Exception as e:
                    print(f"pygame播放失败: {str(e)}")
                    return False
            except Exception as e:
                print(f"使用缓存播放失败: {str(e)}")
                # 如果缓存播放失败，继续尝试其他方式

        print(f"开始语音合成: {text}")

        # 尝试方法1: edge-tts (最高质量)
        try:
            import asyncio
            import edge_tts

            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            temp_file_path = os.path.join(temp_dir, f"voice_edge_{int(time.time())}.mp3")

            # 定义异步函数
            async def generate_voice():
                # 使用中文女声
                communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
                await communicate.save(temp_file_path)

            # 执行异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(generate_voice())

            # 使用pygame播放
            try:
                from pygame import mixer
                mixer.init()
                mixer.music.load(temp_file_path)
                mixer.music.play()

                # 等待播放完成
                while mixer.music.get_busy():
                    time.sleep(0.1)

                # 保存引用以防止垃圾回收
                self.current_sound = mixer

                # 保存到缓存
                with open(temp_file_path, 'rb') as f:
                    self.voice_cache[text] = f.read()

                # 添加定时器删除临时文件
                def delete_temp_file():
                    try:
                        if os.path.exists(temp_file_path):
                            os.remove(temp_file_path)
                            print(f"临时文件已删除: {temp_file_path}")
                    except Exception as e:
                        print(f"删除临时文件时出错: {str(e)}")

                QTimer.singleShot(1000, delete_temp_file)

                print(f"使用edge-tts播放成功: {text}")
                return True
            except Exception as e:
                print(f"pygame播放失败: {str(e)}")
                return False

        except Exception as e:
            print(f"edge-tts失败: {str(e)}")

            # 尝试方法2: gTTS
            try:
                from gtts import gTTS

                temp_file_path = os.path.join(temp_dir, f"voice_gtts_{int(time.time())}.mp3")

                # 生成语音文件
                tts = gTTS(text=text, lang='zh-cn')
                tts.save(temp_file_path)

                # 尝试使用pygame播放
                try:
                    from pygame import mixer
                    mixer.init()
                    mixer.music.load(temp_file_path)
                    mixer.music.play()

                    # 等待播放完成
                    while mixer.music.get_busy():
                        time.sleep(0.1)

                    # 保存引用以防止垃圾回收
                    self.current_sound = mixer

                    # 保存到缓存
                    with open(temp_file_path, 'rb') as f:
                        self.voice_cache[text] = f.read()

                    # 添加定时器删除临时文件
                    def delete_temp_file():
                        try:
                            if os.path.exists(temp_file_path):
                                os.remove(temp_file_path)
                                print(f"临时文件已删除: {temp_file_path}")
                        except Exception as e:
                            print(f"删除临时文件时出错: {str(e)}")

                    QTimer.singleShot(1000, delete_temp_file)

                    print(f"使用gTTS播放成功: {text}")
                    return True

                except Exception as e:
                    print(f"pygame播放失败: {str(e)}")
                    return False

            except Exception as e:
                print(f"gTTS失败: {str(e)}")

                # 尝试方法3: pyttsx3 (备选方案)
                try:
                    import pyttsx3
                    engine = pyttsx3.init()

                    # 设置语音属性
                    engine.setProperty('rate', 150)  # 语速
                    engine.setProperty('volume', 0.9)  # 音量

                    # 在Windows上可以设置中文女声
                    voices = engine.getProperty('voices')
                    for voice in voices:
                        if "chinese" in voice.name.lower() and "female" in voice.name.lower():
                            engine.setProperty('voice', voice.id)
                            break

                    # 播放语音
                    engine.say(text)
                    engine.runAndWait()
                    print(f"使用pyttsx3播放成功: {text}")
                    return True

                except Exception as e:
                    print(f"pyttsx3失败: {str(e)}")

                    # 所有方法都失败，播放备用提示音
                    try:
                        # 确保音频文件存在
                        sound_file = "sounds/notification.wav"
                        if not os.path.exists(sound_file):
                            # 如果文件不存在，创建一个简单的提示音
                            sound_dir = os.path.dirname(sound_file)
                            if not os.path.exists(sound_dir):
                                os.makedirs(sound_dir)

                            # 生成简单提示音（使用pygame生成）
                            try:
                                from pygame import sndarray, mixer
                                import numpy as np

                                mixer.init(frequency=44100, size=-16, channels=2)
                                duration = 0.2  # 短促提示音
                                sample_rate = 44100

                                # 创建简单的叮咚声
                                t = np.linspace(0, duration, int(sample_rate * duration), False)
                                note = np.sin(2 * np.pi * 440 * t) * np.exp(-5 * t)

                                sound_array = (note * 32767).astype(np.int16)
                                stereo_sound = np.column_stack((sound_array, sound_array))

                                snd = sndarray.make_sound(stereo_sound)
                                snd.play()

                                # 等待播放完成
                                time.sleep(duration + 0.1)
                                print("使用生成的提示音")
                                return True
                            except Exception as e:
                                print(f"无法生成提示音: {str(e)}")
                                return False

                        QSound.play(sound_file)
                        print("使用备用提示音")
                        return True
                    except Exception as e:
                        print(f"备用提示音播放失败: {str(e)}")
                        return False

    def switch_page(self, page_name):
        """切换到指定页面"""
        self.current_section = page_name

        # 使用更简短的提示文本
        prompt_text = f"进入{page_name}"
        self.play_voice_prompt(prompt_text)

        # 切换页面显示
        if page_name == "首页":
            self.content_stacked_widget.setCurrentIndex(0)
        elif page_name == "故事":
            self.content_stacked_widget.setCurrentIndex(1)
        elif page_name == "儿歌":
            self.content_stacked_widget.setCurrentIndex(2)
        elif page_name == "游戏":
            self.content_stacked_widget.setCurrentIndex(3)
        elif page_name == "学习":
            self.content_stacked_widget.setCurrentIndex(4)
        elif page_name == "习惯养成":
            self.content_stacked_widget.setCurrentIndex(5)

        print(f"已切换到: {page_name}")

    def start_speech_interaction(self):
        """启动语音交互功能"""
        self.speech_interaction_request.emit(True)

        # 创建语音交互对话框
        self.create_voice_interaction_dialog()

    def stop_speech_interaction(self):
        """停止语音交互功能"""
        self.speech_interaction_request.emit(False)

        # 如果存在对话框，关闭它
        if hasattr(self, 'voice_dialog') and self.voice_dialog:
            self.voice_dialog.close()

    def create_voice_interaction_dialog(self):
        """创建语音交互对话框"""
        # 创建对话框
        self.voice_dialog = QDialog(self)
        self.voice_dialog.setWindowTitle("语音交互")
        self.voice_dialog.setFixedSize(400, 500)
        self.voice_dialog.setStyleSheet("background-color: white;")

        # 创建对话框布局
        dialog_layout = QVBoxLayout(self.voice_dialog)

        # 添加提示标签
        prompt_label = QLabel("请说话...")
        prompt_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        prompt_label.setAlignment(Qt.AlignCenter)
        prompt_label.setStyleSheet("color: #4A148C; margin: 10px;")

        # 添加麦克风图标
        mic_label = QLabel()
        mic_label.setPixmap(QIcon("icons/mic.png").pixmap(64, 64))
        mic_label.setAlignment(Qt.AlignCenter)

        # 添加音量进度条
        volume_progress_bar = QProgressBar()
        volume_progress_bar.setRange(0, 100)
        volume_progress_bar.setValue(0)
        volume_progress_bar.setTextVisible(False)
        volume_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #C5CAE9;
                border-radius: 3px;
                background-color: #FFFFFF;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3F51B5;
                width: 5px;
                margin: 0.5px;
            }
        """)

        # 添加对话历史文本框
        self.dialog_history = QTextEdit()
        self.dialog_history.setReadOnly(True)
        self.dialog_history.setStyleSheet("""
            QTextEdit {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 10px;
                background-color: #F5F5F5;
                font-size: 14px;
            }
        """)
        self.dialog_history.setMinimumHeight(200)

        # 添加按钮
        button_layout = QHBoxLayout()

        # 开始录音按钮
        start_button = QPushButton("开始对话")
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)

        # 停止按钮
        stop_button = QPushButton("停止")
        stop_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)

        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)

        # 添加按钮到布局
        button_layout.addWidget(start_button)
        button_layout.addWidget(stop_button)
        button_layout.addWidget(close_button)

        # 添加组件到对话框布局
        dialog_layout.addWidget(prompt_label)
        dialog_layout.addWidget(mic_label)
        dialog_layout.addWidget(volume_progress_bar)
        dialog_layout.addWidget(self.dialog_history)
        dialog_layout.addLayout(button_layout)

        # 连接按钮信号
        start_button.clicked.connect(self.start_voice_dialog)
        stop_button.clicked.connect(self.stop_voice_dialog)
        close_button.clicked.connect(self.voice_dialog.close)

        # 保存进度条引用
        self.volume_progress_bar = volume_progress_bar

        # 显示对话框
        self.voice_dialog.show()

    def start_voice_dialog(self):
        """开始语音对话"""
        # 初始化语音识别管理器（如果尚未初始化）
        if not hasattr(self, 'speech_recognition_manager'):
            from src.speech.baidu_speech_integration import SpeechInteractionManager
            # 使用正确的API密钥
            self.speech_recognition_manager = SpeechInteractionManager(
                "6632791",
                "u3Rn2MPnawYg6y1GvxDtuAPk",
                "v3bvbSHK3hLmsKnoMkPTk8ApqlPBvPtB"
            )

            # 连接信号
            self.speech_recognition_manager.recognition_result_signal.connect(self.handle_speech_recognition_result)
            self.speech_recognition_manager.volume_change_signal.connect(self.update_volume_display)

        # 开始录音
        self.speech_recognition_manager.start_recording()

        # 添加系统消息到对话历史
        self.add_to_dialog_history("系统", "我在听，请说话...")

    # def stop_voice_dialog(self):
    #     """停止语音对话"""
    #     if hasattr(self, 'speech_recognition_manager'):
    #         self.speech_recognition_manager.stop_recording()

    def stop_voice_dialog(self):
        """停止语音对话"""
        if hasattr(self, 'speech_recognition_manager'):
            if hasattr(self.speech_recognition_manager, 'end_recording'):
                self.speech_recognition_manager.end_recording()
            elif hasattr(self.speech_recognition_manager, 'stop_recording'):
                self.speech_recognition_manager.stop_recording()

    def handle_speech_recognition_result(self, result):
        """处理语音识别结果"""
        if result.get("success"):
            user_text = result.get("result", "")

            # 添加用户消息到对话历史
            self.add_to_dialog_history("用户", user_text)

            # 处理用户语音命令
            self.process_voice_command(user_text)
        else:
            error_msg = result.get("error_msg", "未知错误")
            print(f"语音识别失败: {error_msg}")

            # 添加错误消息到对话历史
            self.add_to_dialog_history("系统", f"抱歉，我没有听清楚。({error_msg})")

    # def update_volume_display(self, volume):
    #     """更新音量显示"""
    #     if hasattr(self, 'volume_progress_bar'):
    #         # 将音量值映射到0-100范围
    #         normalized_volume = min(100, max(0, int(volume / 30 * 100)))
    #         self.volume_progress_bar.setValue(normalized_volume)

    def update_volume_display(self, volume):
        """更新音量显示"""
        if hasattr(self, 'volume_progress_bar'):
            # 检查volume是否为NaN，如果是则使用0
            if np.isnan(volume):
                volume = 0.0

            # 将音量值映射到0-100范围
            normalized_volume = min(100, max(0, int(volume / 30 * 100)))
            self.volume_progress_bar.setValue(normalized_volume)

    def add_to_dialog_history(self, speaker, message):
        """添加消息到对话历史"""
        if hasattr(self, 'dialog_history'):
            # 格式化消息
            formatted_message = f"<b>{speaker}:</b> {message}<br>"

            # 添加到对话历史
            current_html = self.dialog_history.toHtml()
            self.dialog_history.setHtml(current_html + formatted_message)

            # 滚动到底部
            self.dialog_history.verticalScrollBar().setValue(
                self.dialog_history.verticalScrollBar().maximum()
            )

    def process_voice_command(self, command):
        """处理语音命令"""
        # 使用更智能的命令识别逻辑
        command = command.lower()
        response = None
        executed = False

        # 1. 页面导航命令
        navigation_commands = {
            "首页": ["首页", "主页", "回到首页", "返回首页", "回主页"],
            "故事": ["故事", "讲故事", "听故事", "看故事", "想听故事"],
            "儿歌": ["儿歌", "唱歌", "听歌", "歌曲", "音乐", "想听歌"],
            "游戏": ["游戏", "玩游戏", "玩耍", "想玩游戏"],
            "学习": ["学习", "学习中心", "我要学习", "学东西"],
            "习惯养成": ["习惯", "习惯养成", "好习惯", "养成习惯"]
        }

        for page, keywords in navigation_commands.items():
            if any(keyword in command for keyword in keywords):
                self.switch_page(page)
                response = f"已为您切换到{page}页面。"
                executed = True
                break

        # 2. 系统信息查询
        if not executed:
            if any(word in command for word in ["你是谁", "你叫什么", "你的名字"]):
                response = "我是智能儿童伴侣系统，可以陪你学习、讲故事、唱儿歌，还有更多有趣的功能。"
                executed = True
            elif any(word in command for word in ["你能做什么", "你有什么功能", "帮我做什么"]):
                response = "我可以为你讲故事、播放儿歌、提供游戏、辅助学习，还能帮助你养成好习惯。你想尝试哪个功能呢？"
                executed = True
            elif "几点" in command or "时间" in command:
                import datetime
                now = datetime.datetime.now()
                response = f"现在时间是{now.hour}点{now.minute}分。"
                executed = True

        # 3. 故事相关命令
        if not executed and "故事" in command:
            if "讲个" in command or "讲一个" in command or "说一个" in command:
                response = "好的，我来讲一个小故事。从前有只小兔子，它很喜欢吃胡萝卜..."
                # 这里可以调用故事模块随机获取一个故事
                executed = True
            elif "继续" in command or "接着讲" in command:
                response = "好的，我继续讲故事。小兔子在森林里遇到了一只狐狸..."
                executed = True

        # 4. 学习相关命令
        if not executed and "学习" in command:
            subjects = ["识字", "算术", "英语", "科学", "阅读理解"]
            for subject in subjects:
                if subject in command:
                    response = f"好的，让我们开始学习{subject}吧！"
                    # 这里可以打开相应的学习内容
                    executed = True
                    break

        # 5. 互动对话命令
        if not executed:
            greetings = ["你好", "早上好", "晚上好", "下午好", "嗨", "哈喽"]
            if any(greeting in command for greeting in greetings):
                import datetime
                hour = datetime.datetime.now().hour
                if hour < 12:
                    greeting = "早上好"
                elif hour < 18:
                    greeting = "下午好"
                else:
                    greeting = "晚上好"
                response = f"{greeting}！我很高兴见到你，有什么我能帮助你的吗？"
                executed = True
            elif "再见" in command or "拜拜" in command:
                response = "再见！希望很快能再次见到你。"
                executed = True

        # 6. 默认响应
        if not executed:
            response = "我不太明白你的意思。你可以尝试说'讲个故事'或'我想学习'这样的命令。"

        # 添加系统回复到对话历史
        self.add_to_dialog_history("系统", response)

        # 语音播放回复
        self.play_voice_prompt(response)

    def create_feature_button(self, name, color, icon_path):
        """创建功能按钮"""
        button = QPushButton(name)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 10px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: darken({color}, 10%);
            }}
        """)
        button.setMinimumSize(150, 150)

        # Add icon in actual project
        # button.setIcon(QIcon(icon_path))
        # button.setIconSize(QSize(64, 64))

        button.clicked.connect(lambda: self.switch_page(name))
        return button

    def test_speech_synthesis(self):
        """测试语音合成功能"""
        test_text = "这是一个语音合成测试"
        print(f"正在测试语音合成: {test_text}")

        # 播放测试语音
        self.play_voice_prompt(test_text)


class ParentControlInterface(QMainWindow):
    """家长控制中心界面"""

    def __init__(self):
        super().__init__()

        # Set window basic properties
        self.setWindowTitle("家长控制中心")
        self.setMinimumSize(1000, 700)

        # Set central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.initialize_interface()

    def initialize_interface(self):
        """Initialize all interface elements"""
        self.create_header_bar()
        self.create_content_area()

    def create_header_bar(self):
        """Create application top header bar"""
        header_frame = QFrame()
        header_frame.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1976D2, stop:1 #2196F3); border-radius: 10px;")
        header_frame.setMinimumHeight(80)
        header_frame.setMaximumHeight(80)

        header_layout = QHBoxLayout(header_frame)

        # Title label
        title_label = QLabel("Parent Control Center")
        title_label.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")

        # User information
        user_info = QLabel("Welcome, Parent User")
        user_info.setStyleSheet("color: white; font-size: 14px;")

        # Exit button
        exit_button = QPushButton("Exit")
        exit_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #1976D2;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E3F2FD;
            }
        """)

        # Add to header layout
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(user_info)
        header_layout.addWidget(exit_button)

        self.main_layout.addWidget(header_frame)

    def create_content_area(self):
        """Create main content display area"""
        content_area = QHBoxLayout()

        # Create left navigation
        left_navigation = self.create_left_navigation()
        left_navigation.setMaximumWidth(200)

        # Create right content area
        self.content_stacked_widget = QStackedWidget()

        # Create each section page
        self.usage_statistics_page = self.create_usage_statistics_page()
        self.time_control_page = self.create_time_control_page()
        self.content_filter_page = self.create_content_filter_page()
        self.learning_progress_page = self.create_learning_progress_page()
        self.habit_formation_page = self.create_habit_formation_page()
        self.basic_settings_page = self.create_basic_settings_page()

        # Add pages to stacked widget
        self.content_stacked_widget.addWidget(self.usage_statistics_page)
        self.content_stacked_widget.addWidget(self.time_control_page)
        self.content_stacked_widget.addWidget(self.content_filter_page)
        self.content_stacked_widget.addWidget(self.learning_progress_page)
        self.content_stacked_widget.addWidget(self.habit_formation_page)
        self.content_stacked_widget.addWidget(self.basic_settings_page)

        # Default to show usage statistics page
        self.content_stacked_widget.setCurrentIndex(0)

        content_area.addWidget(left_navigation)
        content_area.addWidget(self.content_stacked_widget)

        self.main_layout.addLayout(content_area)

    def create_left_navigation(self):
        """Create left navigation bar"""
        navigation_frame = QFrame()
        navigation_frame.setStyleSheet("background-color: #F5F5F5; border-radius: 10px;")

        navigation_layout = QVBoxLayout(navigation_frame)

        # Navigation item data
        navigation_item_list = [
            {"name": "Usage Statistics", "icon": "icons/stats.png"},
            {"name": "Time Control", "icon": "icons/time.png"},
            {"name": "Content Filter", "icon": "icons/filter.png"},
            {"name": "Learning Progress", "icon": "icons/progress.png"},
            {"name": "Habit Formation", "icon": "icons/habits.png"},
            {"name": "Basic Settings", "icon": "icons/settings.png"}
        ]

        # Create navigation buttons
        for navigation_item in navigation_item_list:
            navigation_button = QPushButton(navigation_item["name"])
            navigation_button.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    text-align: left;
                    color: #424242;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #E0E0E0;
                }
            """)

            # Add icon in actual project
            # navigation_button.setIcon(QIcon(navigation_item["icon"]))
            # navigation_button.setIconSize(QSize(20, 20))

            navigation_button.clicked.connect(lambda checked, name=navigation_item["name"]: self.switch_page(name))
            navigation_layout.addWidget(navigation_button)

        navigation_layout.addStretch()

        return navigation_frame

    def create_usage_statistics_page(self):
        """Create usage statistics page"""
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Usage Statistics")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1976D2;")

        # Add usage statistics content in actual project
        layout.addWidget(title)
        layout.addWidget(QLabel("Usage statistics content will be displayed here"))

        return page

    def create_time_control_page(self):
        """Create time control page"""
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Time Control")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1976D2;")

        # Add time control content in actual project
        layout.addWidget(title)
        layout.addWidget(QLabel("Time control content will be displayed here"))

        return page

    def create_content_filter_page(self):
        """Create content filter page"""
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Content Filter")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1976D2;")

        # Add content filter content in actual project
        layout.addWidget(title)
        layout.addWidget(QLabel("Content filter content will be displayed here"))

        return page

    def create_learning_progress_page(self):
        """Create learning progress page"""
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Learning Progress")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1976D2;")

        # Add learning progress content in actual project
        layout.addWidget(title)
        layout.addWidget(QLabel("Learning progress content will be displayed here"))

        return page

    def create_habit_formation_page(self):
        """Create habit formation page"""
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Habit Formation")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1976D2;")

        # Add habit formation content in actual project
        layout.addWidget(title)
        layout.addWidget(QLabel("Habit formation content will be displayed here"))

        return page

    def create_basic_settings_page(self):
        """Create basic settings page"""
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Basic Settings")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1976D2;")

        # Add basic settings content in actual project
        layout.addWidget(title)
        layout.addWidget(QLabel("Basic settings content will be displayed here"))

        return page

    def switch_page(self, page_name):
        """Switch to specified page"""
        if page_name == "Usage Statistics":
            self.content_stacked_widget.setCurrentIndex(0)
        elif page_name == "Time Control":
            self.content_stacked_widget.setCurrentIndex(1)
        elif page_name == "Content Filter":
            self.content_stacked_widget.setCurrentIndex(2)
        elif page_name == "Learning Progress":
            self.content_stacked_widget.setCurrentIndex(3)
        elif page_name == "Habit Formation":
            self.content_stacked_widget.setCurrentIndex(4)
        elif page_name == "Basic Settings":
            self.content_stacked_widget.setCurrentIndex(5)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Create and display children main interface
    window = ChildrenMainInterface()

    # Create and display parent control interface
    # window = ParentControlInterface()

    window.show()
    sys.exit(app.exec_())