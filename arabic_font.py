import os
import sys

def get_font_path():
    if getattr(sys, 'frozen', False):
        # Si l'application est "gelée" (compilée)
        return os.path.join(sys._MEIPASS, 'arabic_font.ttf')
    else:
        # Si l'application est en cours d'exécution normalement
        return os.path.join(os.path.dirname(__file__), 'arabic_font.ttf')