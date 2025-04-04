import sys
import os
import tempfile
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QGridLayout, QFrame, QScrollArea)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QColor, QPalette
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, QThread
from PyQt5.QtMultimedia import QSound

# 导入语音模块
from src.speech.baidu_speech_integration import BaiduSpeechService

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
        header_frame.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8E44AD, stop:1 #9B59B6); border-radius: 10px;")
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
        # 可以通过调用百度 API 的配额查询接口
        # 或者本地记录每日使用次数
        pass

    def play_voice_prompt(self, text):
        """播放语音提示"""
        # 先检查配额
        if not self.check_api_quota():
            print("API 配额不足")
            # 使用备选提示方式
            return False
        
        try:
            result = self.speech_service.synthesize_speech(text, volume=5, speed=5, pitch=5, voice=0)
            
            if not result.get("success"):
                error_code = result.get("error_code")
                if error_code == 502:  # API 限制错误
                    print("API 配额已用完,使用备选提示音")
                    # 使用系统提示音或预录制的音频作为备选
                    QSound.play("sounds/notification.wav")  # 需要预先准备提示音文件
                else:
                    print(f"语音合成失败: {result.get('error_msg')}")
            
            # 将音频数据保存到临时文件
            import tempfile
            import os
            
            # 确保临时目录存在
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
                
            # 使用固定路径而不是临时文件
            temp_file_path = os.path.join(temp_dir, f"voice_{int(time.time())}.mp3")
            
            with open(temp_file_path, 'wb') as temp_file:
                temp_file.write(result["audio_data"])
            
            print(f"语音文件已保存到: {temp_file_path}")
            
            # 检查文件是否成功创建
            if os.path.exists(temp_file_path) and os.path.getsize(temp_file_path) > 0:
                from PyQt5.QtMultimedia import QSound
                sound = QSound(temp_file_path)
                sound.play()
                
                # 保存引用以防止过早垃圾回收
                self.current_sound = sound
                print("语音播放已启动")
                
                # 添加一个定时器，在播放完成后删除临时文件
                def delete_temp_file():
                    try:
                        if os.path.exists(temp_file_path):
                            os.remove(temp_file_path)
                            print(f"临时文件已删除: {temp_file_path}")
                    except Exception as e:
                        print(f"删除临时文件时出错: {str(e)}")
                
                from PyQt5.QtCore import QTimer
                # 假设语音播放时间不超过10秒
                QTimer.singleShot(10000, delete_temp_file)
                
                return True
            else:
                print(f"创建语音文件失败: {temp_file_path}")
                return False
                
        except Exception as e:
            import traceback
            print(f"播放语音提示时出错: {str(e)}")
            print(traceback.format_exc())
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
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar, QTextEdit
        
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
        
    def stop_voice_dialog(self):
        """停止语音对话"""
        if hasattr(self, 'speech_recognition_manager'):
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
            
    def update_volume_display(self, volume):
        """更新音量显示"""
        if hasattr(self, 'volume_progress_bar'):
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
        # 简单的命令处理逻辑
        response = "我不太明白你的意思。"
        
        # 页面切换命令
        if "首页" in command or "主页" in command or "回到首页" in command:
            self.switch_page("首页")
            response = "已为您切换到首页。"
        elif "故事" in command:
            self.switch_page("故事")
            response = "已为您切换到故事页面。"
        elif "儿歌" in command or "歌曲" in command or "音乐" in command:
            self.switch_page("儿歌")
            response = "已为您切换到儿歌页面。"
        
        # 询问命令
        elif "你是谁" in command or "你叫什么" in command:
            response = "我是智能儿童伴侣系统，可以陪你学习、讲故事、唱儿歌，还有更多有趣的功能。"
        elif "你能做什么" in command or "你有什么功能" in command:
            response = "我可以为你讲故事、播放儿歌、提供游戏、辅助学习，还能帮助你养成好习惯。"
            
        # 添加系统回复到对话历史
        self.add_to_dialog_history("系统", response)
        
        # 语音播放回复
        self.play_voice_prompt(response)
    
    def create_feature_button(self, name, color, icon_path):
        """Create feature button"""
        button = QPushButton(name)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 10px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                /* 文本居中对齐  # text-align: bottom; */
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
        """测试百度语音合成功能"""
        test_text = "这是一个语音合成测试"
        print(f"正在测试语音合成: {test_text}")
        
        # 播放测试语音
        self.play_voice_prompt(test_text)
