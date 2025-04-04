import os
import sys

# Add project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.database.database_system import DatabaseManager
from src.speech.baidu_speech_integration import SpeechInteractionManager
from src.emotion.emotion_recognition import EmotionRecognitionSystem
from src.speech.speech_module_integration import integrate_speech_module

class MainProgram:
    """Intelligent Children Companion Interaction Software System Main Program"""
    
    def __init__(self):
        """Initialize main program"""
        # Initialize database
        self.database = DatabaseManager()
        self.database.initialize_database()
        
        # Initialize speech interaction system
        # Note: When actually using, need to replace with real API keys
        # self.speech_system = SpeechInteractionManager("your_app_id", "your_api_key", "your_secret_key")
        self.speech_system = SpeechInteractionManager("6632791", "u3Rn2MPnawYg6y1GvxDtuAPk","v3bvbSHK3hLmsKnoMkPTk8ApqlPBvPtB")
        # Initialize emotion recognition system
        self.emotion_system = EmotionRecognitionSystem()
        
        print("Intelligent Children Companion Interaction Software System initialization complete")
    
    def start(self):
        """Start main program"""
        # Import UI module
        # from src.ui.pyqt_interface import QApplication, ChildrenMainInterface, ParentControlInterface
        from src.ui.pyqt_interface import QApplication, ChildrenMainInterface
        
        # Create application instance
        app = QApplication(sys.argv)
        
        # Set application style
        app.setStyle("Fusion")
        
        # Show login interface
        # In actual project, should first show login interface, then display corresponding interface based on login user type
        # For demonstration purposes, directly show children main interface
        # window = ChildrenMainInterface()
        # window.show()

        # 修改后的代码
        window = ChildrenMainInterface()
        integrate_speech_module(window, self.speech_system)  # 添加了这一行
        window.show()
        
        # Run application
        sys.exit(app.exec_())

if __name__ == "__main__":
    # Create and start main program
    program = MainProgram()
    program.start()
