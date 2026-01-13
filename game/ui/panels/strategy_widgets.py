import pygame
import math

class DataGraph:
    """Base class for data visualization widgets."""
    def __init__(self, width, height, bg_color=(20, 24, 30)):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.surface = pygame.Surface((width, height))
    
    def clear(self):
        self.surface.fill(self.bg_color)
        pygame.draw.rect(self.surface, (50, 60, 70), (0, 0, self.width, self.height), 1)

class SpectrumGraph(DataGraph):
    """Visualizes Star Energy Spectrum."""
    
    BANDS = [
        ('gamma_ray', (200, 0, 255), "Gamma"),
        ('xray', (148, 0, 211), "X-Ray"),
        ('ultraviolet', (75, 0, 130), "UV"),
        ('blue', (0, 0, 255), "Blue"),
        ('green', (0, 255, 0), "Green"),
        ('red', (255, 0, 0), "Red"),
        ('infrared', (139, 0, 0), "IR"),
        ('microwave', (160, 82, 45), "Micro"),
        ('radio', (128, 128, 128), "Radio")
    ]
    
    def render(self, star, vertical=False):
        self.clear()
        if not hasattr(star, 'spectrum'):
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
        
        font = pygame.font.SysFont("arial", 8) 
        
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
            lbl = font.render(label, True, (150, 150, 150))
            
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
        'N2': (173, 216, 230), # Light Blue
        'O2': (0, 0, 255),     # Blue
        'CO2': (100, 100, 100),# Grey
        'H2O': (0, 0, 139),    # Dark Blue
        'CH4': (255, 165, 0),  # Orange
        'H2': (255, 192, 203), # Pink
        'He': (255, 255, 255), # White
        'Ar': (128, 0, 128),   # Purple
        'SO2': (255, 255, 0)   # Yellow
    }
    
    def render(self, planet, vertical=False):
        self.clear()
        if not hasattr(planet, 'atmosphere') or not planet.atmosphere:
            font = pygame.font.SysFont("arial", 12)
            txt = font.render("Trace / None", True, (100, 100, 100))
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
        
        font = pygame.font.SysFont("arial", 8)
        
        for i, (gas, pressure) in enumerate(top_items):
            # Normalize to Max (Relative composition view)
            ratio = pressure / max_p
            bar_h = int(ratio * max_h)
            
            x = margin_x + i * bar_width
            y = bottom_y - bar_h
            
            color = self.GAS_COLORS.get(gas, (100, 150, 100))
            
            rect = pygame.Rect(x + 4, y, bar_width - 8, bar_h)
            pygame.draw.rect(self.surface, color, rect)
            
            # Label (Gas Name)
            lbl = font.render(gas, True, (200, 200, 200))
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
                
            val_txt = font.render(val_str, True, (150, 150, 150))
            if vertical: val_txt = pygame.transform.rotate(val_txt, 90)
            
            val_rect = val_txt.get_rect(center=(x + bar_width/2, y - 8))
            self.surface.blit(val_txt, val_rect)
            
        return self.surface
