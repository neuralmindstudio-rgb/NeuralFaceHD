import os
import requests
import shutil
import time
import threading
import socket
from datetime import datetime

from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
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

        self.barra_t = BoxLayout(
            size_hint=(1, None),
            height=dp(55),
            spacing=dp(10),
            padding=dp(10),
            pos_hint={'top': 1}
        )

        self.btn_sair = MDRectangleFlatButton(
            text="LOGOUT",
            theme_text_color="Custom",
            text_color=(1, 0, 0, 1),
            line_color=(1, 0, 0, 1)
        )
        self.btn_sair.bind(on_release=self.fazer_logout)

        self.btn_salvar = MDRoundFlatIconButton(
            text="SALVAR",
            icon="download",
            disabled=True
        )
        self.btn_salvar.bind(on_release=self.abrir_menu_salvamento)

        # 🔴 COMPARTILHAR DESATIVADO TEMPORARIAMENTE
        # self.btn_share = MDIconButton(
        #     icon="share-variant",
        #     theme_text_color="Custom",
        #     text_color=(1, 1, 1, 1),
        #     disabled=True
        # )
        # self.btn_share.bind(on_release=self.compartilhar_resultado)

        self.lbl_rede = Label(
            text="OFFLINE",
            color=(1, 0, 0, 1),
            font_size='9sp',
            bold=True
        )

        self.btn_mais = MDIconButton(
            icon="dots-vertical",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )
        self.btn_mais.bind(on_release=self.abrir_menu)

        self.barra_t.add_widget(self.btn_sair)
        self.barra_t.add_widget(self.btn_salvar)
        # self.barra_t.add_widget(self.btn_share)
        self.barra_t.add_widget(self.lbl_rede)
        self.barra_t.add_widget(self.btn_mais)

        self.meio = MDBoxLayout(
            orientation='vertical',
            size_hint=(0.98, 0.68),
            pos_hint={'center_x': 0.5, 'center_y': 0.58},
            md_bg_color=(0, 0, 0, 0),
            padding=dp(10)
        )
        with self.meio.canvas.before:
            Color(*self.cor_roxo_destaque)
            self.rect_meio = RoundedRectangle(
                pos=self.meio.pos,
                size=self.meio.size,
                radius=[dp(25)]
            )
        self.meio.bind(pos=self.update_rect_meio, size=self.update_rect_meio)

        self.area_foto = BoxLayout()
        self.img_preview = Image(source='', opacity=0)
        self.area_foto.add_widget(self.img_preview)

        self.barra_p = MDProgressBar(
            type="indeterminate",
            size_hint_y=None,
            height=dp(3),
            opacity=0,
            color=self.cor_verde_status,
            running_duration=0.3
        )
        self.meio.add_widget(self.area_foto)
        self.meio.add_widget(self.barra_p)

        self.painel = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(185),
            padding=dp(10),
            spacing=dp(5),
            pos_hint={'bottom': 1}
        )

        self.label_s = Label(
            text="Neural Face HD",
            color=(0.5, 0.5, 0.6, 1),
            font_size='11sp',
            size_hint_y=None,
            height=dp(18)
        )

        l1 = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(44))
        self.btn_b = MDRoundFlatIconButton(
            text="BASE",
            icon="image-plus",
            size_hint_x=0.5
        )
        self.btn_b.bind(on_release=lambda x: self.abrir_seletor_nativo("base"))

        self.btn_r = MDRoundFlatIconButton(
            text="ROSTO",
            icon="face-man-profile",
            size_hint_x=0.5
        )
        self.btn_r.bind(on_release=lambda x: self.abrir_seletor_nativo("rosto"))

        l1.add_widget(self.btn_b)
        l1.add_widget(self.btn_r)

        self.btn_idx = MDRoundFlatIconButton(
            text="TROCAR ROSTO (0)",
            icon="account-switch",
            size_hint_x=1,
            height=dp(40)
        )
        self.btn_idx.bind(on_release=self.alternar_rosto)

        l2 = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(50))
        self.btn_limpar = MDRectangleFlatButton(text="LIMPAR", size_hint_x=0.25)
        self.btn_limpar.bind(on_release=self.limpar_tudo)

        self.btn_gerar = MDFillRoundFlatButton(
            text="GERAR",
            md_bg_color=(0.5, 0, 0.8, 1),
            size_hint_x=0.45
        )
        self.btn_gerar.bind(on_release=self.enviar_ao_pc)

        self.btn_rec = MDRectangleFlatButton(
            text="+ CRÉDITOS",
            size_hint_x=0.3,
            theme_text_color="Custom",
            text_color=(0, 0.8, 0, 1),
            line_color=(0, 0.8, 0, 1)
        )
        self.btn_rec.bind(on_release=self.abrir_loja)

        l2.add_widget(self.btn_limpar)
        l2.add_widget(self.btn_gerar)
        l2.add_widget(self.btn_rec)

        self.painel.add_widget(self.label_s)
        self.painel.add_widget(l1)
        self.painel.add_widget(self.btn_idx)
        self.painel.add_widget(l2)

        layout_geral.add_widget(self.barra_t)
        layout_geral.add_widget(self.meio)
        layout_geral.add_widget(self.painel)
        self.add_widget(layout_geral)

        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Termos de Uso",
                "on_release": lambda x="Termos": self.menu_callback(x)
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Sobre",
                "on_release": lambda x="Sobre": self.menu_callback(x)
            },
        ]
        self.dropdown = MDDropdownMenu(
            caller=self.btn_mais,
            items=menu_items,
            width_mult=4
        )

    # =========================
    # ANDROID SYSTEM BARS
    # =========================
    def mostrar_barras_android(self, *args):
        if not ANDROID_OK:
            return

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
                except Exception as e:
                    print(f"Erro mostrar barras Android: {e}")

            if run_on_ui_thread:
                run_on_ui_thread(_mostrar)()
            else:
                _mostrar()

        except Exception as e:
            print(f"Erro preparar barras Android: {e}")

    # =========================
    # MENU
    # =========================
    def abrir_menu(self, instance):
        self.dropdown.open()

    def menu_callback(self, opcao):
        self.dropdown.dismiss()
        if opcao == "Termos":
            self.exibir_termos_popup()
        elif opcao == "Sobre":
            MDDialog(
                title="Neural Mind Studio",
                text="Neural Face HD v1.0\n\nAI avançada para imagens."
            ).open()

    # =========================
    # SELETOR NATIVO ANDROID
    # =========================
    def abrir_seletor_nativo(self, tipo):
        self.tipo_atual = tipo

        if ANDROID_OK:
            try:
                if tipo == "salvar":
                    self.abrir_salvar_android()
                else:
                    self.abrir_seletor_android()
                return
            except Exception as e:
                print(f"Erro seletor Android nativo: {e}")

        if filechooser and tipo != "salvar":
            try:
                filechooser.open_file(on_selection=self.processar_selecao_nativa)
            except Exception:
                self.abrir_fallback_filemanager()
        else:
            self.abrir_fallback_filemanager()

    def abrir_seletor_android(self):
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        currentActivity = PythonActivity.mActivity

        intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        intent.setType("image/*")
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        intent.addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)

        currentActivity.startActivityForResult(intent, self.PICK_IMAGE_REQUEST)

    def abrir_salvar_android(self):
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        currentActivity = PythonActivity.mActivity

        nome = "NeuralFaceHD_" + time.strftime("%Y%m%d_%H%M%S") + ".jpg"

        intent = Intent(Intent.ACTION_CREATE_DOCUMENT)
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        intent.setType("image/jpeg")
        intent.putExtra(Intent.EXTRA_TITLE, nome)

        currentActivity.startActivityForResult(intent, self.CREATE_FILE_REQUEST)

    def on_activity_result(self, request_code, result_code, intent):
        if not ANDROID_OK:
            return

        try:
            Activity = autoclass('android.app.Activity')
            if result_code != Activity.RESULT_OK or intent is None:
                return

            if request_code == self.PICK_IMAGE_REQUEST:
                uri = intent.getData()
                if uri is None:
                    return

                caminho_local = self.copiar_uri_para_arquivo(uri)
                if caminho_local:
                    Clock.schedule_once(lambda dt: self.select_path(caminho_local))
                return

            if request_code == self.CREATE_FILE_REQUEST:
                uri = intent.getData()
                if uri is None:
                    return

                ok = self.salvar_em_uri(uri)
                self.label_s.text = "SALVO COM SUCESSO!" if ok else "ERRO AO GRAVAR ARQUIVO"
                return

        except Exception as e:
            print(f"Erro on_activity_result: {e}")

    def copiar_uri_para_arquivo(self, uri):
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            currentActivity = PythonActivity.mActivity
            resolver = currentActivity.getContentResolver()

            try:
                Intent = autoclass('android.content.Intent')
                flags = (
                    Intent.FLAG_GRANT_READ_URI_PERMISSION |
                    Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION
                )
                resolver.takePersistableUriPermission(uri, flags)
            except Exception:
                pass

            pfd = resolver.openFileDescriptor(uri, "r")
            if pfd is None:
                return ""

            fd = pfd.detachFd()
            pasta_destino = os.path.join(App.get_running_app().user_data_dir, "selecoes")
            os.makedirs(pasta_destino, exist_ok=True)

            nome_arquivo = f"{self.tipo_atual}_{int(time.time() * 1000)}.jpg"
            caminho_destino = os.path.join(pasta_destino, nome_arquivo)

            with os.fdopen(fd, "rb") as origem, open(caminho_destino, "wb") as destino:
                shutil.copyfileobj(origem, destino)

            return caminho_destino
        except Exception as e:
            print(f"Erro copiar URI para arquivo: {e}")
            return ""

    def salvar_em_uri(self, uri):
    try:
        if not self.arquivo_gerado_agora or not os.path.exists(self.arquivo_gerado_agora):
            print("Erro salvar_em_uri: arquivo não encontrado")
            return False

        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        currentActivity = PythonActivity.mActivity
        resolver = currentActivity.getContentResolver()

        # 🔥 IMPORTANTE: modo "w" resolve erro de salvamento
        stream = resolver.openOutputStream(uri, "w")
        if stream is None:
            print("Erro salvar_em_uri: stream None")
            return False

        with open(self.arquivo_gerado_agora, "rb") as origem:
            while True:
                chunk = origem.read(8192)
                if not chunk:
                    break
                stream.write(chunk)

        stream.flush()
        stream.close()

        print("Arquivo salvo com sucesso")
        return True

    except Exception as e:
        print(f"Erro salvar_em_uri: {e}")
        return False

    def abrir_fallback_filemanager(self):
        self.file_manager_aberto = True
        path = "/storage/emulated/0/" if os.path.exists("/storage/emulated/0/") else os.path.expanduser("~")
        self.file_manager.show(path)

    def processar_selecao_nativa(self, selection):
        if selection:
            Clock.schedule_once(lambda dt: self.select_path(selection[0]))

    def processar_selecao_kivymd(self, path):
        if self.tipo_atual != "salvar" and os.path.isdir(path):
            self.file_manager.show(path)
            return
        self.fechar_seletor()
        self.select_path(path)

    def fechar_seletor(self, *args):
        try:
            self.file_manager.close()
        except Exception:
            pass
        self.file_manager_aberto = False

    def select_path(self, path):
        if not os.path.exists(path):
            return

        if self.tipo_atual == "base":
            self.path_base = path
            self.face_index = 0
            self.btn_idx.text = f"TROCAR ROSTO ({self.face_index})"
            self.recriar_widget_imagem(path)
        else:
            self.path_rosto = path
            if self.path_base:
                self.recriar_widget_imagem(self.path_base)

    # =========================
    # SALVAR / COMPARTILHAR
    # =========================
    def abrir_menu_salvamento(self, instance):
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(10),
            adaptive_height=True
        )
        btn1 = MDFillRoundFlatButton(
            text="SALVAR NA GALERIA",
            md_bg_color=self.cor_roxo_destaque,
            size_hint_x=1,
            on_release=self.salvar_escolhendo_pasta
        )

        # 🔴 COMPARTILHAR DESATIVADO TEMPORARIAMENTE
        # btn2 = MDFillRoundFlatButton(
        #     text="COMPARTILHAR",
        #     md_bg_color=(0.3, 0.3, 0.8, 1),
        #     size_hint_x=1,
        #     on_release=self.compartilhar_resultado
        # )

        content.add_widget(btn1)
        # content.add_widget(btn2)

        self.dialogo_save_choice = MDDialog(
            title="Imagem Pronta!",
            type="custom",
            content_cls=content
        )
        self.dialogo_save_choice.open()

    def salvar_escolhendo_pasta(self, instance):
        if self.dialogo_save_choice:
            self.dialogo_save_choice.dismiss()

        self.tipo_atual = "salvar"

        if ANDROID_OK:
            try:
                self.abrir_salvar_android()
                return
            except Exception as e:
                print(f"Erro salvar Android nativo: {e}")

        self.file_manager_aberto = True
        self.file_manager.show("/storage/emulated/0")

    def compartilhar_resultado(self, *args):
        if self.dialogo_save_choice:
            self.dialogo_save_choice.dismiss()

        if not self.arquivo_gerado_agora or not os.path.exists(self.arquivo_gerado_agora):
            self.label_s.text = "ARQUIVO NÃO ENCONTRADO"
            return

        if ANDROID_OK:
            try:
                self.compartilhar_android(self.arquivo_gerado_agora)
                return
            except Exception as e:
                print(f"Erro compartilhar Android: {e}")
                self.label_s.text = "ERRO AO COMPARTILHAR"
                return

        if share:
            try:
                share.share(filepath=self.arquivo_gerado_agora)
                return
            except Exception as e:
                print(f"Erro share plyer: {e}")
                self.label_s.text = "ERRO AO COMPARTILHAR"
                return

        self.label_s.text = "COMPARTILHAMENTO INDISPONÍVEL"

    def compartilhar_android(self, caminho_arquivo):
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        ClipData = autoclass('android.content.ClipData')
        MediaStoreImagesMedia = autoclass('android.provider.MediaStore$Images$Media')
        ContentValues = autoclass('android.content.ContentValues')

        currentActivity = PythonActivity.mActivity
        resolver = currentActivity.getContentResolver()

        valores = ContentValues()
        nome = f"NeuralFace_{int(time.time())}.jpg"
        valores.put("_display_name", nome)
        valores.put("mime_type", "image/jpeg")

     
