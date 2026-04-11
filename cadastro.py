import os
import threading
from datetime import datetime

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window

from kivymd.uix.card import MDCard
from kivymd.uix.button import MDFillRoundFlatButton, MDRectangleFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog

# 🔥 NOVO FIREBASE VIA REST
try:
    from banco_dados import cadastro
    print("Cadastro REST OK")
except Exception as e:
    print(f"Erro banco_dados cadastro: {e}")
    cadastro = None

store = JsonStore('saved_user.json')


class TelaCadastro(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        # 1. Mudança para 'below_target': evita que a tela tente se redimensionar 
        # e cause o loop infinito/piscadeira.
        Window.softinput_mode = "below_target"

        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.rect_fundo = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)

        self.layout_conteudo = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(20), dp(20), dp(20), dp(40)],
            spacing=dp(15)
        )
        self.layout_conteudo.bind(minimum_height=self.layout_conteudo.setter('height'))

        self.card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(680),
            padding=dp(20),
            spacing=dp(10),
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

        self.nome = MDTextField(hint_text="Nome Completo", mode="rectangle")
        self.data_nasc = MDTextField(
            hint_text="Nascimento",
            helper_text="DD/MM/AAAA (Apenas +18)",
            helper_text_mode="persistent",
            mode="rectangle",
            max_text_length=10
        )

        self.email = MDTextField(hint_text="Seu Email", mode="rectangle")
        self.senha = MDTextField(
            hint_text="Senha (mín. 6 dígitos)",
            password=True,
            mode="rectangle",
            icon_right="eye-off"
        )
        self.senha.bind(on_touch_down=self.click_icone_senha)

        self.confirma_senha = MDTextField(
            hint_text="Confirmar Senha",
            password=True,
            mode="rectangle",
            icon_right="eye-off"
        )
        self.confirma_senha.bind(on_touch_down=self.click_icone_senha)

        # 2. Mantemos apenas o bind de foco simplificado para evitar loops
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
        
        # 3. Espaçador fixo no final para permitir que o ScrollView suba os campos
        self.espacador_final = BoxLayout(size_hint_y=None, height=dp(400))
        self.layout_conteudo.add_widget(self.espacador_final)

        self.scroll.add_widget(self.layout_conteudo)
        self.add_widget(self.scroll)

    def on_pre_enter(self, *args):
        Window.softinput_mode = "below_target"

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
            # 4. Rola apenas uma vez com delay para o teclado se estabilizar
            Clock.schedule_once(lambda dt: self.rolar_para_campo(instance), 0.2)

    def rolar_para_campo(self, campo):
        try:
            # Padding ajustado para deixar o campo bem visível acima do teclado
            self.scroll.scroll_to(campo, padding=dp(200), animate=True)
        except Exception as e:
            print(f"Erro ao rolar campo: {e}")

    def ir_para_login(self, *args):
        self.manager.current = 'login'

    def iniciar_thread_cadastro(self, instance):
        if not cadastro:
            MDDialog(title="Erro", text="Sistema indisponível.").open()
            return

        if self.senha.text != self.confirma_senha.text:
            MDDialog(title="Erro", text="As senhas não conferem.").open()
            return
        
        if len(self.senha.text) < 6:
            MDDialog(title="Erro", text="A senha deve ter 6 dígitos.").open()
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
        # Strip e Lower para evitar erros de login depois
        e_mail = self.email.text.strip().lower()
        pass_w = self.senha.text.strip()
        nome = self.nome.text.strip()

        try:
            sucesso = cadastro(e_mail, pass_w, nome)
            if sucesso:
                Clock.schedule_once(lambda dt: self.sucesso_cadastro(), 0.1)
            else:
                Clock.schedule_once(lambda dt: self.falha_cadastro("E-mail já cadastrado ou erro na rede."), 0.1)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.falha_cadastro(f"Erro: {e}"), 0.1)

    def sucesso_cadastro(self):
        self.btn_registrar.text = "FINALIZAR E GANHAR 5 CRÉDITOS"
        self.btn_registrar.disabled = False
        MDDialog(title="Sucesso!", text="Conta criada! Faça o login.").open()
        self.manager.current = 'login'

    def falha_cadastro(self, erro):
        self.btn_registrar.text = "FINALIZAR E GANHAR 5 CRÉDITOS"
        self.btn_registrar.disabled = False
        MDDialog(title="Erro", text=erro).open()
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
        
        # Espaçador de segurança maior
        self.espacador_final = BoxLayout(size_hint_y=None, height=dp(500))
        self.layout_conteudo.add_widget(self.espacador_final)

        self.scroll.add_widget(self.layout_conteudo)
        self.add_widget(self.scroll)
        
        # Monitor de teclado para forçar o scroll
        Window.bind(on_keyboard_height=self.solucionar_teclado)

    def garantir_foco(self, instance, touch):
        if instance.collide_point(*touch.pos):
            instance.focus = True
            return True
        return False

    def solucionar_teclado(self, window, height):
        # Força o ScrollView a entender que o teclado ocupou espaço
        if height > 0:
            self.espacador_final.height = height + dp(150)
        else:
            self.espacador_final.height = dp(500)

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
            # Rola com um tempo maior para garantir que o teclado já subiu
            Clock.schedule_once(lambda dt: self.rolar_para_campo(instance), 0.3)

    def rolar_para_campo(self, campo):
        try:
            # Centraliza o campo na tela visível (0.5)
            self.scroll.scroll_to(campo, padding=dp(250), animate=True)
        except Exception as e:
            print(f"Erro ao rolar campo: {e}")

    def ir_para_login(self, *args):
        self.manager.current = 'login'

    def iniciar_thread_cadastro(self, instance):
        if not cadastro:
            MDDialog(title="Erro", text="Sistema offline.").open()
            return
        
        # Validação básica
        if len(self.senha.text) < 6:
            MDDialog(title="Erro", text="Senha deve ter 6+ dígitos.").open()
            return

        self.btn_registrar.text = "PROCESSANDO..."
        self.btn_registrar.disabled = True
        threading.Thread(target=self.processar_firebase, daemon=True).start()

    def processar_firebase(self):
        # Limpeza de strings para evitar erros de login depois
        e_mail = self.email.text.strip().lower()
        pass_w = self.senha.text.strip()
        nome = self.nome.text.strip()

        try:
            sucesso = cadastro(e_mail, pass_w, nome)
            if sucesso:
                Clock.schedule_once(lambda dt: self.sucesso_cadastro(), 0.1)
            else:
                Clock.schedule_once(lambda dt: self.falha_cadastro("Erro no cadastro."), 0.1)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.falha_cadastro(f"Erro: {e}"), 0.1)

    def sucesso_cadastro(self):
        self.btn_registrar.text = "FINALIZAR E GANHAR 5 CRÉDITOS"
        self.btn_registrar.disabled = False
        MDDialog(title="Sucesso!", text="Conta criada! Tente logar.").open()
        self.manager.current = 'login'

    def falha_cadastro(self, erro):
        self.btn_registrar.text = "FINALIZAR E GANHAR 5 CRÉDITOS"
        self.btn_registrar.disabled = False
        MDDialog(title="Erro", text=erro).open()
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

        layout_conteudo.add_widget(self.card)
        
        # Espaçador dinâmico para o teclado
        self.espacador_fim = BoxLayout(size_hint_y=None, height=dp(400))
        layout_conteudo.add_widget(self.espacador_fim)

        self.scroll.add_widget(layout_conteudo)
        self.add_widget(self.scroll)
        
        # Monitora a altura do teclado globalmente
        Window.bind(on_keyboard_height=self.ajustar_rolagem_teclado)

    def garantir_foco(self, instance, touch):
        if instance.collide_point(*touch.pos):
            instance.focus = True
            return True
        return False

    def ajustar_rolagem_teclado(self, window, height):
        if height > 0:
            self.espacador_fim.height = height + dp(100)
        else:
            self.espacador_fim.height = dp(400)

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
            Clock.schedule_once(lambda dt: self.rolar_para_campo(instance), 0.2)

    def rolar_para_campo(self, campo):
        try:
            self.scroll.scroll_to(campo, padding=dp(250), animate=True)
        except Exception as e:
            print(f"Erro ao rolar campo: {e}")

    def ir_para_login(self, *args):
        self.manager.current = 'login'

    def iniciar_thread_cadastro(self, instance):
        if not cadastro:
            MDDialog(
                title="Erro",
                text="Sistema de cadastro indisponível no momento."
            ).open()
            return

        if self.senha.text != self.confirma_senha.text:
            MDDialog(title="Erro", text="As senhas não conferem.").open()
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
        e_mail = self.email.text.strip()
        pass_w = self.senha.text.strip()
        nome = self.nome.text.strip()

        try:
            sucesso = cadastro(e_mail, pass_w, nome)

            if sucesso:
                Clock.schedule_once(lambda dt: self.sucesso_cadastro(), 0.1)
            else:
                Clock.schedule_once(
                    lambda dt: self.falha_cadastro("E-mail já cadastrado ou erro na conexão."),
                    0.1
                )

        except Exception as e:
            print(f"Erro cadastro: {e}")
            Clock.schedule_once(lambda dt: self.falha_cadastro("Erro na conexão."), 0.1)

    def sucesso_cadastro(self):
        self.btn_registrar.text = "FINALIZAR E GANHAR 5 CRÉDITOS"
        self.btn_registrar.disabled = False
        self.manager.current = 'login'
        MDDialog(title="Sucesso!", text="Conta criada! Faça seu login.").open()

    def falha_cadastro(self, erro):
        self.btn_registrar.text = "FINALIZAR E GANHAR 5 CRÉDITOS"
        self.btn_registrar.disabled = False
        MDDialog(title="Erro", text=erro).open()
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

        layout_conteudo.add_widget(self.card)
        # ALTERAÇÃO 2: Aumentei o espaçador para garantir que até o último campo possa ser rolado para cima do teclado
        layout_conteudo.add_widget(BoxLayout(size_hint_y=None, height=dp(450)))

        self.scroll.add_widget(layout_conteudo)
        self.add_widget(self.scroll)
        self.dialogo = None

    def on_pre_enter(self, *args):
        # Garante que a configuração do teclado seja aplicada ao entrar na tela
        Window.softinput_mode = "below_target"

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
            # ALTERAÇÃO 3: Simplificação da rolagem automática para o campo focado
            Clock.schedule_once(lambda dt: self.rolar_para_campo(instance), 0.2)

    def rolar_para_campo(self, campo):
        try:
            # Rola suavemente até o campo, deixando um respiro (padding) para o teclado
            self.scroll.scroll_to(campo, padding=dp(220), animate=True)
        except Exception as e:
            print(f"Erro ao rolar campo: {e}")

    def ir_para_login(self, *args):
        self.manager.current = 'login'

    def iniciar_thread_cadastro(self, instance):
        if not cadastro:
            MDDialog(
                title="Erro",
                text="Sistema de cadastro indisponível no momento."
            ).open()
            return

        if self.senha.text != self.confirma_senha.text:
            MDDialog(title="Erro", text="As senhas não conferem.").open()
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
        e_mail = self.email.text.strip()
        pass_w = self.senha.text.strip()
        nome = self.nome.text.strip()

        try:
            # ALTERAÇÃO 4: Agora integrado com o banco_dados.py corrigido
            sucesso = cadastro(e_mail, pass_w, nome)

            if sucesso:
                Clock.schedule_once(lambda dt: self.sucesso_cadastro(), 0.1)
            else:
                Clock.schedule_once(
                    lambda dt: self.falha_cadastro("Verifique os dados ou se o e-mail já existe."),
                    0.1
                )

        except Exception as e:
            print(f"Erro cadastro: {e}")
            Clock.schedule_once(lambda dt: self.falha_cadastro("Erro na conexão."), 0.1)

    def sucesso_cadastro(self):
        self.btn_registrar.text = "FINALIZAR E GANHAR 5 CRÉDITOS"
        self.btn_registrar.disabled = False
        self.manager.current = 'login'
        MDDialog(title="Sucesso!", text="Conta criada! Faça seu login.").open()

    def falha_cadastro(self, erro):
        self.btn_registrar.text = "FINALIZAR E GANHAR 5 CRÉDITOS"
        self.btn_registrar.disabled = False
        MDDialog(title="Erro", text=erro).open()
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

        layout_conteudo.add_widget(self.card)
        layout_conteudo.add_widget(BoxLayout(size_hint_y=None, height=dp(350)))

        self.scroll.add_widget(layout_conteudo)
        self.add_widget(self.scroll)
        self.dialogo = None

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
        if not cadastro:
            MDDialog(
                title="Erro",
                text="Sistema de cadastro indisponível no momento."
            ).open()
            return

        if self.senha.text != self.confirma_senha.text:
            MDDialog(title="Erro", text="As senhas não conferem.").open()
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
        e_mail = self.email.text.strip()
        pass_w = self.senha.text.strip()
        nome = self.nome.text.strip()

        try:
            sucesso = cadastro(e_mail, pass_w, nome)

            if sucesso:
                Clock.schedule_once(lambda dt: self.sucesso_cadastro(), 0.1)
            else:
                Clock.schedule_once(
                    lambda dt: self.falha_cadastro("E-mail já cadastrado ou erro na conexão."),
                    0.1
                )

        except Exception as e:
            print(f"Erro cadastro: {e}")
            Clock.schedule_once(lambda dt: self.falha_cadastro("Erro na conexão."), 0.1)

    def sucesso_cadastro(self):
        self.btn_registrar.text = "FINALIZAR E GANHAR 5 CRÉDITOS"
        self.btn_registrar.disabled = False
        self.manager.current = 'login'
        MDDialog(title="Sucesso!", text="Conta criada! Faça seu login.").open()

    def falha_cadastro(self, erro):
        self.btn_registrar.text = "FINALIZAR E GANHAR 5 CRÉDITOS"
        self.btn_registrar.disabled = False
        MDDialog(title="Erro", text=erro).open()
