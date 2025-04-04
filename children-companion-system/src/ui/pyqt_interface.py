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
        
        # 初始化语音缓存
        self.voice_cache = {}
        
        try:
            # 使用本地语音系统
            self.speech_service = LocalSpeechSystem()
            # 预先缓存常用提示音
            self.cache_common_prompts()
        except Exception as e:
            print(f"语音系统初始化失败: {str(e)}")
        
        # Set central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.initialize_interface()

    def cache_common_prompts(self):
        """缓存常用提示音"""
        try:
            common_prompts = ["进入首页", "进入故事", "进入儿歌", "进入游戏", "进入学习"]
            for prompt in common_prompts:
                result = self.speech_service.synthesize_speech(prompt)
                # 添加空值检查
                if result and result.get("success"):
                    self.voice_cache[prompt] = result["audio_data"]
                else:
                    print(f"缓存提示音失败: {prompt}")
        except Exception as e:
            print(f"缓存提示音时出错: {str(e)}")

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
        """创建主页面"""
        main_page = QWidget()
        layout = QVBoxLayout(main_page)

        # 示例功能列表
        features = [
            {"name": "故事", "color": "#FF5722", "icon": "icons/story.png"},
            {"name": "儿歌", "color": "#4CAF50", "icon": "icons/music.png"},
            {"name": "游戏", "color": "#2196F3", "icon": "icons/game.png"},
            {"name": "学习", "color": "#FFC107", "icon": "icons/learn.png"},
        ]

        for feature in features:
            button = self.create_feature_button(feature["name"], feature["color"], feature["icon"])
            layout.addWidget(button)

        return main_page

    def create_feature_button(self, name, color, icon_path):
        """创建功能按钮"""
        button = QPushButton(name)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: darken({color}, 10%);
            }}
        """)
        button.setMinimumSize(150, 150)

        # 如果提供了图标路径，添加图标
        if icon_path and os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(64, 64))

        return button

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
                        if "chinese" in voice.languages[0].lower():
                            engine.setProperty('voice', voice.id)
                            break

                    # 播放语音
                    engine.say(text)
                    engine.runAndWait()
                    
                    print(f"使用pyttsx3播放成功: {text}")
                    return True

                except Exception as e:
                    print(f"pyttsx3失败: {str(e)}")
                    return False

    def start_speech_interaction(self):
        """启动语音交互对话"""
        try:
            # 创建语音交互对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("语音助手")
            dialog.setMinimumWidth(400)
            
            # 创建对话框布局
            dialog_layout = QVBoxLayout(dialog)
            
            # 添加对话历史显示区域
            self.dialog_history = QTextEdit()
            self.dialog_history.setReadOnly(True)
            dialog_layout.addWidget(self.dialog_history)
            
            # 添加音量显示进度条
            self.volume_progress_bar = QProgressBar()
            self.volume_progress_bar.setStyleSheet("""
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
            dialog_layout.addWidget(self.volume_progress_bar)
            
            # 添加控制按钮
            button_layout = QHBoxLayout()
            
            start_button = QPushButton("开始对话")
            start_button.clicked.connect(self.start_voice_dialog)
            button_layout.addWidget(start_button)
            
            stop_button = QPushButton("停止")
            stop_button.clicked.connect(self.stop_voice_dialog)
            button_layout.addWidget(stop_button)
            
            dialog_layout.addLayout(button_layout)
            
            # 显示对话框
            dialog.exec_()
            
        except Exception as e:
            print(f"启动语音交互时出错: {str(e)}")

    def start_voice_dialog(self):
        """开始语音对话"""
        try:
            print("开始语音对话")
            if not hasattr(self, 'speech_recognition_manager'):
                from src.speech.local_speech_system import LocalSpeechSystem
                self.speech_recognition_manager = LocalSpeechSystem()
                
                # 连接信号
                self.speech_recognition_manager.recognition_result_signal.connect(
                    self.handle_speech_recognition_result
                )
                self.speech_recognition_manager.volume_change_signal.connect(
                    self.update_volume_display
                )
            
            self.speech_recognition_manager.start_recording()
            self.add_to_dialog_history("系统", "我在听，请说话...")
            
        except Exception as e:
            print(f"启动语音对话失败: {str(e)}")

    def stop_voice_dialog(self):
        """停止语音对话"""
        try:
            if hasattr(self, 'speech_recognition_manager'):
                self.speech_recognition_manager.stop_recording()
                print("停止录音")
        except Exception as e:
            print(f"停止录音失败: {str(e)}")

    def add_to_dialog_history(self, speaker, text):
        """添加对话到历史记录"""
        if hasattr(self, 'dialog_history'):
            self.dialog_history.append(f"{speaker}: {text}")

    def update_volume_display(self, volume):
        """更新音量显示"""
        try:
            if hasattr(self, 'volume_progress_bar'):
                if volume is not None and isinstance(volume, (int, float)) and not np.isnan(volume):
                    normalized_volume = min(100, max(0, int(volume / 30 * 100)))
                else:
                    normalized_volume = 0
                self.volume_progress_bar.setValue(normalized_volume)
        except Exception as e:
            print(f"更新音量显示时出错: {str(e)}")
            if hasattr(self, 'volume_progress_bar'):
                self.volume_progress_bar.setValue(0)

    def handle_speech_recognition_result(self, result):
        """处理语音识别结果"""
        print(f"语音识别结果: {result}")
        if result.get("success"):
            user_text = result.get("result", "")
            if user_text:
                self.add_to_dialog_history("用户", user_text)
                self.process_voice_command(user_text)
        else:
            error_msg = result.get("error_msg", "未知错误")
            print(f"语音识别失败: {error_msg}")
            self.add_to_dialog_history("系统", f"抱歉，我没有听清楚。({error_msg})")

    def switch_page(self, page_name):
        """切换页面"""
        try:
            # 更新当前页面
            self.current_section = page_name
            
            # 页面索引映射
            page_indices = {
                "首页": 0,
                "故事": 1,
                "儿歌": 2,
                "游戏": 3,
                "学习": 4,
                "习惯": 5
            }
            
            # 切换到对应页面
            if page_name in page_indices:
                self.content_stacked_widget.setCurrentIndex(page_indices[page_name])
                
                # 播放提示音
                prompt_text = f"进入{page_name}"
                if prompt_text in self.voice_cache:
                    self.play_voice_prompt(prompt_text)
                    
            print(f"切换到页面: {page_name}")
            
        except Exception as e:
            print(f"切换页面时出错: {str(e)}")