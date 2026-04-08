import os
# REMOVIDO: os.environ['KIVY_VIDEO'] = 'ffpyplayer' (Não usamos mais vídeo)

from kivy.core.window import Window
# Garante o fundo preto antes de tudo carregar
Window.clearcolor = (0, 0, 0, 1)

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock

# --- IMPORTAÇÃO DOS SEUS ARQUIVOS SEPARADOS ---
import login         
import cadastro      
import interface_ia  
import splash        
import loja          

class NeuralApp(MDApp):
    def build(self):
        # Configuração do tema visual
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Purple"
        
        sm = ScreenManager()
        
        # --- ADICIONANDO AS TELAS ---
        
        # 1. Splash Screen (Verifique se dentro de splash.py não há vídeo!)
        sm.add_widget(splash.TelaSplash(name='splash'))
        
        # 2. Tela de Login
        sm.add_widget(login.TelaLogin(name='login'))
        
        # 3. Tela de Cadastro
        sm.add_widget(cadastro.TelaCadastro(name='registro'))
        
        # 4. Interface Principal (IA)
        sm.add_widget(interface_ia.TelaPrincipal(name='principal'))
        
        # 5. Loja de Créditos
        sm.add_widget(loja.TelaLoja(name='loja'))
        
        # Inicia pela Splash
        sm.current = 'splash'
        return sm

    def on_start(self):
        """
        Força o Android a manter a tela ligada (Wake Lock).
        """
        try:
            from android.runnable import run_on_ui_thread
            @run_on_ui_thread
            def keep_screen_on():
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                WindowManager = autoclass('android.view.WindowManager$LayoutParams')
                activity.getWindow().addFlags(WindowManager.FLAG_KEEP_SCREEN_ON)
            keep_screen_on()
        except Exception as e:
            print(f"Aviso: WakeLock não aplicado: {e}")

    def on_pause(self):
        return True

    def on_resume(self):
        pass

if __name__ == "__main__":
    # Garante que o teclado não cubra os campos no Android
    Window.softinput_mode = "below_target"
    NeuralApp().run()
