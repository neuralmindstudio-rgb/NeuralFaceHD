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
try:
    import splash
    print("splash OK")
except Exception as e:
    print(f"Erro splash: {e}")

try:
    import login
    print("login OK")
except Exception as e:
    print(f"Erro login: {e}")

try:
    import cadastro
    print("cadastro OK")
except Exception as e:
    print(f"Erro cadastro: {e}")

try:
    import interface_ia
    print("interface_ia OK")
except Exception as e:
    print(f"Erro interface_ia: {e}")

try:
    import loja
    print("loja OK")
except Exception as e:
    print(f"Erro loja: {e}")


class NeuralApp(MDApp):
    def build(self):
        # Configuração visual profissional
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Amber"
        
        self.sm = ScreenManager()
        
        try:
            # Splash
            try:
                self.sm.add_widget(splash.TelaSplash(name='splash'))
                print("Tela splash OK")
            except Exception as e:
                print(f"Erro tela splash: {e}")

            # Login
            try:
                self.sm.add_widget(login.TelaLogin(name='login'))
                print("Tela login OK")
            except Exception as e:
                print(f"Erro tela login: {e}")

            # Cadastro
            try:
                self.sm.add_widget(cadastro.TelaCadastro(name='registro'))
                print("Tela cadastro OK")
            except Exception as e:
                print(f"Erro tela cadastro: {e}")

            # 🔥 INTERFACE IA (PONTO CRÍTICO)
            try:
                self.sm.add_widget(interface_ia.TelaPrincipal(name='principal'))
                print("Tela principal OK")
            except Exception as e:
                print(f"Erro interface IA: {e}")

            # Loja
            try:
                self.sm.add_widget(loja.TelaLoja(name='loja'))
                print("Tela loja OK")
            except Exception as e:
                print(f"Erro tela loja: {e}")

            self.sm.current = 'splash'

        except Exception as e:
            print(f"Erro geral ao carregar telas: {e}")
            
        return self.sm

    def on_start(self):
        if os.name == 'posix':
            self.aplicar_wake_lock()

            try:
                from android.permissions import request_permissions, Permission

                permissoes = [
                    Permission.CAMERA,
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                ]

                # Android mais novo
                if hasattr(Permission, "READ_MEDIA_IMAGES"):
                    permissoes.append(Permission.READ_MEDIA_IMAGES)

                request_permissions(permissoes)
                print("Permissões Android solicitadas")
            except Exception as e:
                print(f"Erro permissões Android: {e}")

    def aplicar_wake_lock(self):
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
        return True

    def on_resume(self):
        pass


if __name__ == "__main__":
    Window.softinput_mode = "pan"
    NeuralApp().run()
