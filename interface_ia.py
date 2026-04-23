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

        # --- BARRA SUPERIOR (TOPO) ---
        # Ajustado para não ficar sob o relógio/câmera
        self.barra_t = BoxLayout(
            size_hint=(1, None),
            height=dp(85),
            spacing=dp(10),
            padding=[dp(10), dp(40), dp(10), dp(5)],
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
        self.barra_t.add_widget(self.lbl_rede)
        self.barra_t.add_widget(self.btn_mais)

        # --- ÁREA DA FOTO (MEIO) ---
        # Quadro ampliado e centralizado
        self.meio = MDBoxLayout(
            orientation='vertical',
            size_hint=(0.98, 0.62),
            pos_hint={'center_x': 0.5, 'center_y': 0.54},
            md_bg_color=(0, 0, 0, 0),
            padding=dp(5)
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

        # --- PAINEL DE BOTÕES (BASE) ---
        # Aumentamos o padding inferior para 45dp para fugir da barra do Android
        self.painel = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(230),
            padding=[dp(10), dp(5), dp(10), dp(45)],
            spacing=dp(5),
            pos_hint={'x': 0, 'y': 0}
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
                    window.setSoftInputMode(LayoutParams.SOFT_INPUT_ADJUST_RESIZE)
                except Exception as e:
                    print(f"Erro mostrar barras Android: {e}")

            if run_on_ui_thread:
                run_on_ui_thread(_mostrar)()
            else:
                _mostrar()
        except Exception as e:
            print(f"Erro preparar barras Android: {e}")

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
        
        timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
        nome_sugerido = f"NFHD_{timestamp}.jpg"

        intent = Intent(Intent.ACTION_CREATE_DOCUMENT)
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        intent.setType("image/jpeg")
        intent.putExtra(Intent.EXTRA_TITLE, nome_sugerido)
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
                return False

            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            currentActivity = PythonActivity.mActivity
            resolver = currentActivity.getContentResolver()

            stream = resolver.openOutputStream(uri)
            if stream is None:
                return False

            with open(self.arquivo_gerado_agora, "rb") as origem:
                shutil.copyfileobj(origem, stream)

            stream.flush()
            stream.close()

            try:
                pfd = resolver.openFileDescriptor(uri, "rw")
                fd_desc = pfd.getFileDescriptor()
                fd_desc.sync()
                pfd.close()
            except:
                pass

            Cache.remove('kv.image')
            Cache.remove('kv.texture')
            gc.collect() 
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
        content.add_widget(btn1)
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

    def enviar_ao_pc(self, instance):
        if not bd or not bd.local_id:
            self.label_s.text = "LOGIN NECESSÁRIO"
            return
        if self.creditos_atuais <= 0:
            self.exibir_aviso_sem_creditos()
            return
        if not self.servidor_online:
            self.label_s.text = "SERVIDOR OFFLINE"
            return
        if not self.path_base or not self.path_rosto:
            self.label_s.text = "SELECIONE AS FOTOS"
            return
        self.processando_agora = True
        self.imagem_final_pronta = False
        self.recriar_widget_imagem(self.path_base)
        self.set_controles_interativos(False)
        self.label_s.text = "PROCESSANDO IA..."
        self.barra_p.opacity = 1
        self.barra_p.start()
        threading.Thread(target=self.processo_servidor, daemon=True).start()

    def exibir_aviso_sem_creditos(self):
        self.dialogo_sem_creditos = MDDialog(
            title="Saldo Insuficiente",
            text="Seus créditos acabaram! Deseja recarregar agora?",
            buttons=[
                MDRectangleFlatButton(
                    text="DEPOIS",
                    on_release=lambda x: self.dialogo_sem_creditos.dismiss()
                ),
                MDFillRoundFlatButton(
                    text="IR PARA LOJA",
                    md_bg_color=(0, 0.8, 0, 1),
                    on_release=lambda x: (
                        self.dialogo_sem_creditos.dismiss(),
                        self.abrir_loja()
                    )
                )
            ]
        )
        self.dialogo_sem_creditos.open()

    def set_controles_interativos(self, estado):
        self.btn_gerar.disabled = not estado
        self.btn_b.disabled = not estado
        self.btn_r.disabled = not estado
        self.btn_idx.disabled = not estado
        self.btn_limpar.disabled = not estado
        self.btn_rec.disabled = not estado

    def processo_servidor(self):
        tentativas_maximas = 8
        tentativa_atual = 0
        sucesso_ia = False
        while tentativa_atual < tentativas_maximas and not sucesso_ia:
            try:
                tentativa_atual += 1
                if not bd or not bd.local_id:
                    raise Exception("Usuário não autenticado")
                
                pasta_app = App.get_running_app().user_data_dir
                nome_temporario = os.path.join(pasta_app, "ia_temp_result.jpg")
                
                payload = {'face_index': str(self.face_index)}
                combinacao_atual = f"{self.path_base}_{self.path_rosto}"
                deve_cobrar = combinacao_atual != self.ultima_combinacao
                
                with open(self.path_base, 'rb') as fb, open(self.path_rosto, 'rb') as fr:
                    res = self.session.post(
                        self.url_swap,
                        files={'foto_base': fb, 'foto_rosto': fr},
                        data=payload,
                        timeout=45
                    )
                    if res.status_code == 200:
                        with open(nome_temporario, "wb") as f:
                            f.write(res.content)
                        self.arquivo_gerado_agora = nome_temporario
                        if deve_cobrar:
                            try:
                                ok = bd.atualizar_creditos(self.creditos_atuais - 1)
                                if ok:
                                    self.ultima_combinacao = combinacao_atual
                            except:
                                pass
                        sucesso_ia = True
                        Clock.schedule_once(lambda dt: self.sucesso())
                        return
                    else:
                        time.sleep(7)
            except Exception as e:
                print(f"DEBUG Tentativa {tentativa_atual}: {e}")
                time.sleep(7)
        if not sucesso_ia:
            Clock.schedule_once(
                lambda dt: self.erro("SERVIDOR OCUPADO - TENTE NOVAMENTE")
            )

    def sucesso(self):
        self.processando_agora = False
        self.set_controles_interativos(True)
        self.imagem_final_pronta = True
        self.recriar_widget_imagem(self.arquivo_gerado_agora)
        self.btn_salvar.disabled = False
        self.label_s.text = "CONCLUÍDO!"
        self.parar_barra()
        self.atualizar_saldo_ui()

    def erro(self, msg):
        self.processando_agora = False
        self.set_controles_interativos(True)
        self.label_s.text = msg
        self.parar_barra()

    def parar_barra(self):
        self.barra_p.stop()
        self.barra_p.opacity = 0

    def recriar_widget_imagem(self, path):
        self.area_foto.clear_widgets()
        Cache.remove('kv.image')
        Cache.remove('kv.texture')
        self.img_preview = Image(
            source=path,
            allow_stretch=True,
            keep_ratio=True,
            opacity=1
        )
        self.img_preview.reload()
        self.img_preview.bind(
            on_touch_down=self.evento_pressionar_foto,
            on_touch_up=self.evento_soltar_foto
        )
        self.area_foto.add_widget(self.img_preview)

    def atualizar_saldo_ui(self, *args):
        if not bd or not bd.local_id:
            self.creditos_atuais = 0
            self.btn_gerar.text = "GERAR (0)"
            return
        try:
            self.creditos_atuais = bd.pegar_creditos()
            self.btn_gerar.text = f"GERAR ({self.creditos_atuais})"
        except Exception as e:
            print(f"Erro atualizar saldo: {e}")
            self.creditos_atuais = 0
            self.btn_gerar.text = "GERAR (0)"

    def on_enter(self):
        self.mostrar_barras_android()
        Clock.schedule_once(self.mostrar_barras_android, 0.2)
        Clock.schedule_once(self.mostrar_barras_android, 0.6)
        Clock.schedule_once(self.mostrar_barras_android, 1.0)
        self.atualizar_saldo_ui()
        self.verificar_e_registrar_usuario()
        self.checar_termos_no_firebase()
        Window.bind(on_keyboard=self.ao_clicar_voltar)
        if self.th is None or not self.th.is_alive():
            self.th = threading.Thread(target=self.checar_conexao_loop, daemon=True)
            self.th.start()

    def on_leave(self):
        Window.unbind(on_keyboard=self.ao_clicar_voltar)

    def ao_clicar_voltar(self, window, key, *args):
        if key == 27:
            if self.file_manager_aberto:
                self.fechar_seletor()
                return True
            else:
                self.fazer_logout()
                return True
        return False

    def verificar_e_registrar_usuario(self):
        if not bd or not bd.local_id or not bd.current_user:
            return
        try:
            url = f"{bd.DATABASE_URL}/usuarios/{bd.local_id}.json"
            if bd.id_token:
                url = f"{url}?auth={bd.id_token}"
            res = requests.get(url, timeout=10)
            dados = res.json()
            data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
            u_email = bd.current_user.get("email", "")
            if not isinstance(dados, dict):
                dados = {}
            info = {
                "email": dados.get("email", u_email),
                "data_cadastro": dados.get("data_cadastro", data_hoje),
                "creditos": dados.get("creditos", 5),
                "aceitou_termos": dados.get("aceitou_termos", False),
                "nome": dados.get("nome", ""),
                "data_nascimento": dados.get("data_nascimento", "")
            }
            if (
                "email" not in dados
                or "data_cadastro" not in dados
                or "creditos" not in dados
                or "aceitou_termos" not in dados
                or "nome" not in dados
                or "data_nascimento" not in dados
            ):
                requests.patch(url, json=info, timeout=10)
        except Exception as e:
            print(f"Erro verificar usuario: {e}")

    def checar_conexao_loop(self):
        while True:
            if not self.processando_agora:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect((self.ip_servidor, 8080))
                    s.close()
                    Clock.schedule_once(lambda dt: self.atualizar_ui_servidor(True))
                except Exception:
                    Clock.schedule_once(lambda dt: self.atualizar_ui_servidor(False))
            time.sleep(5)

    def atualizar_ui_servidor(self, online):
        self.servidor_online = online
        self.lbl_rede.text = "ONLINE" if online else "OFFLINE"
        self.lbl_rede.color = (0, 1, 0, 1) if online else (1, 0, 0, 1)

    def update_rect_meio(self, instance, value):
        self.rect_meio.pos = instance.pos
        self.rect_meio.size = instance.size

    def evento_pressionar_foto(self, instance, touch):
        if instance.collide_point(*touch.pos) and self.imagem_final_pronta:
            instance.source = self.path_base

    def evento_soltar_foto(self, instance, touch):
        if self.imagem_final_pronta:
            instance.source = self.arquivo_gerado_agora

    def desbloquear_idx(self, dt):
        self.bloqueio_idx = False

    def alternar_rosto(self, instance):
        if self.bloqueio_idx:
            return
        self.bloqueio_idx = True
        Clock.schedule_once(self.desbloquear_idx, 0.2)
        self.face_index = (self.face_index + 1) if self.face_index < 5 else 0
        instance.text = f"TROCAR ROSTO ({self.face_index})"

    def limpar_tudo(self, *args):
        self.area_foto.clear_widgets()
        self.path_base = ""
        self.path_rosto = ""
        self.label_s.text = "Neural Face HD"
        self.btn_salvar.disabled = True
        self.ultima_combinacao = ""

    def fazer_logout(self, *args):
        if bd:
            bd.current_user = None
            bd.id_token = None
            bd.local_id = None
        self.manager.current = 'login'

    def abrir_loja(self, *args):
        if self.manager and self.manager.has_screen('loja'):
            self.manager.current = 'loja'
        else:
            self.label_s.text = "LOJA INDISPONÍVEL"

    def salvar_aceite_firebase(self, *args):
        if not bd or not bd.local_id:
            if self.dialogo_termos:
                self.dialogo_termos.dismiss()
            return
        try:
            url = f"{bd.DATABASE_URL}/usuarios/{bd.local_id}.json"
            if bd.id_token:
                url = f"{url}?auth={bd.id_token}"
            requests.patch(url, json={"aceitou_termos": True}, timeout=10)
            if self.dialogo_termos:
                self.dialogo_termos.dismiss()
        except Exception:
            if self.dialogo_termos:
                self.dialogo_termos.dismiss()

    def exibir_termos_popup(self):
        texto = (
            "[b]TERMOS DE USO E RESPONSABILIDADE LEGAL[/b]\n\n"
            "Ao utilizar o [b]Neural Face HD[/b], você declara ser maior de 18 "
            "anos e assume total responsabilidade civil e criminal pelo uso desta ferramenta, "
            "declarando estar ciente de:\n\n"
            "1. [b]PROTEÇÃO À CRIANÇA (ECA):[/b] É terminantemente proibida a manipulação de "
            "imagens de menores de 18 anos. Violações estão sujeitas às penas da Lei 8.069/90 "
            "e da Lei 14.811/2024 (ECA Digital).\n\n"
            "2. [b]DIREITO DE IMAGEM:[/b] Você declara possuir autorização legal e consensual "
            "de todas as pessoas cujas faces serão processadas.\n\n"
            "3. [b]USO ILÍCITO:[/b] Proibida a criação de conteúdo pornográfico (Deepnude), "
            "difamatório, político-eleitoral enganoso ou que promova ódio/violência.\n\n"
            "4. [b]ISENÇÃO:[/b] O desenvolvedor fornece apenas a tecnologia. O usuário é o "
            "único responsável pela destinação do conteúdo gerado.\n\n"
            "O uso indevido resultará em banimento imediato e cooperação total com autoridades judiciais."
        )
        scroll = ScrollView(size_hint=(1, None), height=dp(380))
        conteudo_texto = Label(
            text=texto,
            markup=True,
            size_hint_y=None,
            color=(1, 1, 1, 1),
            font_size='14sp',
            halign="left",
            valign="top",
            padding=(dp(10), dp(10))
        )
        conteudo_texto.bind(
            width=lambda instance, value: setattr(instance, 'text_size', (value - dp(20), None))
        )
        conteudo_texto.bind(
            texture_size=lambda instance, value: setattr(instance, 'height', value[1])
        )
        scroll.add_widget(conteudo_texto)
        self.dialogo_termos = MDDialog(
            title="CONSENTIMENTO JURÍDICO",
            type="custom",
            content_cls=scroll,
            size_hint_x=0.9,
            auto_dismiss=False,
            buttons=[
                MDRectangleFlatButton(
                    text="RECUSAR",
                    theme_text_color="Custom",
                    text_color=(1, 0, 0, 1),
                    line_color=(1, 0, 0, 1),
                    on_release=lambda x: (self.dialogo_termos.dismiss(), self.fazer_logout())
                ),
                MDFillRoundFlatButton(
                    text="EU ACEITO",
                    on_release=self.salvar_aceite_firebase
                )
            ]
        )
        self.dialogo_termos.open()

    def checar_termos_no_firebase(self):
        if not bd or not bd.local_id:
            return
        try:
            url = f"{bd.DATABASE_URL}/usuarios/{bd.local_id}.json"
            if bd.id_token:
                url = f"{url}?auth={bd.id_token}"
            res = requests.get(url, timeout=10)
            dados = res.json()
            if not dados or not dados.get("aceitou_termos", False):
                Clock.schedule_once(lambda dt: self.exibir_termos_popup(), 0.5)
        except Exception as e:
            print(f"Erro termos firebase: {e}")
