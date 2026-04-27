import os
import requests
import shutil
import time
import threading
import socket
import gc  
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

# Fallbacks e Android Nativo
try:
    from plyer import share, filechooser
except ImportError:
    share = None
    filechooser = None

try:
    from jnius import autoclass, cast
    ANDROID_OK = True
except Exception:
    autoclass = None
    cast = None
    ANDROID_OK = False

try:
    from android import activity
    from android.runnable import run_on_ui_thread
except Exception:
    activity = None
    run_on_ui_thread = None

try:
    import banco_dados as bd
except Exception as e:
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
        self.dialogo_termos = None
        self.file_manager_aberto = False
        self.th = None
        self.processando_agora = False
        self.tipo_atual = "base"

        self.file_manager = MDFileManager(
            exit_manager=self.fechar_seletor,
            select_path=self.processar_selecao_kivymd,
            preview=True,
        )

        if ANDROID_OK and activity:
            try:
                activity.bind(on_activity_result=self.on_activity_result)
            except: pass

        layout_geral = FloatLayout()

        # --- BARRA SUPERIOR (Ajustada para o Gabarito Perfeito) ---
        self.barra_t = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(115),          
            spacing=dp(10),
            padding=[dp(10), dp(75), dp(10), dp(5)], 
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

        # --- ÁREA CENTRAL (Ajustada para o Gabarito Perfeito) ---
        self.meio = MDBoxLayout(
            orientation='vertical',
            size_hint=(0.98, 0.58), 
            pos_hint={'center_x': 0.5, 'center_y': 0.54}, 
            md_bg_color=(0, 0, 0, 0),
            padding=dp(2)
        )
        with self.meio.canvas.before:
            Color(*self.cor_roxo_destaque)
            self.rect_meio = RoundedRectangle(pos=self.meio.pos, size=self.meio.size, radius=[dp(25)])
        self.meio.bind(pos=self.update_rect_meio, size=self.update_rect_meio)

        self.area_foto = BoxLayout()
        self.img_preview = Image(source='', opacity=0)
        self.area_foto.add_widget(self.img_preview)

        self.barra_p = MDProgressBar(type="indeterminate", size_hint_y=None, height=dp(3), opacity=0, color=self.cor_verde_status)
        self.meio.add_widget(self.area_foto)
        self.meio.add_widget(self.barra_p)

        # --- PAINEL INFERIOR (Fixo) ---
        self.painel = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(185),
            padding=[dp(10), dp(5), dp(10), dp(5)],
            spacing=dp(5),
            pos_hint={'x': 0, 'y': 0.05} 
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

        l2.add_widget(self.btn_limpar); l2.add_widget(self.btn_gerar); l2.add_widget(self.btn_rec)
        self.painel.add_widget(self.label_s); self.painel.add_widget(l1); self.painel.add_widget(self.btn_idx); self.painel.add_widget(l2)
        
        self.espacador_android = Widget(size_hint_y=None, height=0)
        self.painel.add_widget(self.espacador_android)

        layout_geral.add_widget(self.meio)
        layout_geral.add_widget(self.painel)
        layout_geral.add_widget(self.barra_t) # Adicionada por último para ficar no topo
        self.add_widget(layout_geral)

        menu_items = [{"viewclass": "OneLineListItem", "text": "Termos de Uso", "on_release": lambda x="Termos": self.menu_callback(x)},
                      {"viewclass": "OneLineListItem", "text": "Sobre", "on_release": lambda x="Sobre": self.menu_callback(x)}]
        self.dropdown = MDDropdownMenu(caller=self.btn_mais, items=menu_items, width_mult=4)

    def on_enter(self):
        self.atualizar_saldo_ui()
        Clock.schedule_once(lambda dt: self.checar_termos_no_firebase(), 1)
        if self.th is None or not self.th.is_alive():
            self.th = threading.Thread(target=self.checar_conexao_loop, daemon=True)
            self.th.start()

    def salvar_aceite_firebase(self, *args):
        if not bd or not bd.local_id:
            if self.dialogo_termos: self.dialogo_termos.dismiss()
            return
        try:
            url = f"{bd.DATABASE_URL}/usuarios/{bd.local_id}.json"
            if bd.id_token: url = f"{url}?auth={bd.id_token}"
            requests.patch(url, json={"aceitou_termos": True}, timeout=10)
            if self.dialogo_termos: self.dialogo_termos.dismiss()
        except:
            if self.dialogo_termos: self.dialogo_termos.dismiss()

    def exibir_termos_popup(self):
        texto = (
            "[b]TERMOS DE USO E RESPONSABILIDADE LEGAL[/b]\n\n"
            "Ao utilizar o [b]Neural Face HD[/b], você declara ser maior de 18 "
            "anos e assume total responsabilidade civil e criminal pelo uso desta ferramenta, "
            "declarando estar ciente de:\n\n"
            "1. [b]PROTEÇÃO À CRIANÇA (ECA):[/b] É terminantemente proibida a manipulação de "
            "imagens de menores de 18 anos (Lei 14.811/2024).\n\n"
            "2. [b]DIREITO DE IMAGEM:[/b] Você declara possuir autorização legal das pessoas processadas.\n\n"
            "3. [b]USO ILÍCITO:[/b] Proibida a criação de conteúdo pornográfico, difamatório ou político enganoso.\n\n"
            "4. [b]ISENÇÃO:[/b] O desenvolvedor fornece a tecnologia, mas o usuário é o único responsável pelo uso."
        )
        scroll = ScrollView(size_hint=(1, None), height=dp(350))
        lbl = Label(text=texto, markup=True, size_hint_y=None, color=(1,1,1,1), font_size='14sp', halign="left", valign="top", padding=(dp(10), dp(10)))
        lbl.bind(width=lambda ins, val: setattr(ins, 'text_size', (val - dp(20), None)))
        lbl.bind(texture_size=lambda ins, val: setattr(ins, 'height', val[1]))
        scroll.add_widget(lbl)
        self.dialogo_termos = MDDialog(title="CONSENTIMENTO JURÍDICO", type="custom", content_cls=scroll, size_hint_x=0.9, auto_dismiss=False,
            buttons=[
                MDRectangleFlatButton(text="RECUSAR", text_color=(1,0,0,1), on_release=lambda x: (self.dialogo_termos.dismiss(), self.fazer_logout())),
                MDFillRoundFlatButton(text="EU ACEITO", on_release=self.salvar_aceite_firebase)
            ])
        self.dialogo_termos.open()

    def checar_termos_no_firebase(self):
        if not bd or not bd.local_id: return
        try:
            url = f"{bd.DATABASE_URL}/usuarios/{bd.local_id}.json"
            if bd.id_token: url = f"{url}?auth={bd.id_token}"
            res = requests.get(url, timeout=10)
            dados = res.json()
            if not dados or not dados.get("aceitou_termos", False):
                self.exibir_termos_popup()
        except: pass

    # --- RESTANTE DAS FUNÇÕES (Mantidas do original) ---
    def atualizar_saldo_ui(self, *args):
        if not bd or not bd.local_id: self.btn_gerar.text = "GERAR (0)"; return
        try:
            self.creditos_atuais = bd.pegar_creditos()
            self.btn_gerar.text = f"GERAR ({self.creditos_atuais})"
        except: self.btn_gerar.text = "GERAR (0)"

    def abrir_menu(self, instance): self.dropdown.open()
    def menu_callback(self, opcao):
        self.dropdown.dismiss()
        if opcao == "Termos": self.exibir_termos_popup()
        elif opcao == "Sobre": MDDialog(title="Neural Mind Studio", text="Neural Face HD v1.0").open()

    def abrir_seletor_nativo(self, tipo):
        self.tipo_atual = tipo
        if ANDROID_OK:
            try:
                if tipo == "salvar": self.abrir_salvar_android()
                else: self.abrir_seletor_android()
                return
            except: pass
        self.abrir_fallback_filemanager()

    def abrir_seletor_android(self):
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        intent.setType("image/*")
        PythonActivity.mActivity.startActivityForResult(intent, self.PICK_IMAGE_REQUEST)

    def abrir_salvar_android(self):
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        intent = Intent(Intent.ACTION_CREATE_DOCUMENT)
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        intent.setType("image/jpeg")
        intent.putExtra(Intent.EXTRA_TITLE, f"NeuralFace_{ts}.jpg")
        PythonActivity.mActivity.startActivityForResult(intent, self.CREATE_FILE_REQUEST)

    def on_activity_result(self, request_code, result_code, intent):
        if not ANDROID_OK: return
        try:
            Activity = autoclass('android.app.Activity')
            if result_code != Activity.RESULT_OK or intent is None: return
            uri = intent.getData()
            if request_code == self.PICK_IMAGE_REQUEST:
                path = self.copiar_uri_para_arquivo(uri)
                if path: Clock.schedule_once(lambda dt: self.select_path(path))
            elif request_code == self.CREATE_FILE_REQUEST:
                if self.salvar_em_uri(uri): self.label_s.text = "SALVO COM SUCESSO!"
        except: pass

    def copiar_uri_para_arquivo(self, uri):
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            resolver = PythonActivity.mActivity.getContentResolver()
            pfd = resolver.openFileDescriptor(uri, "r")
            dest = os.path.join(App.get_running_app().user_data_dir, f"temp_{int(time.time())}.jpg")
            with os.fdopen(pfd.detachFd(), "rb") as o, open(dest, "wb") as d:
                shutil.copyfileobj(o, d)
            return dest
        except: return ""

    def salvar_em_uri(self, uri):
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            resolver = PythonActivity.mActivity.getContentResolver()
            stream = resolver.openOutputStream(uri, "wt")
            with open(self.arquivo_gerado_agora, "rb") as origem:
                shutil.copyfileobj(origem, stream)
            stream.close()
            Cache.remove('kv.image'); Cache.remove('kv.texture'); gc.collect()
            return True
        except: return False

    def select_path(self, path):
        if self.tipo_atual == "base":
            self.path_base = path; self.face_index = 0
            self.btn_idx.text = f"TROCAR ROSTO ({self.face_index})"
            self.recriar_widget_imagem(path)
        else:
            self.path_rosto = path
            if self.path_base: self.recriar_widget_imagem(self.path_base)

    def recriar_widget_imagem(self, path):
        self.area_foto.clear_widgets()
        Cache.remove('kv.image'); Cache.remove('kv.texture')
        self.img_preview = Image(source=path, allow_stretch=True, keep_ratio=True, opacity=1)
        self.img_preview.bind(on_touch_down=self.evento_pressionar_foto, on_touch_up=self.evento_soltar_foto)
        self.area_foto.add_widget(self.img_preview)

    def abrir_menu_salvamento(self, instance):
        content = MDBoxLayout(orientation="vertical", spacing=dp(12), padding=dp(10), adaptive_height=True)
        btn = MDFillRoundFlatButton(text="SALVAR NA GALERIA", md_bg_color=self.cor_roxo_destaque, size_hint_x=1, on_release=self.salvar_escolhendo_pasta)
        content.add_widget(btn)
        self.dialogo_save_choice = MDDialog(title="Imagem Pronta!", type="custom", content_cls=content)
        self.dialogo_save_choice.open()

    def salvar_escolhendo_pasta(self, instance):
        if self.dialogo_save_choice: self.dialogo_save_choice.dismiss()
        self.abrir_seletor_nativo("salvar")

    def enviar_ao_pc(self, instance):
        if self.creditos_atuais <= 0: self.exibir_aviso_sem_creditos(); return
        if not self.servidor_online: self.label_s.text = "SERVIDOR OFFLINE"; return
        if not self.path_base or not self.path_rosto: self.label_s.text = "SELECIONE AS FOTOS"; return
        self.set_controles_interativos(False); self.label_s.text = "PROCESSANDO IA..."
        self.barra_p.opacity = 1; self.barra_p.start()
        threading.Thread(target=self.processo_servidor, daemon=True).start()

    def processo_servidor(self):
        try:
            nome_temp = os.path.join(App.get_running_app().user_data_dir, "ia_temp_result.jpg")
            payload = {'face_index': str(self.face_index)}
            with open(self.path_base, 'rb') as fb, open(self.path_rosto, 'rb') as fr:
                res = self.session.post(self.url_swap, files={'foto_base': fb, 'foto_rosto': fr}, data=payload, timeout=45)
                if res.status_code == 200:
                    with open(nome_temp, "wb") as f: f.write(res.content)
                    self.arquivo_gerado_agora = nome_temp
                    bd.atualizar_creditos(self.creditos_atuais - 1)
                    Clock.schedule_once(lambda dt: self.sucesso())
                else: Clock.schedule_once(lambda dt: self.erro("ERRO NO SERVIDOR"))
        except: Clock.schedule_once(lambda dt: self.erro("FALHA DE CONEXÃO"))

    def sucesso(self):
        self.set_controles_interativos(True); self.imagem_final_pronta = True
        self.recriar_widget_imagem(self.arquivo_gerado_agora)
        self.btn_salvar.disabled = False; self.label_s.text = "CONCLUÍDO!"
        self.parar_barra(); self.atualizar_saldo_ui()

    def erro(self, msg):
        self.set_controles_interativos(True); self.label_s.text = msg; self.parar_barra()

    def parar_barra(self): self.barra_p.stop(); self.barra_p.opacity = 0
    def set_controles_interativos(self, estado):
        for b in [self.btn_gerar, self.btn_b, self.btn_r, self.btn_idx, self.btn_limpar]: b.disabled = not estado

    def checar_conexao_loop(self):
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2); s.connect((self.ip_servidor, 8080)); s.close()
                Clock.schedule_once(lambda dt: self.atualizar_ui_servidor(True))
            except: Clock.schedule_once(lambda dt: self.atualizar_ui_servidor(False))
            time.sleep(5)

    def atualizar_ui_servidor(self, online):
        self.servidor_online = online
        self.lbl_rede.text = "ONLINE" if online else "OFFLINE"
        self.lbl_rede.color = (0, 1, 0, 1) if online else (1, 0, 0, 1)

    def fazer_logout(self, *args):
        if bd: bd.current_user = None; bd.id_token = None; bd.local_id = None
        self.manager.current = 'login'

    def alternar_rosto(self, instance):
        self.face_index = (self.face_index + 1) if self.face_index < 5 else 0
        instance.text = f"TROCAR ROSTO ({self.face_index})"

    def limpar_tudo(self, *args):
        self.area_foto.clear_widgets(); self.path_base = ""; self.path_rosto = ""
        self.label_s.text = "Neural Face HD"; self.btn_salvar.disabled = True

    def fechar_seletor(self, *args): self.file_manager.close()
    def processar_selecao_kivymd(self, path): self.fechar_seletor(); self.select_path(path)
    def update_rect_meio(self, instance, value): self.rect_meio.pos = instance.pos; self.rect_meio.size = instance.size
    def evento_pressionar_foto(self, instance, touch):
        if instance.collide_point(*touch.pos) and self.imagem_final_pronta: instance.source = self.path_base
    def evento_soltar_foto(self, instance, touch):
        if self.imagem_final_pronta: instance.source = self.arquivo_gerado_agora
    def abrir_loja(self, *args):
        if self.manager and self.manager.has_screen('loja'): self.manager.current = 'loja'
    def abrir_fallback_filemanager(self):
        self.file_manager.show("/storage/emulated/0/" if os.path.exists("/storage/emulated/0/") else os.path.expanduser("~"))

    def exibir_aviso_sem_creditos(self):
        self.dialogo_sem_creditos = MDDialog(title="Saldo Insuficiente", text="Seus créditos acabaram!",
            buttons=[MDRectangleFlatButton(text="DEPOIS", on_release=lambda x: self.dialogo_sem_creditos.dismiss()),
                     MDFillRoundFlatButton(text="LOJA", on_release=lambda x: (self.dialogo_sem_creditos.dismiss(), self.abrir_loja()))])
        self.dialogo_sem_creditos.open()
