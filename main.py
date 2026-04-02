import os
# Configuração para evitar flashes brancos e problemas de GPU
os.environ['KIVY_VIDEO'] = 'ffpyplayer'

from kivy.core.window import Window
# Garante o fundo preto antes de tudo carregar
Window.clearcolor = (0, 0, 0, 1)

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock

# --- IMPORTAÇÃO DOS SEUS ARQUIVOS SEPARADOS ---
import login         # Agora busca no seu login.py centralizado
import cadastro      # Agora busca no seu cadastro.py (o backup bom)
import interface_ia  # Sua tela principal
import splash        # Sua tela de abertura
import loja          # Sua loja Neon

class NeuralApp(MDApp):
    def build(self):
        # Configuração do tema visual
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Purple"
        
        sm = ScreenManager()
        
        # --- ADICIONANDO AS TELAS ---
        
        # 1. Splash Screen
        sm.add_widget(splash.TelaSplash(name='splash'))
        
        # 2. Tela de Login (Puxando do arquivo login.py)
        sm.add_widget(login.TelaLogin(name='login'))
        
        # 3. Tela de Cadastro (Puxando do arquivo cadastro.py)
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
        Esta função roda assim que o App inicia. 
        Ela tenta forçar o Android a manter a tela ligada (Wake Lock).
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
            print(f"Aviso: WakeLock não aplicado (comum fora do Android): {e}")

    def on_pause(self):
        """
        Quando o usuário minimiza o app ou a tela apaga.
        Retornar True impede que o Android mate o processo imediatamente.
        """
        return True

    def on_resume(self):
        """
        Quando o usuário volta para o aplicativo.
        """
        pass

if __name__ == "__main__":
    # Garante que o teclado não cubra os campos no Android
    Window.softinput_mode = "below_target"
    NeuralApp().run()