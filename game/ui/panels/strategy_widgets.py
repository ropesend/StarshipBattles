import pygame
import math

from game.core.protocols import is_star
from game.ui.fonts import get_font
from game.ui.colors import (
    TEXT_MUTED, TEXT_ITEM, TEXT_DIM, WHITE,
    BORDER_DARK,
    SPECTRUM_GAMMA, SPECTRUM_XRAY, SPECTRUM_UV, SPECTRUM_BLUE, SPECTRUM_GREEN,
    SPECTRUM_RED, SPECTRUM_INFRARED, SPECTRUM_MICROWAVE, SPECTRUM_RADIO,
    GAS_N2, GAS_O2, GAS_CO2, GAS_H2O, GAS_CH4, GAS_H2, GAS_HE, GAS_AR, GAS_SO2,
    GAS_UNKNOWN,
)

class DataGraph:
    """Base class for data visualization widgets."""
    def __init__(self, width, height, bg_color=(20, 24, 30)):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.surface = pygame.Surface((width, height))

    def clear(self):
        self.surface.fill(self.bg_color)
        pygame.draw.rect(self.surface, BORDER_DARK, (0, 0, self.width, self.height), 1)

class SpectrumGraph(DataGraph):
    """Visualizes Star Energy Spectrum."""
    
    BANDS = [
        ('gamma_ray', SPECTRUM_GAMMA, "Gamma"),
        ('xray', SPECTRUM_XRAY, "X-Ray"),
        ('ultraviolet', SPECTRUM_UV, "UV"),
        ('blue', SPECTRUM_BLUE, "Blue"),
        ('green', SPECTRUM_GREEN, "Green"),
        ('red', SPECTRUM_RED, "Red"),
        ('infrared', SPECTRUM_INFRARED, "IR"),
        ('microwave', SPECTRUM_MICROWAVE, "Micro"),
        ('radio', SPECTRUM_RADIO, "Radio")
    ]
    
    def render(self, star, vertical=False):
        self.clear()
        if not is_star(star):
            return self.surface
            
        s = star.spectrum
        
        # Extract values
        values = []
        max_val = 0.0
        for attr, color, label in self.BANDS:
            val = getattr(s, attr, 0.0)
            values.append(val)
            if val > max_val:
                max_val = val
        
        if max_val <= 0:
            return self.surface
            
        # Draw Bars
        bar_width = (self.width - 20) / len(self.BANDS)
        margin_x = 10
        bottom_y = self.height - 10 
        max_h = self.height - 20 
        
        font = get_font(8)
        
        # Logarithmic Scale Calculation
        # Use log10(value + 1) to handle zeros and scaling
        # Max log value based on max_val
        log_max = math.log10(max_val + 1) if max_val > 0 else 1.0
        
        for i, val in enumerate(values):
            attr, color, label = self.BANDS[i]
            
            # Log Sclae
            log_val = math.log10(val + 1)
            normalized = log_val / log_max if log_max > 0 else 0
            
            bar_h = int(normalized * max_h)
            
            # Ensure at least 1px if non-zero
            if val > 0 and bar_h < 1: bar_h = 1
            
            x = margin_x + i * bar_width
            y = bottom_y - bar_h
            
            rect = pygame.Rect(x + 2, y, bar_width - 4, bar_h)
            pygame.draw.rect(self.surface, color, rect)
            
            # Label
            lbl = font.render(label, True, TEXT_MUTED)
            
            if vertical:
                 # Rotate +90 (Reads Bottom-to-Top)
                 # On a vertically rotated graph, this becomes Left-to-Right
                 lbl = pygame.transform.rotate(lbl, 90)
                 # Position: Centered on bar width, at bottom
                 lbl_rect = lbl.get_rect(center=(x + bar_width/2, self.height - 10))
            else:
                 lbl_rect = lbl.get_rect(center=(x + bar_width/2, self.height - 5))
                 
            self.surface.blit(lbl, lbl_rect)
            
        return self.surface

class AtmosphereGraph(DataGraph):
    """Visualizes Planet Atmosphere Composition."""
    
    GAS_COLORS = {
        'N2': GAS_N2,
        'O2': GAS_O2,
        'CO2': GAS_CO2,
        'H2O': GAS_H2O,
        'CH4': GAS_CH4,
        'H2': GAS_H2,
        'He': GAS_HE,
        'Ar': GAS_AR,
        'SO2': GAS_SO2,
    }
    
    def render(self, planet, vertical=False):
        self.clear()
        # atmosphere is always present via IPlanet protocol
        if not planet.atmosphere:
            font = get_font(12)
            txt = font.render("Trace / None", True, TEXT_DIM)
            if vertical: txt = pygame.transform.rotate(txt, 90)
            self.surface.blit(txt, (10, self.height/2))
            return self.surface
            
        # Sort gases by pressure
        items = sorted(planet.atmosphere.items(), key=lambda x: x[1], reverse=True)
        
        # Take Top 6
        top_items = items[:6]
        
        total_p = sum(p for g, p in items)
        max_p = top_items[0][1] if top_items else 1.0
        
        # Layout: Horizontal Bars? Or Vertical?
        # Vertical fits "Graph" theme.
        
        bar_width = (self.width - 20) / max(1, len(top_items))
        margin_x = 10
        bottom_y = self.height - 10
        max_h = self.height - 20 
        
        font = get_font(8)

        for i, (gas, pressure) in enumerate(top_items):
            # Normalize to Max (Relative composition view)
            ratio = pressure / max_p
            bar_h = int(ratio * max_h)
            
            x = margin_x + i * bar_width
            y = bottom_y - bar_h
            
            color = self.GAS_COLORS.get(gas, GAS_UNKNOWN)
            
            rect = pygame.Rect(x + 4, y, bar_width - 8, bar_h)
            pygame.draw.rect(self.surface, color, rect)
            
            # Label (Gas Name)
            lbl = font.render(gas, True, TEXT_ITEM)
            if vertical: lbl = pygame.transform.rotate(lbl, 90)
            
            if vertical:
                 lbl_rect = lbl.get_rect(center=(x + bar_width/2, self.height - 10))
            else:
                 lbl_rect = lbl.get_rect(center=(x + bar_width/2, self.height - 5))
            self.surface.blit(lbl, lbl_rect)
            
            # Value (Abbrev)
            # if > 1000 Pa -> kPa?
            val_str = f"{int(pressure)}Pa"
            if pressure > 10000:
                val_str = f"{pressure/1000:.0f}k"
            elif pressure > 100:
                val_str = f"{int(pressure)}"
                
            val_txt = font.render(val_str, True, TEXT_MUTED)
            if vertical: val_txt = pygame.transform.rotate(val_txt, 90)
            
            val_rect = val_txt.get_rect(center=(x + bar_width/2, y - 8))
            self.surface.blit(val_txt, val_rect)
            
        return self.surface
