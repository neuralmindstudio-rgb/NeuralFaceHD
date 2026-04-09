import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window

from kivymd.uix.button import MDFillRoundFlatButton, MDRectangleFlatButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.dialog import MDDialog

# 🔥 NOVO FIREBASE VIA REST
try:
    from banco_dados import login as realizar_login, recuperar_senha
    print("Banco REST OK")
except Exception as e:
    print(f"Erro banco_dados: {e}")
    realizar_login = None
    recuperar_senha = None

store = JsonStore('saved_user.json')


class TelaLogin(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

        Window.softinput_mode = "resize"
        Window.bind(on_keyboard=self.voltar_ao_login)

        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)

        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=dp(30),
            spacing=dp(15)
        )
        container.bind(minimum_height=container.setter('height'))

        # espaço superior
        container.add_widget(BoxLayout(size_hint_y=None, height=dp(80)))

        container.add_widget(Label(
            text="NEURAL FACE HD",
            font_size='32sp',
            bold=True,
            color=(0.6, 0.2, 1, 1),
            halign="center",
            size_hint_y=None,
            height=dp(50)
        ))

        container.add_widget(Label(
            text="by Neural Mind Studio",
            font_size='12sp',
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=dp(20),
            halign="center"
        ))

        self.input_email = MDTextField(
            hint_text="E-mail",
            mode="rectangle",
            size_hint_y=None,
            height=dp(56)
        )

        self.input_senha = MDTextField(
            hint_text="Senha",
            mode="rectangle",
            password=True,
            icon_right="eye-off",
            size_hint_y=None,
            height=dp(56)
        )

        self.input_email.bind(on_touch_down=self.forcar_foco)
        self.input_senha.bind(on_touch_down=self.forcar_foco)
        self.input_senha.bind(on_touch_down=self.checar_clique_no_olho)

        container.add_widget(self.input_email)
        container.add_widget(self.input_senha)

        layout_opcoes = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(48)
        )

        box_check = BoxLayout(
            orientation='horizontal',
            size_hint_x=0.5,
            spacing=dp(8)
        )
        box_check.bind(on_touch_down=self.toggle_checkbox_lembrar)

        self.check_lembrar = MDCheckbox(
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            selected_color=(0.6, 0.2, 1, 1)
        )

        box_check.add_widget(self.check_lembrar)
        box_check.add_widget(Label(
            text="Lembrar",
            font_size='13sp',
            color=(0.7, 0.7, 0.7, 1)
        ))

        btn_esqueci = MDFlatButton(
            text="Esqueci a senha?",
            font_size='12sp',
            on_release=self.resetar_senha
        )

        layout_opcoes.add_widget(box_check)
        layout_opcoes.add_widget(btn_esqueci)
        container.add_widget(layout_opcoes)

        container.add_widget(MDFillRoundFlatButton(
            text="ENTRAR NO SISTEMA",
            size_hint_x=1,
            md_bg_color=(0.4, 0, 0.8, 1),
            on_release=self.fazer_login
        ))

        container.add_widget(MDRectangleFlatButton(
            text="CRIAR NOVA CONTA",
            size_hint_x=1,
            text_color=(1, 1, 1, 1),
            line_color=(0.6, 0.2, 1, 1),
            on_release=lambda x: self.ir_para_registro()
        ))

        container.add_widget(MDRectangleFlatButton(
            text="SAIR",
            size_hint_x=1,
            text_color=(1, 0, 0, 1),
            line_color=(0.4, 0.4, 0.4, 1),
            on_release=lambda x: os._exit(0)
        ))

        # espaço inferior
        container.add_widget(BoxLayout(size_hint_y=None, height=dp(120)))

        scroll.add_widget(container)
        self.add_widget(scroll)

        Clock.schedule_once(self.carregar_dados_salvos)

    def on_pre_enter(self, *args):
        Window.softinput_mode = "resize"

    def forcar_foco(self, instance, touch):
        if instance.collide_point(*touch.pos):
            instance.focus = True

    def toggle_checkbox_lembrar(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.check_lembrar.active = not self.check_lembrar.active
            return True
        return False

    def checar_clique_no_olho(self, instance, touch):
        if instance.collide_point(*touch.pos):
            if touch.x > (instance.right - dp(75)):
                instance.password = not instance.password
                instance.icon_right = "eye" if not instance.password else "eye-off"
                return True
        return False

    def voltar_ao_login(self, window, key, *args):
        if key == 27:
            if self.manager.current != 'login':
                self.manager.current = 'login'
                return True
        return False

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def carregar_dados_salvos(self, dt):
        try:
            if store.exists('user_creds'):
                dados = store.get('user_creds')
                self.input_email.text = dados['email']
                self.input_senha.text = dados['password']
                self.check_lembrar.active = True
        except Exception:
            pass

    def ir_para_registro(self):
        self.manager.current = 'registro'

    def fazer_login(self, instance):
        print("Tentando login...")

        if not self.input_email.text or not self.input_senha.text:
            MDDialog(title="Aviso", text="Preencha todos os campos.").open()
            return

        if not realizar_login:
            MDDialog(title="Erro", text="Sistema de login indisponível.").open()
            return

        try:
            sucesso = realizar_login(
                self.input_email.text.strip(),
                self.input_senha.text.strip()
            )

            if sucesso:
                if self.check_lembrar.active:
                    store.put(
                        'user_creds',
                        email=self.input_email.text,
                        password=self.input_senha.text
                    )
                else:
                    if store.exists('user_creds'):
                        store.delete('user_creds')

                self.manager.current = 'principal'
            else:
                MDDialog(title="Erro", text="E-mail ou senha incorretos.").open()

        except Exception as e:
            print(f"Erro login: {e}")
            MDDialog(title="Erro", text="Falha no login.").open()

    def resetar_senha(self, instance):
        if not recuperar_senha:
            MDDialog(title="Erro", text="Recuperação indisponível.").open()
            return

        if self.input_email.text:
            try:
                ok = recuperar_senha(self.input_email.text.strip())
                if ok:
                    MDDialog(title="Sucesso", text="E-mail enviado.").open()
                else:
                    MDDialog(title="Erro", text="Falha ao enviar.").open()
            except Exception as e:
                print(f"Erro resetar senha: {e}")
                MDDialog(title="Erro", text="Falha ao enviar.").open()
        else:
            MDDialog(title="Aviso", text="Digite o e-mail.").open()
