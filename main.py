import copy
import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.core.window import Window

# Spielfeld-Dimensionen
REIHEN = 6
SPALTEN = 7

LEER = 0
SPIELER = 1
KI = 2

class SpielfeldWidget(GridLayout):
    def __init__(self, spiel_logik, **kwargs):
        super().__init__(**kwargs)
        self.cols = SPALTEN
        self.rows = REIHEN
        self.spiel = spiel_logik
        self.buttons = []
        
        # Erzeuge das Raster aus Buttons für die Touch-Eingabe
        for r in range(REIHEN):
            reihe_buttons = []
            for c in range(SPALTEN):
                # Jeder Button repraesentiert eine Zelle
                btn = Button(background_color=(0, 0, 0, 0)) # Transparent, wir zeichnen selbst
                btn.bind(on_press=self.spalte_geklickt)
                btn.spalte = c # Speichere die Spaltennummer im Button
                self.add_widget(btn)
                reihe_buttons.append(btn)
            self.buttons.append(reihe_buttons)
            
        # Zeichne das 3D-Spielfeld initiale
        self.bind(pos=self.zeichne_brett, size=self.zeichne_brett)

    def spalte_geklickt(self, instance):
        if self.spiel.aktueller_spieler == SPIELER and self.spiel.spiel_aktiv:
            self.spiel.spieler_zug(instance.spalte)

    def zeichne_brett(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # 1. Das blaue Plastik-Spielfeld als Hintergrund
            Color(0.11, 0.22, 0.54, 1) # #1E3A8A Dunkelblau
            Rectangle(pos=self.pos, size=self.size)
            
            # Berechne die Groesse jeder einzelnen Zelle dynamisch
            zell_breite = self.width / SPALTEN
            zell_hoehe = self.height / REIHEN
            
            # 2. Zeichne die Löcher und die Chips hinein
            for r in range(REIHEN):
                for c in range(SPALTEN):
                    # Kivy zeichnet von unten links nach oben rechts, 
                    # daher spiegeln wir die Reihe visuell für die korrekte Schwerkraft
                    visuelle_reihe = REIHEN - 1 - r
                    wert = self.spiel.brett[visuelle_reihe][c]
                    
                    x = self.x + c * zell_breite + (zell_breite * 0.1)
                    y = self.y + r * zell_hoehe + (zell_hoehe * 0.1)
                    w = zell_breite * 0.8
                    h = zell_hoehe * 0.8
                    
                    # 3D Tiefen-Schatten des Lochs
                    Color(0, 0, 0, 0.4)
                    Ellipse(pos=(x + 2, y - 2), size=(w, h))
                    
                    if wert == LEER:
                        Color(0.06, 0.09, 0.15, 1) # Dunkler Hintergrund im leeren Loch
                        Ellipse(pos=(x, y), size=(w, h))
                    elif wert == SPIELER:
                        # Roter Spieler-Chip mit 3D Glanzkante
                        Color(0.6, 0.1, 0.1, 1) # Schatten
                        Ellipse(pos=(x, y), size=(w, h))
                        Color(0.93, 0.26, 0.26, 1) # Hauptfarbe
                        Ellipse(pos=(x, y + h*0.05), size=(w, h*0.95))
                        Color(0.98, 0.64, 0.64, 1) # Lichtpunkt
                        Ellipse(pos=(x + w*0.2, y + h*0.5), size=(w*0.2, h*0.2))
                    elif wert == KI:
                        # Gelber KI-Chip mit 3D Glanzkante
                        Color(0.57, 0.25, 0.05, 1) # Schatten
                        Ellipse(pos=(x, y), size=(w, h))
                        Color(0.98, 0.74, 0.14, 1) # Hauptfarbe
                        Ellipse(pos=(x, y + h*0.05), size=(w, h*0.95))
                        Color(0.99, 0.94, 0.54, 1) # Lichtpunkt
                        Ellipse(pos=(x + w*0.2, y + h*0.5), size=(w*0.2, h*0.2))

class VierGewinntApp(App):
    def build(self):
        Window.clearcolor = (0.06, 0.09, 0.15, 1) # Dark Mode Hintergrund
        
        self.brett = [[LEER for _ in range(SPALTEN)] for _ in range(REIHEN)]
        self.aktueller_spieler = SPIELER
        self.spiel_aktiv = True
        self.score_spieler = 0
        self.score_ki = 0
        
        # Hauptlayout (Vertikal)
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Top-Bar für den Punktestand
        self.score_label = Label(
            text=f"Spieler: {self.score_spieler}  |  KI: {self.score_ki}",
            font_size='20sp', bold=True, size_hint_y=0.1
        )
        self.main_layout.add_widget(self.score_label)
        
        # Status-Anzeige
        self.status_label = Label(
            text="Du bist am Zug!", font_size='16sp', 
            color=(0.93, 0.26, 0.26, 1), size_hint_y=0.08
        )
        self.main_layout.add_widget(self.status_label)
        
        # Das Spielfeld-Raster hinzufügen
        self.spielfeld_view = SpielfeldWidget(self, size_hint_y=0.72)
        self.main_layout.add_widget(self.spielfeld_view)
        
        # Kontroll-Leiste unten (Reset Button)
        bot_bar = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)
        reset_btn = Button(text="Neustart", background_color=(0.06, 0.72, 0.5, 1), font_size='18sp', bold=True)
        reset_btn.bind(on_press=self.reset_spiel)
        bot_bar.add_widget(reset_btn)
        
        self.main_layout.add_widget(bot_bar)
        return self.main_layout

    def spieler_zug(self, spalte):
        reihe = self.get_freie_reihe(self.brett, spalte)
        if reihe is not None:
            self.brett[reihe][spalte] = SPIELER
            self.spielfeld_view.zeichne_brett()
            
            if self.pruefe_sieg(self.brett, SPIELER):
                self.score_spieler += 1
                self.beende_spiel("Du hast gewonnen!")
                return
            elif self.pruefe_unentschieden(self.brett):
                self.beende_spiel("Unentschieden!")
                return
                
            self.aktueller_spieler = KI
            self.status_label.text = "KI überlegt..."
            self.status_label.color = (0.98, 0.74, 0.14, 1)
            
            # Simuliere eine kurze Bedenkzeit für die KI
            from kivy.clock import Clock
            Clock.schedule_once(self.ki_zug, 0.5)

    def ki_zug(self, dt):
        gueltige_zuege = [c for c in range(SPALTEN) if self.brett[0][c] == LEER]
        if not gueltige_zuege or not self.spiel_aktiv:
            return

        # Einfache Minimax-Logik (Tiefe 2) für flüssige Mobile-Performance
        spalte = self.bester_zug_ki(gueltige_zuege)
        reihe = self.get_freie_reihe(self.brett, spalte)
        
        if reihe is not None:
            self.brett[reihe][spalte] = KI
            self.spielfeld_view.zeichne_brett()
            
            if self.pruefe_sieg(self.brett, KI):
                self.score_ki += 1
                self.beende_spiel("Die KI gewinnt!")
                return
            elif self.pruefe_unentschieden(self.brett):
                self.beende_spiel("Unentschieden!")
                return
                
        self.aktueller_spieler = SPIELER
        self.status_label.text = "Du bist am Zug!"
        self.status_label.color = (0.93, 0.26, 0.26, 1)

    def bester_zug_ki(self, gueltige_zuege):
        # Bevorzugt sofortige Gewinne oder blockiert den Spieler
        for c in gueltige_zuege:
            temp = copy.deepcopy(self.brett)
            r = self.get_freie_reihe(temp, c)
            temp[r][c] = KI
            if self.pruefe_sieg(temp, KI): return c
            
        for c in gueltige_zuege:
            temp = copy.deepcopy(self.brett)
            r = self.get_freie_reihe(temp, c)
            temp[r][c] = SPIELER
            if self.pruefe_sieg(temp, SPIELER): return c
            
        return random.choice(gueltige_zuege)

    def get_freie_reihe(self, brett, spalte):
        for r in range(REIHEN-1, -1, -1):
            if brett[r][spalte] == LEER:
                return r
        return None

    def pruefe_sieg(self, brett, spieler):
        for r in range(REIHEN):
            for c in range(SPALTEN - 3):
                if all(brett[r][c+i] == spieler for i in range(4)): return True
        for r in range(REIHEN - 3):
            for c in range(SPALTEN):
                if all(brett[r+i][c] == spieler for i in range(4)): return True
        for r in range(3, REIHEN):
            for c in range(SPALTEN - 3):
                if all(brett[r-i][c+i] == spieler for i in range(4)): return True
        for r in range(REIHEN - 3):
            for c in range(SPALTEN - 3):
                if all(brett[r+i][c+i] == spieler for i in range(4)): return True
        return False

    def pruefe_unentschieden(self, brett):
        return all(brett[0][c] != LEER for c in range(SPALTEN))

    def beende_spiel(self, nachricht):
        self.spiel_aktiv = False
        self.status_label.text = nachricht
        self.status_label.color = (1, 1, 1, 1)
        self.score_label.text = f"Spieler: {self.score_spieler}  |  KI: {self.score_ki}"

    def reset_spiel(self, instance):
        self.brett = [[LEER for _ in range(SPALTEN)] for _ in range(REIHEN)]
        self.aktueller_spieler = SPIELER
        self.spiel_aktiv = True
        self.status_label.text = "Du bist am Zug!"
        self.status_label.color = (0.93, 0.26, 0.26, 1)
        self.spielfeld_view.zeichne_brett()

if __name__ == '__main__':
    VierGewinntApp().run()
