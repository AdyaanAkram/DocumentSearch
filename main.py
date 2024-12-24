from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel,
                           QCheckBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor
import sys
import os
from datetime import datetime
from styles import COLORS, STYLES

try:
    import PyPDF2
    import docx
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

class SearchThread(QThread):
    result_found = pyqtSignal(str)
    status_update = pyqtSignal(str)
    
    def __init__(self, search_term, search_contents):
        super().__init__()
        self.search_term = search_term.lower()
        self.search_contents = search_contents
        self.running = True
    
    def search_pdf(self, filepath):
        try:
            with open(filepath, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    if not self.running:
                        return False
                    text += page.extract_text().lower()
                return self.search_term in text
        except:
            return False

    def search_word(self, filepath):
        try:
            doc = docx.Document(filepath)
            text = ""
            for paragraph in doc.paragraphs:
                if not self.running:
                    return False
                text += paragraph.text.lower()
            return self.search_term in text
        except:
            return False
    
    def run(self):
        found_count = 0
        search_paths = [
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads")
        ]
        
        for search_path in search_paths:
            if not self.running:
                break
                
            try:
                for root, _, files in os.walk(search_path):
                    for file in files:
                        if not self.running:
                            break
                            
                        try:
                            full_path = os.path.join(root, file)
                            found_in_name = self.search_term in file.lower()
                            found_in_content = False
                            file_type = "Unknown"
                            
                            # Search file contents if enabled
                            if self.search_contents and not found_in_name:
                                ext = os.path.splitext(file)[1].lower()
                                
                                # PDF Files
                                if ext == '.pdf':
                                    found_in_content = self.search_pdf(full_path)
                                    file_type = "PDF"
                                
                                # Word Documents
                                elif ext in ['.docx', '.doc']:
                                    found_in_content = self.search_word(full_path)
                                    file_type = "Word Document"
                                
                                # Text Files
                                elif ext in ['.txt', '.py', '.java', '.html', '.csv', '.md', '.json', '.xml', '.log']:
                                    try:
                                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                                            content = f.read(1024*1024)  # Read first 1MB only
                                            if self.search_term in content.lower():
                                                found_in_content = True
                                                file_type = "Text File"
                                    except:
                                        pass
                            
                            if found_in_name or found_in_content:
                                stats = os.stat(full_path)
                                modified = datetime.fromtimestamp(stats.st_mtime)
                                size = self.format_size(stats.st_size)
                                
                                result = f"File: {file}\n"
                                result += f"Type: {file_type}\n"
                                result += f"Location: {root}\n"
                                result += f"Modified: {modified}\n"
                                result += f"Size: {size}\n"
                                result += f"Found in: {'File Name' if found_in_name else 'File Content'}\n"
                                result += "-" * 50 + "\n\n"
                                
                                self.result_found.emit(result)
                                found_count += 1
                                
                                if found_count % 10 == 0:
                                    self.status_update.emit(f"Found {found_count} matches...")
                                    
                        except Exception as e:
                            continue
                            
            except Exception as e:
                self.status_update.emit(f"Error searching {search_path}: {str(e)}")
        
        self.status_update.emit(f"Search complete. Found {found_count} matches.")
    
    def stop(self):
        self.running = False
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

class SearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced File Search")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['background']};
            }}
            QWidget {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
            }}
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("File Search")
        font = QFont()
        font.setFamily(STYLES['title_font']['family'])
        font.setPointSize(STYLES['title_font']['size'])
        font.setWeight(STYLES['title_font']['weight'])
        title.setFont(font)
        title.setStyleSheet(f"color: {COLORS['primary']};")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Search bar area
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 20, 0, 20)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search term...")
        self.search_input.setMinimumHeight(40)
        font = QFont()
        font.setFamily(STYLES['entry_font']['family'])
        font.setPointSize(STYLES['entry_font']['size'])
        self.search_input.setFont(font)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {COLORS['gray']};
                border-radius: 4px;
                padding: 0 10px;
                background: {COLORS['input_bg']};
                color: {COLORS['text']};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        search_layout.addWidget(self.search_input)
        
        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.setMinimumHeight(40)
        font = QFont()
        font.setFamily(STYLES['button_font']['family'])
        font.setPointSize(STYLES['button_font']['size'])
        self.search_button.setFont(font)
        self.search_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['white']};
                border: none;
                border-radius: 4px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['hover']};
            }}
        """)
        self.search_button.clicked.connect(self.start_search)
        search_layout.addWidget(self.search_button)
        
        # Add search area to main layout
        layout.addLayout(search_layout)
        
        # Search options
        options_layout = QHBoxLayout()
        self.content_search = QCheckBox("Search file contents (slower)")
        font = QFont()
        font.setFamily(STYLES['text_font']['family'])
        font.setPointSize(STYLES['text_font']['size'])
        self.content_search.setFont(font)
        self.content_search.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['text']};
            }}
            QCheckBox::indicator {{
                width: 13px;
                height: 13px;
                border: 1px solid {COLORS['gray']};
                border-radius: 2px;
                background: {COLORS['input_bg']};
            }}
            QCheckBox::indicator:checked {{
                background: {COLORS['primary']};
            }}
        """)
        options_layout.addWidget(self.content_search)
        layout.addLayout(options_layout)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {COLORS['gray']};
                border-radius: 4px;
                background: {COLORS['white']};
            }}
            QProgressBar::chunk {{
                background: {COLORS['primary']};
            }}
        """)
        self.progress.hide()
        layout.addWidget(self.progress)
        
        # Results area
        self.results_area = QTextEdit()
        font = QFont()
        font.setFamily(STYLES['text_font']['family'])
        font.setPointSize(STYLES['text_font']['size'])
        self.results_area.setFont(font)
        self.results_area.setReadOnly(True)
        self.results_area.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {COLORS['gray']};
                border-radius: 4px;
                background: {COLORS['background']};
                color: {COLORS['text']};
                padding: 10px;
            }}
            QTextEdit:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """)
        layout.addWidget(self.results_area)
        
        # Status bar
        self.status = QLabel("Ready to search")
        font = QFont()
        font.setFamily(STYLES['text_font']['family'])
        font.setPointSize(STYLES['text_font']['size'])
        self.status.setFont(font)
        self.status.setStyleSheet(f"color: {COLORS['gray']};")
        layout.addWidget(self.status)
        
        self.search_thread = None
        self.show()
    
    def start_search(self):
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.stop()
            self.search_button.setText("Search")
            self.progress.hide()
            self.status.setText("Search stopped")
            return
        
        search_term = self.search_input.text()
        if not search_term:
            self.results_area.setText("Please enter a search term")
            return
        
        self.results_area.clear()
        self.search_button.setText("Stop")
        self.progress.show()
        self.progress.setRange(0, 0)  # Indeterminate progress
        
        self.search_thread = SearchThread(
            search_term,
            self.content_search.isChecked()
        )
        self.search_thread.result_found.connect(self.add_result)
        self.search_thread.status_update.connect(self.update_status)
        self.search_thread.finished.connect(self.search_finished)
        self.search_thread.start()
    
    def add_result(self, result):
        self.results_area.append(result)
    
    def update_status(self, message):
        self.status.setText(message)
    
    def search_finished(self):
        self.search_button.setText("Search")
        self.progress.hide()

def main():
    app = QApplication(sys.argv)
    window = SearchApp()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()