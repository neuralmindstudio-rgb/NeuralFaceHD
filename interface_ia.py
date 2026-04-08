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
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.app import App 
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window

from kivymd.uix.button import MDFillRoundFlatButton, MDRectangleFlatButton, MDRoundFlatIconButton, MDIconButton
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu

# Bibliotecas para funções nativas do Android
try:
    from plyer import share, filechooser
except ImportError:
    share = None
    filechooser = None

from banco_dados import db, auth 

tutorial_store = JsonStore('tutorial_status.json')

class TelaPrincipal(Screen):
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
        self.file_manager_aberto = False 
        self.th_conexao = None 
        self.processando_agora = False 

        self.file_manager = MDFileManager(
            exit_manager=self.fechar_seletor,
            select_path=self.processar_selecao_kivymd,
            preview=True,
        )

        layout_geral = FloatLayout()
        
        # BARRA TOPO
        self.barra_t = BoxLayout(size_hint=(1, None), height=dp(55), spacing=dp(10), padding=dp(10), pos_hint={'top': 1})
        self.btn_sair = MDRectangleFlatButton(text="LOGOUT", theme_text_color="Custom", text_color=(1, 0, 0, 1), line_color=(1, 0, 0, 1))
        self.btn_sair.bind(on_release=self.fazer_logout)
        
        self.btn_salvar = MDRoundFlatIconButton(text="SALVAR", icon="download", disabled=True)
        self.btn_salvar.bind(on_release=self.abrir_menu_salvamento) 
        
        self.btn_share = MDIconButton(icon="share-variant", theme_text_color="Custom", text_color=(1, 1, 1, 1), disabled=True)
        self.btn_share.bind(on_release=self.compartilhar_resultado)
        
        self.lbl_rede = Label(text="OFFLINE", color=(1,0,0,1), font_size='9sp', bold=True)
        
        self.btn_mais = MDIconButton(icon="dots-vertical", theme_text_color="Custom", text_color=(1, 1, 1, 1))
        self.btn_mais.bind(on_release=self.abrir_menu)

        self.barra_t.add_widget(self.btn_sair)
        self.barra_t.add_widget(self.btn_salvar)
        self.barra_t.add_widget(self.btn_share)
        self.barra_t.add_widget(self.lbl_rede)
        self.barra_t.add_widget(self.btn_mais)

        # ÁREA DA FOTO
        self.meio = MDBoxLayout(orientation='vertical', size_hint=(0.98, 0.68), pos_hint={'center_x': 0.5, 'center_y': 0.58}, md_bg_color=(0, 0, 0, 0), padding=dp(10))
        with self.meio.canvas.before:
            Color(*self.cor_roxo_destaque)
            self.rect_meio = RoundedRectangle(pos=self.meio.pos, size=self.meio.size, radius=[dp(25)])
        self.meio.bind(pos=self.update_rect_meio, size=self.update_rect_meio)

        self.area_foto = BoxLayout()
        self.img_preview = Image(source='', opacity=0)
        self.area_foto.add_widget(self.img_preview)
        
        self.barra_p = MDProgressBar(type="indeterminate", size_hint_y=None, height=dp(3), opacity=0, color=self.cor_verde_status)
        self.meio.add_widget(self.area_foto)
        self.meio.add_widget(self.barra_
