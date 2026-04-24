import os
import threading
import requests
import json
import uuid
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.core.clipboard import Clipboard
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.popup import Popup 

from kivymd.uix.card import MDCard
from kivymd.uix.button import MDFillRoundFlatButton, MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog

from banco_dados import db, auth 

try:
    import config_mp
except ImportError:
    config_mp = None

class TelaLoja(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.popup_pix = None 
        
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        layout_geral = FloatLayout()

        # Container Central
        self.container_meio = BoxLayout(
            orientation='vertical', 
            size_hint=(0.9, None), 
            spacing=dp(15),
            pos_hint={'center_x': 0.5, 'center_y': 0.55}
        )
        self.container_meio.bind(minimum_height=self.container_meio.setter('height'))

        # Título
        self.container_meio.add_widget(Label(
            text="RECARREGAR CRÉDITOS", 
            font_size='22sp', bold=True, color=(0.6, 0.2, 1, 1),
            size_hint_y=None, height=dp(50)
        ))

        # Logo
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        self.logo = Image(
            source='logo.png', 
            size_hint=(1, None), height=dp(250), 
            allow_stretch=True, keep_ratio=True
        )
        self.container_meio.add_widget(self.logo)

        # Pacotes
        self.container_pacotes = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None)
        self.container_pacotes.bind(minimum_height=self.container_pacotes.setter('height'))
        
        self.container_pacotes.add_widget(self.criar_card_pacote("BRONZE", "10", "4.99", "#CD7F32"))
        self.container_pacotes.add_widget(self.criar_card_pacote("PRATA", "30", "9.99", "#C0C0C0"))
        self.container_pacotes.add_widget(self.criar_card_pacote("OURO", "100", "24.99", "#FFD700"))
        self.container_meio.add_widget(self.container_pacotes)

        layout_geral.add_widget(self.container_meio)

        # Rodapé
        footer = BoxLayout(orientation='vertical', size_hint=(0.9, None), height=dp(130), spacing=dp(15), pos_hint={'center_x': 0.5, 'y': 0.06})
        footer.add_widget(Label(text="© 2026 Neural Mind Studio", font_size='10sp', color=(0.4, 0.4, 0.4, 1)))
        
        btn_voltar = MDRectangleFlatButton(text="VOLTAR", text_color=(1, 1, 1, 1), line_color=(0.5, 0.5, 0.5, 1), size_hint_x=1)
        btn_voltar.bind(on_release=self.ir_para_principal)
        footer.add_widget(btn_voltar)
        
        layout_geral.add_widget(footer)
        self.add_widget(layout_geral)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def ir_para_principal(self, *args):
        self.manager.current = 'principal'

    def criar_card_pacote(self, nome, qtd, preco, cor_hex):
        card = MDCard(orientation='horizontal', size_hint=(1, None), height=dp(80), padding=dp(10), md_bg_color=(0.1, 0.1, 0.12, 1), radius=[dp(15)])
        info = BoxLayout(orientation='vertical')
        info.add_widget(Label(text=f"PACOTE {nome}", bold=True, color=get_color_from_hex(cor_hex), halign="left"))
        info.add_widget(Label(text=f"{qtd} Créditos de IA", font_size='11sp', color=(0.7, 0.7, 0.7, 1)))
        
        venda = BoxLayout(orientation='vertical', size_hint_x=0.4)
        venda.add_widget(Label(text=f"R$ {preco}", font_size='16sp', bold=True))
        
        btn_comprar = MDFillRoundFlatButton(
            text="COMPRAR", font_size='10sp', md_bg_color=get_color_from_hex("#6200EE"),
            on_release=lambda x: self.gerar_pix_mp(nome, preco, qtd)
        )
        venda.add_widget(btn_comprar)
        card.add_widget(info); card.add_widget(venda)
        return card

    def gerar_pix_mp(self, nome, valor, qtd):
        if not config_mp or not hasattr(config_mp, 'MP_ACCESS_TOKEN'):
            MDDialog(title="Erro", text="Serviço de pagamento indisponível.").open()
            return
            
        def task():
            url = "https://api.mercadopago.com/v1/payments"
            headers = {
                "Authorization": f"Bearer {config_mp.MP_ACCESS_TOKEN}", 
                "X-Idempotency-Key": str(uuid.uuid4()), 
                "Content-Type": "application/json"
            }
            payload = {
                "transaction_amount": float(valor), 
                "description": f"Neural Face HD - {nome}", 
                "payment_method_id": "pix", 
                "payer": {"email": "cliente@neuralfacehd.com"}
            }
            try:
                res = requests.post(url, headers=headers, json=payload, timeout=15)
                if res.status_code == 201:
                    dados = res.json()
                    pix_code = dados['point_of_interaction']['transaction_data']['qr_code']
                    pay_id = dados['id']
                    Clock.schedule_once(lambda dt: self.exibir_pix_dialogo(pix_code, pay_id, qtd))
                else:
                    Clock.schedule_once(lambda dt: MDDialog(title="Erro", text="Falha ao gerar PIX.").open())
            except:
                Clock.schedule_once(lambda dt: MDDialog(title="Conexão", text="Erro de rede ao processar PIX.").open())
        
        threading.Thread(target=task, daemon=True).start()

    def exibir_pix_dialogo(self, codigo, pay_id, qtd):
        layout_p = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        with layout_p.canvas.before:
            Color(0.15, 0.15, 0.17, 1)
            self.bg_pop = RoundedRectangle(pos=layout_p.pos, size=layout_p.size, radius=[dp(20)])
        layout_p.bind(pos=self.update_bg_pop, size=self.update_bg_pop)

        layout_p.add_widget(Label(text="PAGAMENTO PIX", font_size='18sp', bold=True, size_hint_y=None, height=dp(30)))
        layout_p.add_widget(Label(text="Código PIX (Copia e Cola):", font_size='12sp', color=(0.7,0.7,0.7,1), size_hint_y=None, height=dp(20)))

        lbl_cod = Label(
            text=f"[color=#00FFCC]{codigo}[/color]",
            markup=True, halign='center', valign='middle', font_size='10sp',
            size_hint=(1, 1)
        )
        lbl_cod.bind(width=lambda s, w: setattr(s, 'text_size', (w, None)))
        layout_p.add_widget(lbl_cod)

        btns = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(45))
        
        b_copy = MDRectangleFlatButton(text="COPIAR", text_color=(1,1,1,1), line_color=(0.4,0.4,0.4,1), size_hint_x=0.33)
        b_copy.bind(on_release=lambda x: self.copiar_codigo(codigo))
        
        b_verificar = MDFillRoundFlatButton(text="VERIFICAR", md_bg_color=(0, 0.7, 0, 1), size_hint_x=0.33)
        b_verificar.bind(on_release=lambda x: self.verificar_pago(pay_id, qtd))

        b_cancelar = MDRectangleFlatButton(text="SAIR", text_color=(1,0,0,1), line_color=(1,0,0,1), size_hint_x=0.33)
        b_cancelar.bind(on_release=lambda x: self.popup_pix.dismiss())
        
        btns.add_widget(b_copy); btns.add_widget(b_verificar); btns.add_widget(b_cancelar)
        layout_p.add_widget(btns)

        self.popup_pix = Popup(
            title='', content=layout_p, size_hint=(0.95, 0.6), 
            auto_dismiss=True, background_color=[0,0,0,0], separator_height=0
        )
        self.popup_pix.open()

    def update_bg_pop(self, instance, value):
        self.bg_pop.pos = instance.pos
        self.bg_pop.size = instance.size

    def copiar_codigo(self, codigo):
        Clipboard.copy(codigo)
        MDDialog(title="Copiado", text="Código PIX copiado para a área de transferência!").open()

    def verificar_pago(self, pay_id, qtd):
        def check():
            url = f"https://api.mercadopago.com/v1/payments/{pay_id}"
            headers = {"Authorization": f"Bearer {config_mp.MP_ACCESS_TOKEN}"}
            try:
                res = requests.get(url, headers=headers, timeout=10)
                if res.status_code == 200 and res.json().get("status") == "approved":
                    Clock.schedule_once(lambda dt: self.finalizar_venda_sucesso(qtd))
                else:
                    Clock.schedule_once(lambda dt: MDDialog(title="Aguardando", text="Pagamento ainda não detectado.").open())
            except: pass
        threading.Thread(target=check, daemon=True).start()

    def finalizar_venda_sucesso(self, qtd_add):
        try:
            # Refresh Token para garantir autorização
            user_ref = auth.refresh(auth.current_user['refreshToken'])
            uid = user_ref['userId']
            id_token = user_ref['idToken']
            
            res = db.child("usuarios").child(uid).get(id_token).val()
            atual = 0
            if res:
                if isinstance(res, dict): atual = res.get("creditos", 0)
                elif isinstance(res, int): atual = res
            
            # Atualiza no Firebase enviando o Token
            db.child("usuarios").child(uid).update({"creditos": atual + int(qtd_add)}, id_token)
            
            if self.popup_pix: self.popup_pix.dismiss() 
            
            MDDialog(title="Sucesso!", text=f"Recarga concluída! {qtd_add} créditos adicionados.").open()
            
            # Força atualização do saldo na tela principal
            self.manager.get_screen('principal').atualizar_saldo_ui()
            self.manager.current = 'principal'
        except Exception as e:
            print(f"Erro na finalização: {e}")
