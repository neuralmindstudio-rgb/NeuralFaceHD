import threading
from datetime import datetime

import requests

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

from kivymd.uix.card import MDCard
from kivymd.uix.button import MDFillRoundFlatButton, MDRectangleFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog

import banco_dados as bd

Window.softinput_mode = "resize"


class TelaCadastro(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.rect_fundo = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)

        self.layout_conteudo = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=dp(20),
            spacing=dp(20)
        )
        self.layout_conteudo.bind(minimum_height=self.layout_conteudo.setter('height'))

        self.card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(720),
            padding=dp(20),
            spacing=dp(15),
            md_bg_color=(0.07, 0.07, 0.08, 1),
            radius=[dp(15)],
            elevation=2
        )

        self.card.add_widget(Label(
            text="CRIAR NOVA CONTA",
            font_size='22sp',
            bold=True,
            color=(0.6, 0.2, 1, 1),
            size_hint_y=None,
            height=dp(50)
        ))

        self.nome = MDTextField(
            hint_text="Nome Completo",
            mode="rectangle",
            line_color_focus=(0.6, 0.2, 1, 1)
        )

        self.data_nasc = MDTextField(
            hint_text="Nascimento",
            helper_text="Use barras: DD/MM/AAAA (Apenas +18)",
            helper_text_mode="persistent",
            mode="rectangle",
            line_color_focus=(0.6, 0.2, 1, 1),
            max_text_length=10
        )

        self.email = MDTextField(
            hint_text="Seu Email",
            mode="rectangle",
            line_color_focus=(0.6, 0.2, 1, 1)
        )

        self.senha = MDTextField(
            hint_text="Senha (mín. 6 dígitos)",
            password=True,
            mode="rectangle",
            line_color_focus=(0.6, 0.2, 1, 1),
            icon_right="eye-off"
        )
        self.senha.bind(on_touch_down=self.click_icone_senha)

        self.confirma_senha = MDTextField(
            hint_text="Confirmar Senha",
            password=True,
            mode="rectangle",
            line_color_focus=(0.6, 0.2, 1, 1),
            icon_right="eye-off"
        )
        self.confirma_senha.bind(on_touch_down=self.click_icone_senha)

        self.nome.bind(focus=self.on_focus_campo)
        self.data_nasc.bind(focus=self.on_focus_campo)
        self.email.bind(focus=self.on_focus_campo)
        self.senha.bind(focus=self.on_focus_campo)
        self.confirma_senha.bind(focus=self.on_focus_campo)

        self.card.add_widget(self.nome)
        self.card.add_widget(self.data_nasc)
        self.card.add_widget(self.email)
        self.card.add_widget(self.senha)
        self.card.add_widget(self.confirma_senha)

        self.btn_registrar = MDFillRoundFlatButton(
            text="FINALIZAR E GANHAR 5 CRÉDITOS",
            md_bg_color=(0.15, 0.6, 0.15, 1),
            size_hint_x=1,
            height=dp(50)
        )
        self.btn_registrar.bind(on_release=self.iniciar_thread_cadastro)

        self.btn_voltar = MDRectangleFlatButton(
            text="VOLTAR",
            text_color=(1, 1, 1, 1),
            line_color=(0.5, 0.5, 0.5, 1),
            size_hint_x=1
        )
        self.btn_voltar.bind(on_release=self.ir_para_login)

        self.card.add_widget(self.btn_registrar)
        self.card.add_widget(self.btn_voltar)

        self.layout_conteudo.add_widget(self.card)
        self.layout_conteudo.add_widget(BoxLayout(size_hint_y=None, height=dp(450)))

        self.scroll.add_widget(self.layout_conteudo)
        self.add_widget(self.scroll)

    def on_pre_enter(self, *args):
        Window.softinput_mode = "resize"

    def update_rect(self, instance, value):
        self.rect_fundo.pos = instance.pos
        self.rect_fundo.size = instance.size

    def click_icone_senha(self, instance, touch):
        if instance.collide_point(*touch.pos) and touch.pos[0] > instance.right - dp(75):
            instance.password = not instance.password
            instance.icon_right = "eye" if not instance.password else "eye-off"
            return True
        return False

    def on_focus_campo(self, instance, value):
        if value:
            Clock.schedule_once(lambda dt: self.manter_foco(instance), 0.10)
            Clock.schedule_once(lambda dt: self.manter_foco(instance), 0.30)
            Clock.schedule_once(lambda dt: self.rolar_para_campo(instance), 0.20)
            Clock.schedule_once(lambda dt: self.rolar_para_campo(instance), 0.45)

    def manter_foco(self, instance):
        try:
            instance.focus = True
        except Exception:
            pass

    def rolar_para_campo(self, campo):
        try:
            self.scroll.scroll_to(campo, padding=dp(120), animate=False)
            Clock.schedule_once(
                lambda dt: self.scroll.scroll_to(campo, padding=dp(160), animate=False),
                0.15
            )
        except Exception as e:
            print(f"Erro ao rolar campo: {e}")

    def ir_para_login(self, *args):
        self.manager.current = 'login'

    def iniciar_thread_cadastro(self, instance):
        if not self.nome.text.strip() or not self.email.text.strip() or not self.senha.text.strip():
            MDDialog(title="Aviso", text="Preencha todos os campos.").open()
            return

        if self.senha.text != self.confirma_senha.text:
            MDDialog(title="Erro", text="As senhas não conferem.").open()
            return

        if len(self.senha.text.strip()) < 6:
            MDDialog(title="Erro", text="A senha deve ter pelo menos 6 dígitos.").open()
            return

        data_str = self.data_nasc.text.strip()
        try:
            nasc = datetime.strptime(data_str, "%d/%m/%Y")
            idade = (datetime.now() - nasc).days // 365
            if idade < 18:
                MDDialog(title="Acesso Restrito", text="Você precisa ter +18 anos.").open()
                return
        except Exception:
            MDDialog(title="Data Inválida", text="Use o formato DD/MM/AAAA").open()
            return

        self.btn_registrar.text = "PROCESSANDO..."
        self.btn_registrar.disabled = True
        threading.Thread(target=self.processar_firebase, daemon=True).start()

    def processar_firebase(self):
        e_mail = self.email.text.strip().lower()
        pass_w = self.senha.text.strip()
        nome = self.nome.text.strip()
        data_nascimento = self.data_nasc.text.strip()

        try:
            sucesso = bd.cadastro(e_mail, pass_w, nome)

            if sucesso:
                # Complementa os dados do usuário recém-criado sem alterar o restante do banco
                try:
                    if bd.local_id:
                        url = f"{bd.DATABASE_URL}/usuarios/{bd.local_id}.json"
                        if getattr(bd, "id_token", None):
                            url = f"{url}?auth={bd.id_token}"

                        payload = {
                            "nome": nome,
                            "email": e_mail,
                            "creditos": 5,
                            "data_nascimento": data_nascimento,
                            "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "aceitou_termos": False
                        }

                        res = requests.patch(url, json=payload, timeout=15)
                        print("COMPLEMENTO CADASTRO:", res.text)
                except Exception as e:
                    print(f"Erro ao complementar cadastro: {e}")

                Clock.schedule_once(lambda dt: self.sucesso_cadastro(), 0.1)
            else:
                erro_real = getattr(bd, "ultimo_erro", "Erro no cadastro.")
                Clock.schedule_once(lambda dt: self.falha_cadastro(erro_real), 0.1)

        except Exception as e:
            print(f"Erro cadastro: {e}")
            Clock.schedule_once(lambda dt: self.falha_cadastro(str(e)), 0.1)

    def sucesso_cadastro(self):
        self.btn_registrar.text = "FINALIZAR E GANHAR 5 CRÉDITOS"
        self.btn_registrar.disabled = False

        dialog = MDDialog(
            title="Sucesso!",
            text="Conta criada! Faça seu login.",
            buttons=[
                MDRectangleFlatButton(
                    text="OK",
                    on_release=lambda x: self.fechar_dialogo_e_ir_login(dialog)
                )
            ]
        )
        dialog.open()

    def fechar_dialogo_e_ir_login(self, dialog):
        dialog.dismiss()
        self.manager.current = 'login'

    def falha_cadastro(self, erro):
        self.btn_registrar.text = "FINALIZAR E GANHAR 5 CRÉDITOS"
        self.btn_registrar.disabled = False
        MDDialog(title="Erro", text=erro).open()
