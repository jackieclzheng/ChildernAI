# Speech interaction module integration code

# from PyQt5.QtWidgets import QMenu, QAction, QPushButton, QFont

from PyQt5.QtWidgets import QMenu, QAction, QPushButton
from PyQt5.QtGui import QFont  # QFont应该从QtGui模块导入，而不是QtWidgets

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon

# from .speech_interface import SpeechInterface
from .baidu_speech_integration import SpeechInteractionManager




# def integrate_speech_module(main_interface):
#     """
#     Integrate speech interaction module into the main system interface
#
#     Args:
#         main_interface: Children main interface instance
#     """
#     # Add speech button to main interface
#     add_speech_button(main_interface)
#
#     # Create speech interaction manager
#     main_interface.speech_interaction_manager = create_speech_interaction_manager()
#
#     # Connect signals
#     connect_speech_signals(main_interface)


def integrate_speech_module(main_interface, speech_system=None):
    """
    Integrate speech interaction module into the main system interface

    Args:
        main_interface: Children main interface instance
        speech_system: Optional existing SpeechInteractionManager instance
    """
    # 添加语音按钮到主界面
    add_speech_button(main_interface)

    # 如果提供了外部语音系统实例，直接使用
    if speech_system:
        main_interface.speech_interaction_manager = speech_system
    else:
        # 否则创建新实例
        main_interface.speech_interaction_manager = create_speech_interaction_manager()

    # 连接信号
    connect_speech_signals(main_interface)


def add_speech_button(main_interface):
    """
    Add speech interaction button to main interface
    
    Args:
        main_interface: Children main interface instance
    """
    # Create speech button
    main_interface.speech_button = QPushButton()
    main_interface.speech_button.setIcon(QIcon("icons/mic.png"))
    main_interface.speech_button.setIconSize(QSize(32, 32))
    main_interface.speech_button.setFixedSize(50, 50)
    main_interface.speech_button.setStyleSheet("""
        QPushButton {
            background-color: #4A148C;
            border-radius: 25px;
            border: none;
        }
        QPushButton:hover {
            background-color: #6A1B9A;
        }
        QPushButton:pressed {
            background-color: #7B1FA2;
        }
    """)
    main_interface.speech_button.setToolTip("Speech Interaction")
    
    # Connect button click event
    main_interface.speech_button.clicked.connect(lambda: show_speech_menu(main_interface))
    
    # Add button to main interface bottom right corner
    main_interface.main_layout.addWidget(main_interface.speech_button, alignment=Qt.AlignRight | Qt.AlignBottom)


def show_speech_menu(main_interface):
    """
    Show speech interaction menu
    
    Args:
        main_interface: Children main interface instance
    """
    # Create menu
    menu = QMenu(main_interface)
    menu.setStyleSheet("""
        QMenu {
            background-color: white;
            border: 1px solid #E0E0E0;
            border-radius: 5px;
            padding: 5px;
        }
        QMenu::item {
            padding: 8px 30px 8px 30px;
            border-radius: 3px;
        }
        QMenu::item:selected {
            background-color: #E1BEE7;
        }
    """)
    
    # Add menu items
    quick_recognition_action = QAction(QIcon("icons/mic.png"), "Start Speech Recognition", main_interface)
    quick_recognition_action.triggered.connect(lambda: start_quick_speech_recognition(main_interface))
    
    voice_assistant_action = QAction(QIcon("icons/assistant.png"), "Open Voice Assistant", main_interface)
    voice_assistant_action.triggered.connect(lambda: open_voice_assistant_interface(main_interface))
    
    voice_settings_action = QAction(QIcon("icons/settings.png"), "Voice Settings", main_interface)
    voice_settings_action.triggered.connect(lambda: open_voice_settings(main_interface))
    
    # Add to menu
    menu.addAction(quick_recognition_action)
    menu.addAction(voice_assistant_action)
    menu.addAction(voice_settings_action)
    
    # Show menu
    menu.exec_(main_interface.speech_button.mapToGlobal(main_interface.speech_button.rect().topLeft()))


def create_speech_interaction_manager():
    """
    Create speech interaction manager instance
    
    Returns:
        Speech interaction manager instance
    """
    # Read API keys from configuration file
    import json
    import os
    
    # APP_ID = ""
    # API_KEY = ""
    # SECRET_KEY = ""

    APP_ID = "6632791"
    API_KEY = "u3Rn2MPnawYg6y1GvxDtuAPk"
    SECRET_KEY = "v3bvbSHK3hLmsKnoMkPTk8ApqlPBvPtB"
    
    # Try to load configuration file
    config_file_path = "config/speech_config.json"
    if os.path.exists(config_file_path):
        try:
            with open(config_file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            baidu_config = config.get("baidu_speech", {})
            APP_ID = baidu_config.get("app_id", "")
            API_KEY = baidu_config.get("api_key", "")
            SECRET_KEY = baidu_config.get("secret_key", "")
        except Exception as e:
            print(f"Failed to load speech configuration file: {str(e)}")
    
    # If configuration file doesn't exist or loading failed, use environment variables or default values
    if not all([APP_ID, API_KEY, SECRET_KEY]):
        import os
        APP_ID = os.environ.get("BAIDU_SPEECH_APP_ID", "")
        API_KEY = os.environ.get("BAIDU_SPEECH_API_KEY", "")
        SECRET_KEY = os.environ.get("BAIDU_SPEECH_SECRET_KEY", "")
        
        # If environment variables are not set either, use default example values and warn user
        if not all([APP_ID, API_KEY, SECRET_KEY]):
            print("Warning: No valid Baidu Speech API configuration found, speech functionality will not work properly.")
            print("Please set correct API keys in the configuration file.")
            # Use example values
            # APP_ID = "your_app_id"
            # API_KEY = "your_api_key"
            # SECRET_KEY = "your_secret_key"

            APP_ID = "6632791"
            API_KEY = "u3Rn2MPnawYg6y1GvxDtuAPk"
            SECRET_KEY = "v3bvbSHK3hLmsKnoMkPTk8ApqlPBvPtB"

            # "6632791", "u3Rn2MPnawYg6y1GvxDtuAPk",
            # "v3bvbSHK3hLmsKnoMkPTk8ApqlPBvPtB"


    
    # Create and return speech interaction manager instance
    return SpeechInteractionManager(APP_ID, API_KEY, SECRET_KEY)


def connect_speech_signals(main_interface):
    """
    Connect speech interaction related signals
    
    Args:
        main_interface: Children main interface instance
    """
    # Connect speech recognition result signal
    main_interface.speech_interaction_manager.recognition_result_signal.connect(lambda result: handle_speech_recognition_result(main_interface, result))
    
    # Connect speech status signal
    main_interface.speech_interaction_manager.recording_status_signal.connect(lambda status: update_speech_status(main_interface, status))


def start_quick_speech_recognition(main_interface):
    """
    Start quick speech recognition mode
    
    Args:
        main_interface: Children main interface instance
    """
    # Show recording status prompt
    from PyQt5.QtWidgets import QLabel, QVBoxLayout, QDialog, QProgressBar, QPushButton
    
    # Create recording dialog
    recording_dialog = QDialog(main_interface)
    recording_dialog.setWindowTitle("Speech Recognition")
    recording_dialog.setFixedSize(300, 200)
    recording_dialog.setStyleSheet("background-color: white;")
    
    # Create dialog layout
    dialog_layout = QVBoxLayout(recording_dialog)
    
    # Add prompt label
    prompt_label = QLabel("Please speak...")
    prompt_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
    prompt_label.setAlignment(Qt.AlignCenter)
    prompt_label.setStyleSheet("color: #4A148C; margin: 10px;")
    
    # Add microphone icon
    mic_label = QLabel()
    mic_label.setPixmap(QIcon("icons/mic.png").pixmap(64, 64))
    mic_label.setAlignment(Qt.AlignCenter)
    
    # Add volume progress bar
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
    
    # Add cancel button
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet("""
        QPushButton {
            background-color: #E0E0E0;
            border-radius: 5px;
            padding: 8px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #BDBDBD;
        }
    """)
    
    # Add components to layout
    dialog_layout.addWidget(prompt_label)
    dialog_layout.addWidget(mic_label)
    dialog_layout.addWidget(volume_progress_bar)
    dialog_layout.addWidget(cancel_button)
    
    # Connect cancel button
    cancel_button.clicked.connect(lambda: cancel_quick_recognition(main_interface, recording_dialog))
    
    # Connect volume signal
    main_interface.speech_interaction_manager.volume_change_signal.connect(lambda volume: update_volume_display(volume_progress_bar, volume))
    
    # Show dialog
    recording_dialog.show()
    
    # Start recording
    main_interface.speech_interaction_manager.start_recording()
    
    # Save dialog reference
    main_interface.current_recording_dialog = recording_dialog


def cancel_quick_recognition(main_interface, dialog):
    """
    Cancel quick speech recognition
    
    Args:
        main_interface: Children main interface instance
        dialog: Recording dialog instance
    """
    # Stop recording
    main_interface.speech_interaction_manager.end_recording()
    
    # Close dialog
    dialog.close()
    
    # Clear dialog reference
    main_interface.current_recording_dialog = None


def update_volume_display(progress_bar, volume):
    """
    Update volume progress bar display
    
    Args:
        progress_bar: QProgressBar instance
        volume: Volume level
    """
    # Map volume to 0-100 range
    volume_percentage = min(100, int(volume / 100))
    progress_bar.setValue(volume_percentage)


def handle_speech_recognition_result(main_interface, result):
    """
    Handle speech recognition result
    
    Args:
        main_interface: Children main interface instance
        result: Speech recognition result
    """
    # If there's a recording dialog, close it
    if hasattr(main_interface, "current_recording_dialog") and main_interface.current_recording_dialog:
        main_interface.current_recording_dialog.close()
        main_interface.current_recording_dialog = None
    
    # Process recognition result
    if result.get("success"):
        recognized_text = result.get("result", "")
        
        # Show recognition result
        show_recognition_result(main_interface, recognized_text)
        
        # Execute voice command
        execute_voice_command(main_interface, recognized_text)
    else:
        # Show error message
        error_message = result.get("error_msg", result.get("error", "Unknown error"))
        show_recognition_result(main_interface, f"Cannot recognize: {error_message}", is_error=True)


def show_recognition_result(main_interface, text, is_error=False):
    """
    Show speech recognition result
    
    Args:
        main_interface: Children main interface instance
        text: Recognized text or error message
        is_error: Whether it's an error message
    """
    from PyQt5.QtWidgets import QLabel, QVBoxLayout, QDialog, QTimer
    
    # Create prompt dialog
    prompt_dialog = QDialog(main_interface)
    prompt_dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
    prompt_dialog.setAttribute(Qt.WA_TranslucentBackground)
    prompt_dialog.setFixedSize(400, 100)
    
    # Create dialog layout
    layout = QVBoxLayout(prompt_dialog)
    
    # Create background frame
    background_frame = QLabel(prompt_dialog)
    background_frame.setStyleSheet("""
        background-color: white;
        border-radius: 10px;
        border: 1px solid #E0E0E0;
    """)
    background_frame.setGeometry(0, 0, 400, 100)
    
    # Create text label
    text_label = QLabel(text)
    text_label.setAlignment(Qt.AlignCenter)
    if is_error:
        text_label.setStyleSheet("color: #F44336; font-size: 14px; font-weight: bold;")
    else:
        text_label.setStyleSheet("color: #4A148C; font-size: 14px; font-weight: bold;")
    
    # Add label to layout
    layout.addWidget(text_label)
    
    # Show dialog
    prompt_dialog.show()
    
    # Set timer to auto-close after 3 seconds
    QTimer.singleShot(3000, prompt_dialog.close)


def execute_voice_command(main_interface, recognized_text):
    """
    Execute voice command from recognition
    
    Args:
        main_interface: Children main interface instance
        recognized_text: Recognized text
    """
    # Execute corresponding operation based on recognized text
    if "I want to hear a story" in recognized_text:
        # Open story interface
        if hasattr(main_interface, "open_story_interface"):
            main_interface.open_story_interface()
    
    elif "play children's song" in recognized_text:
        # Open children's song interface
        if hasattr(main_interface, "open_children_song_interface"):
            main_interface.open_children_song_interface()
    
    elif "I want to play games" in recognized_text:
        # Open game interface
        if hasattr(main_interface, "open_game_interface"):
            main_interface.open_game_interface()
    
    elif "learning" in recognized_text:
        # Open learning interface
        if hasattr(main_interface, "open_learning_interface"):
            main_interface.open_learning_interface()
    
    elif "complete" in recognized_text and "task" in recognized_text:
        # Handle habit formation task completion
        if hasattr(main_interface, "handle_habit_task_completion"):
            # Extract task name
            import re
            task_match = re.search(r"complete(.+?)task", recognized_text)
            if task_match:
                task_name = task_match.group(1).strip()
                main_interface.handle_habit_task_completion(task_name)
    
    # If no matching command, play prompt sound
    else:
        # Play unrecognized command prompt
        if hasattr(main_interface, "speech_interaction_manager"):
            main_interface.speech_interaction_manager.synthesize_speech("Sorry, I don't understand this command. Please try saying 'I want to hear a story' or 'I want to play games'.", voice=106)


# def open_voice_assistant_interface(main_interface):
#     """
#     Open voice assistant interface
#
#     Args:
#         main_interface: Children main interface instance
#     """
#     # Create and show voice assistant interface
#     if not hasattr(main_interface, "voice_assistant_interface") or not main_interface.voice_assistant_interface:
#         main_interface.voice_assistant_interface = SpeechInterface(main_interface)
#
#     main_interface.voice_assistant_interface.show()


def open_voice_assistant_interface(main_interface):
    """打开语音助手界面

    Args:
        main_interface: 主界面实例
    """
    # 使用主界面的内置语音交互功能而不是SpeechInterface
    main_interface.start_speech_interaction()


def open_voice_settings(main_interface):
    """
    Open voice settings interface
    
    Args:
        main_interface: Children main interface instance
    """
    # Create and show voice settings interface
    from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QSlider, QPushButton, QHBoxLayout, QGroupBox
    
    # Create settings dialog
    settings_dialog = QDialog(main_interface)
    settings_dialog.setWindowTitle("Voice Settings")
    settings_dialog.setFixedSize(400, 500)
    settings_dialog.setStyleSheet("background-color: white;")
    
    # Create main layout
    main_layout = QVBoxLayout(settings_dialog)
    
    # Create speech recognition settings group
    recognition_settings_group = QGroupBox("Speech Recognition Settings")
    recognition_settings_layout = QVBoxLayout(recognition_settings_group)
    
    # Add language model selection
    language_model_layout = QHBoxLayout()
    language_model_label = QLabel("Language Model:")
    language_model_selector = QComboBox()
    language_model_selector.addItems(["Mandarin General", "Mandarin Children", "English", "Cantonese", "Sichuan Dialect"])
    language_model_layout.addWidget(language_model_label)
    language_model_layout.addWidget(language_model_selector)
    recognition_settings_layout.addLayout(language_model_layout)
    
    # Add speech threshold setting
    threshold_layout = QHBoxLayout()
    threshold_label = QLabel("Speech Threshold:")
    threshold_slider = QSlider(Qt.Horizontal)
    threshold_slider.setRange(100, 1000)
    threshold_slider.setValue(500)
    threshold_layout.addWidget(threshold_label)
    threshold_layout.addWidget(threshold_slider)
    recognition_settings_layout.addLayout(threshold_layout)
    
    # Create speech synthesis settings group
    synthesis_settings_group = QGroupBox("Speech Synthesis Settings")
    synthesis_settings_layout = QVBoxLayout(synthesis_settings_group)
    
    # Add voice selection
    voice_layout = QHBoxLayout()
    voice_label = QLabel("Voice:")
    voice_selector = QComboBox()
    voice_selector.addItems(["Standard Female", "Standard Male", "Du Xiaoyao (Male)", "Du Yaya (Female)", "Du Xiaojiao (Female)", "Du Xiaotong (Child)"])
    voice_layout.addWidget(voice_label)
    voice_layout.addWidget(voice_selector)
    synthesis_settings_layout.addLayout(voice_layout)
    
    # Add speed setting
    speed_layout = QHBoxLayout()
    speed_label = QLabel("Speed:")
    speed_slider = QSlider(Qt.Horizontal)
    speed_slider.setRange(0, 15)
    speed_slider.setValue(5)
    speed_layout.addWidget(speed_label)
    speed_layout.addWidget(speed_slider)
    synthesis_settings_layout.addLayout(speed_layout)
    
    # Add pitch setting
    pitch_layout = QHBoxLayout()
    pitch_label = QLabel("Pitch:")
    pitch_slider = QSlider(Qt.Horizontal)
    pitch_slider.setRange(0, 15)
    pitch_slider.setValue(5)
    pitch_layout.addWidget(pitch_label)
    pitch_layout.addWidget(pitch_slider)
    synthesis_settings_layout.addLayout(pitch_layout)
    
    # Add volume setting
    volume_layout = QHBoxLayout()
    volume_label = QLabel("Volume:")
    volume_slider = QSlider(Qt.Horizontal)
    volume_slider.setRange(0, 15)
    volume_slider.setValue(5)
    volume_layout.addWidget(volume_label)
    volume_layout.addWidget(volume_slider)
    synthesis_settings_layout.addLayout(volume_layout)
    
    # Add test button
    test_button = QPushButton("Test Voice")
    test_button.setStyleSheet("""
        QPushButton {
            background-color: #4A148C;
            color: white;
            border-radius: 5px;
            padding: 8px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #6A1B9A;
        }
    """)
    
    # Add save button
    save_button = QPushButton("Save Settings")
    save_button.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            padding: 8px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #388E3C;
        }
    """)
    
    # Add cancel button
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet("""
        QPushButton {
            background-color: #E0E0E0;
            border-radius: 5px;
            padding: 8px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #BDBDBD;
        }
    """)
    
    # Create button layout
    button_layout = QHBoxLayout()
    button_layout.addWidget(test_button)
    button_layout.addWidget(save_button)
    button_layout.addWidget(cancel_button)
    
    # Add components to main layout
    main_layout.addWidget(recognition_settings_group)
    main_layout.addWidget(synthesis_settings_group)
    main_layout.addLayout(button_layout)
    
    # Connect button events
    test_button.clicked.connect(lambda: test_speech_synthesis(main_interface, voice_selector.currentIndex(), speed_slider.value(), pitch_slider.value(), volume_slider.value()))
    save_button.clicked.connect(lambda: save_voice_settings(main_interface, language_model_selector.currentIndex(), threshold_slider.value(), voice_selector.currentIndex(), speed_slider.value(), pitch_slider.value(), volume_slider.value(), settings_dialog))
    cancel_button.clicked.connect(settings_dialog.close)
    
    # Show settings dialog
    settings_dialog.exec_()


def test_speech_synthesis(main_interface, voice_index, speed, pitch, volume):
    """
    Test speech synthesis effect
    
    Args:
        main_interface: Children main interface instance
        voice_index: Voice selection index
        speed: Speed value
        pitch: Pitch value
        volume: Volume value
    """
    # Map voice index to Baidu API voice ID
    voice_mapping = [0, 1, 3, 4, 5, 106]
    voice_id = voice_mapping[voice_index]
    
    # Synthesize test speech
    test_text = "This is a test speech, you can adjust speed, pitch and volume."
    main_interface.speech_interaction_manager.synthesize_speech(test_text, volume, speed, pitch, voice_id)


def save_voice_settings(main_interface, language_model_index, threshold, voice_index, speed, pitch, volume, dialog):
    """
    Save voice settings
    
    Args:
        main_interface: Children main interface instance
        language_model_index: Language model selection index
        threshold: Speech threshold
        voice_index: Voice selection index
        speed: Speed value
        pitch: Pitch value
        volume: Volume value
        dialog: Settings dialog instance
    """
    # Map language model index to Baidu API language model ID
    language_model_mapping = [1537, 15372, 1737, 1637, 1837]
    language_model_id = language_model_mapping[language_model_index]
    
    # Map voice index to Baidu API voice ID
    voice_mapping = [0, 1, 3, 4, 5, 106]
    voice_id = voice_mapping[voice_index]
    
    # Save settings to configuration file
    import json
    import os
    
    config = {
        "speech_recognition": {
            "language_model_id": language_model_id,
            "threshold": threshold
        },
        "speech_synthesis": {
            "voice_id": voice_id,
            "speed": speed,
            "pitch": pitch,
            "volume": volume
        }
    }
    
    # Ensure configuration directory exists
    os.makedirs("config", exist_ok=True)
    
    # Save configuration
    with open("config/voice_settings.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    
    # Show save success prompt
    from PyQt5.QtWidgets import QMessageBox
    QMessageBox.information(dialog, "Save Successful", "Voice settings have been saved")
    
    # Close dialog
    dialog.close()


def update_speech_status(main_interface, status):
    """
    Update speech status display
    
    Args:
        main_interface: Children main interface instance
        status: Speech status
    """
    # In actual project, can update status bar or other UI elements to display current speech status
    print(f"Speech status: {status}")
