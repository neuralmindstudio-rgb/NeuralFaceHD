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
        
        # FUNDO PRETO PURO
        with layout.canvas.before:
            Color(0, 0, 0, 1) 
            self.rect = Rectangle(size=(3000, 5000), pos=(0,0))
            
        # Centralizando a logo.png
        # IMPORTANTE: A logo.png deve estar na raiz do seu GitHub
        self.logo = Image(
            source='logo.png', 
            size_hint=(None, None),
            size=(dp(280), dp(280)),
            pos_hint={'center_x': 0.5, 'center_y': 0.52},
            opacity=0 
        )
        
        layout.add_widget(self.logo)
        self.add_widget(layout)
        
    def on_enter(self):
        # ANIMAÇÃO DE ENTRADA
        fade_in = Animation(opacity=1, duration=1.2)
        
        # ANIMAÇÃO DE PULSAÇÃO (Efeito Respirar)
        pulsa = Animation(size=(dp(300), dp(300)), opacity=0.7, duration=1.5, t='in_out_quad')
        pulsa += Animation(size=(dp(280), dp(280)), opacity=1.0, duration=1.5, t='in_out_quad')
        pulsa.repeat = True
        
        # Inicia as animações
        fade_in.start(self.logo)
        # Agendamos a pulsação para começar logo após o fade_in
        Clock.schedule_once(lambda dt: pulsa.start(self.logo), 1.2)
        
        # Tempo total de exibição reduzido para 6 segundos (melhor experiência)
        Clock.schedule_once(self.ir_para_login, 6)
        
    def ir_para_login(self, dt):
        # Transição suave para a tela de login
        if self.manager:
            self.manager.current = 'login'
