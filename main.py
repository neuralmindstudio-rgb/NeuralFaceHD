import os
# Bloqueia qualquer tentativa de usar ffpyplayer ou vídeo que derrube o app
os.environ['KIVY_VIDEO'] = ''

from kivy.config import Config
# Desativa o multitouch (aqueles círculos vermelhos) para evitar bugs na interface
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivy.core.window import Window
# Fundo preto imediato para evitar o clarão branco no Splash
Window.clearcolor = (0, 0, 0, 1)

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock

# --- IMPORTAÇÃO DOS MÓDULOS ---
# Se algum desses der erro de 'ModuleNotFound' no futuro, saberemos exatamente qual
import splash
import login
import cadastro
import interface_ia
import loja

class NeuralApp(MDApp):
    def build(self):
        # Configuração visual profissional
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Amber"
        
        # Gerenciador de telas
        self.sm = ScreenManager()
        
        try:
            # Adicionando as telas na ordem de uso
            self.sm.add_widget(splash.TelaSplash(name='splash'))
            self.sm.add_widget(login.TelaLogin(name='login'))
            self.sm.add_widget(cadastro.TelaCadastro(name='registro'))
            self.sm.add_widget(interface_ia.TelaPrincipal(name='principal'))
            self.sm.add_widget(loja.TelaLoja(name='loja'))
            
            self.sm.current = 'splash'
        except Exception as e:
            print(f"Erro ao carregar telas: {e}")
            
        return self.sm

    def on_start(self):
        """ Configurações específicas do Android ao iniciar """
        if os.name == 'posix': # Identifica se é Android/Linux
            self.aplicar_wake_lock()

    def aplicar_wake_lock(self):
        """ Força a tela a ficar ligada durante o uso da IA """
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
            print(f"WakeLock não disponível: {e}")

    def on_pause(self):
        # Permite que o app fique em segundo plano sem ser morto imediatamente
        return True

    def on_resume(self):
        pass

if __name__ == "__main__":
    # Garante que o teclado não suba em cima dos campos de texto
    Window.softinput_mode = "below_target"
    NeuralApp().run()
