
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

# Environment setup
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Assistant")  # Default if not found
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
GraphicsDirPath = os.path.join(current_dir, "Frontend", "Graphics")
def AnswerModifier(Answer):
    lines = Answer.split('\n')  # Split the text into lines
    non_empty_lines = [line for line in lines if line.strip()]  # Remove empty lines
    modified_answer = '\n'.join(non_empty_lines)  # Rejoin the lines
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()  # Convert to lowercase and trim spaces
    query_words = new_query.split()  # Split into words

    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", 
                      "can you", "what's", "where's", "how's"]

    # Check if query starts with a question word
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"  # Ensure it ends with a question mark
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."  # Replace last punctuation with '?'
        else:
            new_query += "."  # Append '?' if no punctuation is present

    return new_query.capitalize()  # Capitalize the first letter
def safe_load_icon(path, default_size=(60, 60)):
    """Safely loads an icon from path with error handling"""
    if not os.path.exists(path):
        print(f"Warning: Icon file not found: {path}")
        # Create a colored placeholder pixmap if file is missing
        pixmap = QPixmap(default_size[0], default_size[1])
        pixmap.fill(Qt.gray)
        return pixmap
    return QPixmap(path)

def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Responses.data', "w", encoding='utf-8') as file:
        file.write(Text)

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data', "r", encoding='utf-8') as file:
        Status = file.read()
    return Status
def GraphicsDirectoryPath(filename):
    """Get the full path for a graphics file"""
    return os.path.join(GraphicsDirPath, filename)

def TempDirectoryPath(filename):
    """Get the full path for a temp file"""
    return os.path.join(TempDirPath, filename)

def SetMicrophoneStatus(command):
    """Write microphone status to file"""
    with open(TempDirectoryPath('Mic.data'), "w", encoding='utf-8') as file:
        file.write(command)

def GetMicrophoneStatus():
    """Read microphone status from file"""
    try:
        with open(TempDirectoryPath('Mic.data'), "r", encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "False"

def MicButtonInitialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        desktop = QApplication.primaryScreen()
        screen_width = desktop.size().width()
        screen_height = desktop.size().height()
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # GIF Label with error handling
        self.gif_label = QLabel()
        gif_path = GraphicsDirectoryPath('Jarvis.gif')
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            max_gif_size_H = int(screen_width / 1.69)
            movie.setScaledSize(QSize(screen_width, max_gif_size_H))
            self.gif_label.setMovie(movie)
            movie.start()
        else:
            print(f"Warning: GIF file not found: {gif_path}")
            self.gif_label.setText("GIF Animation Placeholder")
            self.gif_label.setStyleSheet("color: white; background-color: gray;")
        
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Icon Label
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        initial_icon = safe_load_icon(GraphicsDirectoryPath('Mic_on.png'))
        self.icon_label.setPixmap(initial_icon.scaled(150, 150, Qt.KeepAspectRatio))
        
        self.toggled = True
        self.icon_label.mousePressEvent = self.toggle_icon
        
        # Text Label
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")
        
        content_layout.addWidget(self.gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)
        
        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")
        
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(5)

    def load_icon(self, path, width=60, height=60):
        pixmap = safe_load_icon(path, (width, height))
        new_pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio)
        self.icon_label.setPixmap(new_pixmap)
    
    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 60, 60)
            MicButtonClosed()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'), 60, 60)
            MicButtonInitialed()
        self.toggled = not self.toggled

    def update_status(self):
        """Update status text from file"""
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read().strip()
            self.label.setText(messages)
        except FileNotFoundError:
            self.label.setText("Status Unavailable")

class ChatSection(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(10)  # Changed from invalid -100
        
        # Chat text edit
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QTextEdit.NoFrame)
        layout.addWidget(self.chat_text_edit)
        
        # Set up chat display properties
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        
        # Timer for updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_messages)
        self.timer.start(5)

    def load_messages(self):
        """Load and display messages from file"""
        global old_chat_message
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                messages = file.read().strip()
                
            if messages and messages != old_chat_message:
                self.add_message(messages, 'White')
                old_chat_message = messages
                
        except FileNotFoundError:
            pass

    def add_message(self, message, color):
        """Add a new message to the chat display"""
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.label = QLabel("")
        self.chat_section = ChatSection()
        layout.addWidget(self.label)
        layout.addWidget(self.chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setup_ui()

    def setup_ui(self):
        # Create and set up stacked widget
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.addWidget(InitialScreen())
        self.stacked_widget.addWidget(MessageScreen())
        
        # Set up window properties
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        self.setStyleSheet("background-color: black;")
        
        # Create and set up custom title bar
        self.title_bar = CustomTopBar(self, self.stacked_widget)
        self.setMenuWidget(self.title_bar)
        self.setCentralWidget(self.stacked_widget)

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        
        # Title
        title = QLabel(f" {Assistantname.capitalize()} AI ")
        title.setStyleSheet("color: black; font-size: 18px; background-color: white")
        
        # Navigation buttons
        home_btn = self.create_button("Home.png", "Home", lambda: self.stacked_widget.setCurrentIndex(0))
        chat_btn = self.create_button("Chats.png", "Chat", lambda: self.stacked_widget.setCurrentIndex(1))
        
        # Window control buttons
        min_btn = self.create_button("Minimize2.png", "", self.parent().showMinimized)
        max_btn = self.create_button("Maximize.png", "", self.toggle_maximize)
        close_btn = self.create_button("Close.png", "", self.parent().close)
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addStretch(1)
        layout.addWidget(home_btn)
        layout.addWidget(chat_btn)
        layout.addStretch(1)
        layout.addWidget(min_btn)
        layout.addWidget(max_btn)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        self.setFixedHeight(50)
        self.setStyleSheet("background-color: white")

    def create_button(self, icon_name, text, callback):
        btn = QPushButton()
        icon = QIcon(safe_load_icon(GraphicsDirectoryPath(icon_name)))
        btn.setIcon(icon)
        if text:
            btn.setText(f" {text}")
        btn.setStyleSheet("height: 40px; line-height: 40px; background-color: white; color: black")
        btn.clicked.connect(callback)
        return btn

    def toggle_maximize(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
        else:
            self.parent().showMaximized()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
