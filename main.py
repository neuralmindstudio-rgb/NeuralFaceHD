import os
# Garante que não haja tentativa de usar o motor de vídeo
os.environ['KIVY_VIDEO'] = '' 

from kivy.core.window import Window
# Fundo preto para evitar o "clarão" branco no início
Window.clearcolor = (0, 0, 0, 1)

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager

# --- IMPORTAÇÃO DOS SEUS MÓDULOS ---
# IMPORTANTE: Dentro desses arquivos (.py), substitua 
# 'import firebase_admin' por 'import pyrebase' se houver!
import login         
import cadastro      
import interface_ia  
import splash        
import loja          

class NeuralApp(MDApp):
    def build(self):
        # Tema Escuro Profissional
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple" # Roxo mais moderno
        self.theme_cls.accent_palette = "Amber"
        
        sm = ScreenManager()
        
        # --- ADICIONANDO AS TELAS ---
        # Certifique-se que TelaSplash não usa VideoPlayer!
        sm.add_widget(splash.TelaSplash(name='splash'))
        sm.add_widget(login.TelaLogin(name='login'))
        sm.add_widget(cadastro.TelaCadastro(name='registro'))
        sm.add_widget(interface_ia.TelaPrincipal(name='principal'))
        sm.add_widget(loja.TelaLoja(name='loja'))
        
        sm.current = 'splash'
        return sm

    def on_start(self):
        """ Manter a tela ligada no Android durante a IA """
        if os.name == 'posix': # Se for Android
            try:
                from android.runnable import run_on_ui_thread
                @run_on_ui_thread
                def keep_screen_on():
                    from jnius import autoclass
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    activity = PythonActivity.mActivity
                    Params = autoclass('android.view.WindowManager$LayoutParams')
                    activity.getWindow().addFlags(Params.FLAG_KEEP_SCREEN_ON)
                keep_screen_on()
            except Exception as e:
                print(f"WakeLock Error: {e}")

    def on_pause(self):
        return True

if __name__ == "__main__":
    # Ajusta teclado para não tampar os campos de email/senha
    Window.softinput_mode = "below_target"
    NeuralApp().run()
