import os
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation
from kivy.metrics import dp

class TelaSplash(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = FloatLayout()
        
        # --- MELHORIA 1: FUNDO INVISÍVEL ---
        # Mudamos o fundo do canvas para PRETO PURO (0,0,0,1)
        # Como o fundo da sua logo é preto, ela vai "mesclar" e ficar invisível
        with layout.canvas.before:
            Color(0, 0, 0, 1) # Preto puro
            self.rect = Rectangle(size=(2000, 4000), pos=(0,0))
            
        # Centralizando o arquivo logo.png
        self.logo = Image(
            source='logo.png', 
            size_hint=(None, None),
            size=(dp(280), dp(280)), # Tamanho imponente
            pos_hint={'center_x': 0.5, 'center_y': 0.52},
            opacity=0 # Começa invisível para o fade-in
        )
        
        layout.add_widget(self.logo)
        self.add_widget(layout)
        
    def on_enter(self):
        # ANIMAÇÃO: Mais rápida e agressiva
        # Fade-in inicial mais veloz (1.0s)
        fade_in = Animation(opacity=1, duration=1.0)
        
        # --- MELHORIA 2: PISCAR MAIS RÁPIDO ---
        # Reduzimos a duração de 2s para 1.0s em cada perna
        pulsa = Animation(size=(dp(310), dp(310)), opacity=0.8, duration=1.0, t='in_out_quad')
        pulsa += Animation(size=(dp(280), dp(280)), opacity=0.3, duration=1.0, t='in_out_quad')
        pulsa.repeat = True
        
        # Inicia a sequência
        fade_in.start(self.logo)
        pulsa.start(self.logo)
        
        # Mantemos os 7 segundos para apreciarem a logo
        Clock.schedule_once(self.ir_para_login, 10)
        
    def ir_para_login(self, dt):
        self.manager.current = 'login'
