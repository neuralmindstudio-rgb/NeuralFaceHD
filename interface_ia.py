import os
import requests
import shutil
import time
import threading
import socket
import gc  # 🔥 Essencial para evitar o erro da foto 30
from datetime import datetime

from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget 
from kivy.cache import Cache
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.app import App
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window

from kivymd.uix.button import (
    MDFillRoundFlatButton,
    MDRectangleFlatButton,
    MDRoundFlatIconButton,
    MDIconButton,
)
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu

# Plyer como fallback fora do Android
try:
    from plyer import share, filechooser
except ImportError:
    share = None
    filechooser = None

# Android nativo
try:
    from jnius import autoclass, cast
    ANDROID_OK = True
except Exception:
    autoclass = None
    cast = None
    ANDROID_OK = False

try:
    from android import activity
except Exception:
    activity = None

try:
    from android.runnable import run_on_ui_thread
except Exception:
    run_on_ui_thread = None

# 🔥 BANCO VIA REST
try:
    import banco_dados as bd
    print("Banco REST interface_ia OK")
except Exception as e:
    print(f"Erro banco_dados interface_ia: {e}")
    bd = None

tutorial_store = JsonStore('tutorial_status.json')


class TelaPrincipal(Screen):
    PICK_IMAGE_REQUEST = 1001
    CREATE_FILE_REQUEST = 1002

    def __init__(self, **kw):
        super().__init__(**kw)
        Window.clearcolor = (0, 0, 0, 1)

        self.session = requests.Session()
        self.cor_roxo_destaque = get_color_from_hex("#1A1423")
        self.cor_verde_status = (0, 1, 0, 1)

        self.ip_servidor = "191.253.31.209"
        self.url_swap = f"http://{self.ip_servidor}:8080/swap"

        self.face_index = 0
        self.creditos_atuais = 0
        self.path_base = ""
        self.path_rosto = ""
        self.imagem_final_pronta = False
        self.servidor_online = False
        self.arquivo_gerado_agora = ""
        self.ultima_combinacao = ""
        self.dialogo_termos = None
        self.dialogo_tutorial = None
        self.dialogo_save_choice = None
        self.dialogo_sem_creditos = None
        self.file_manager_aberto = False
        self.th = None
        self.processando_agora = False
        self.bloqueio_idx = False
        self.tipo_atual = "base"

        self.file_manager = MDFileManager(
            exit_manager=self.fechar_seletor,
            select_path=self.processar_selecao_kivymd,
            preview=True,
        )

        if ANDROID_OK and activity:
            try:
                activity.bind(on_activity_result=self.on_activity_result)
            except Exception as e:
                print(f"Erro bind activity result: {e}")

        layout_geral = FloatLayout()

        # --- BARRA SUPERIOR ---
        self.barra_t = BoxLayout(
            size_hint=(1, None),
            height=dp(80),
            spacing=dp(10),
            padding=[dp(10), dp(35), dp(10), dp(10)],
            pos_hint={'top': 1}
        )

        self.btn_sair = MDRectangleFlatButton(text="LOGOUT", theme_text_color="Custom", text_color=(1, 0, 0, 1), line_color=(1, 0, 0, 1))
        self.btn_sair.bind(on_release=self.fazer_logout)

        self.btn_salvar = MDRoundFlatIconButton(text="SALVAR", icon="download", disabled=True)
        self.btn_salvar.bind(on_release=self.abrir_menu_salvamento)

        self.lbl_rede = Label(text="OFFLINE", color=(1, 0, 0, 1), font_size='9sp', bold=True)
        self.btn_mais = MDIconButton(icon="dots-vertical", theme_text_color="Custom", text_color=(1, 1, 1, 1))
        self.btn_mais.bind(on_release=self.abrir_menu)

        self.barra_t.add_widget(self.btn_sair)
        self.barra_t.add_widget(self.btn_salvar)
        self.barra_t.add_widget(self.lbl_rede)
        self.barra_t.add_widget(self.btn_mais)

        # --- ÁREA CENTRAL (AMPLIADA E SUBIDA) ---
        self.meio = MDBoxLayout(
            orientation='vertical',
            size_hint=(0.98, 0.68), # Aumentado para ocupar mais espaço vertical
            pos_hint={'center_x': 0.5, 'center_y': 0.58}, # Subido para equilibrar com o topo
            md_bg_color=(0, 0, 0, 0),
            padding=dp(2) # Padding reduzido para a foto preencher melhor o quadro
        )
        with self.meio.canvas.before:
            Color(*self.cor_roxo_destaque)
            self.rect_meio = RoundedRectangle(pos=self.meio.pos, size=self.meio.size, radius=[dp(25)])
        self.meio.bind(pos=self.update_rect_meio, size=self.update_rect_meio)

        self.area_foto = BoxLayout()
        self.img_preview = Image(source='', opacity=0)
        self.area_foto.add_widget(self.img_preview)

        self.barra_p = MDProgressBar(type="indeterminate", size_hint_y=None, height=dp(3), opacity=0, color=self.cor_verde_status, running_duration=0.3)
        self.meio.add_widget(self.area_foto)
        self.meio.add_widget(self.barra_p)

        # --- PAINEL INFERIOR (COMPACTADO PARA DAR ESPAÇO) ---
        self.painel = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(175), # Altura reduzida para priorizar a área da foto
            padding=[dp(10), dp(2), dp(10), dp(5)],
            spacing=dp(5),
            pos_hint={'x': 0, 'y': 0.01}
        )

        self.label_s = Label(text="Neural Face HD", color=(0.5, 0.5, 0.6, 1), font_size='11sp', size_hint_y=None, height=dp(18))

        l1 = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(44))
        self.btn_b = MDRoundFlatIconButton(text="BASE", icon="image-plus", size_hint_x=0.5)
        self.btn_b.bind(on_release=lambda x: self.abrir_seletor_nativo("base"))
        self.btn_r = MDRoundFlatIconButton(text="ROSTO", icon="face-man-profile", size_hint_x=0.5)
        self.btn_r.bind(on_release=lambda x: self.abrir_seletor_nativo("rosto"))
        l1.add_widget(self.btn_b)
        l1.add_widget(self.btn_r)

        self.btn_idx = MDRoundFlatIconButton(text="TROCAR ROSTO (0)", icon="account-switch", size_hint_x=1, height=dp(40))
        self.btn_idx.bind(on_release=self.alternar_rosto)

        l2 = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(50))
        self.btn_limpar = MDRectangleFlatButton(text="LIMPAR", size_hint_x=0.25)
        self.btn_limpar.bind(on_release=self.limpar_tudo)
        self.btn_gerar = MDFillRoundFlatButton(text="GERAR", md_bg_color=(0.5, 0, 0.8, 1), size_hint_x=0.45)
        self.btn_gerar.bind(on_release=self.enviar_ao_pc)
        self.btn_rec = MDRectangleFlatButton(text="+ CRÉDITOS", size_hint_x=0.3, theme_text_color="Custom", text_color=(0, 0.8, 0, 1), line_color=(0, 0.8, 0, 1))
        self.btn_rec.bind(on_release=self.abrir_loja)

        l2.add_widget(self.btn_limpar)
        l2.add_widget(self.btn_gerar)
        l2.add_widget(self.btn_rec)

        self.painel.add_widget(self.label_s)
        self.painel.add_widget(l1)
        self.painel.add_widget(self.btn_idx)
        self.painel.add_widget(l2)
        
        self.espacador_android = Widget(size_hint_y=None, height=0)
        self.painel.add_widget(self.espacador_android)

        layout_geral.add_widget(self.barra_t)
        layout_geral.add_widget(self.meio)
        layout_geral.add_widget(self.painel)
        self.add_widget(layout_geral)

        Clock.schedule_once(self.ajustar_espaco_sistema, 1)

        menu_items = [{"viewclass": "OneLineListItem", "text": "Termos de Uso", "on_release": lambda x="Termos": self.menu_callback(x)},
                      {"viewclass": "OneLineListItem", "text": "Sobre", "on_release": lambda x="Sobre": self.menu_callback(x)}]
        self.dropdown = MDDropdownMenu(caller=self.btn_mais, items=menu_items, width_mult=4)

    def ajustar_espaco_sistema(self, *args):
        if not ANDROID_OK: return
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            decor_view = PythonActivity.mActivity.getWindow().getDecorView()
            insets = decor_view.getRootWindowInsets()
            if insets:
                bottom_inset = insets.getSystemWindowInsetBottom()
                padding_dp = bottom_inset / Window.density
                if padding_dp > 0:
                    self.espacador_android.height = dp(padding_dp)
                    self.painel.height += dp(padding_dp)
        except: pass

    def mostrar_barras_android(self, *args):
        if not ANDROID_OK: return
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            View = autoclass('android.view.View')
            LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
            currentActivity = PythonActivity.mActivity
            def _mostrar():
                try:
                    window = currentActivity.getWindow()
                    decor = window.getDecorView()
                    window.clearFlags(LayoutParams.FLAG_FULLSCREEN)
                    decor.setSystemUiVisibility(View.SYSTEM_UI_FLAG_VISIBLE)
                    window.setSoftInputMode(LayoutParams.SOFT_INPUT_ADJUST_RESIZE)
                except: pass
            if run_on_ui_thread: run_on_ui_thread(_mostrar)()
            else: _mostrar()
        except: pass

    def salvar_em_uri(self, uri):
        """ 🔥 VERSÃO ANTI-TRAVAMENTO 2.0: Resolve Foto 30 e Nome Inválido """
        try:
            if not self.arquivo_gerado_agora or not os.path.exists(self.arquivo_gerado_agora):
                return False

            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            currentActivity = PythonActivity.mActivity
            resolver = currentActivity.getContentResolver()

            # Força o modo 'wt' (write-truncate) para evitar arquivos corrompidos
            stream = resolver.openOutputStream(uri, "wt")
            if stream is None: return False

            with open(self.arquivo_gerado_agora, "rb") as origem:
                shutil.copyfileobj(origem, stream)

            # Sincronização e Fechamento Rígido
            stream.flush()
            stream.close()

            try:
                pfd = resolver.openFileDescriptor(uri, "rw")
                fd_desc = pfd.getFileDescriptor()
                fd_desc.sync() 
                pfd.close()
            except: pass

            # 🔥 LIBERAÇÃO AGRESSIVA DE RAM
            Cache.remove('kv.image')
            Cache.remove('kv.texture')
            gc.collect() 
            
            # Reset visual temporário para forçar o Kivy a soltar o arquivo antigo
            orig_source = self.img_preview.source
            self.img_preview.source = ""
            self.img_preview.source = orig_source
            
            print("Salvamento concluído com limpeza de sistema.")
            return True

        except Exception as e:
            print(f"Erro no salvamento: {e}")
            return False

    # ... (Mantenha o restante das funções abaixo)
