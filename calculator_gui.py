import cv2
import numpy as np
import math
import time
import random

class CalculatorGUI:
    def __init__(self):
        # Expression handling
        self.expression = ""
        self.current_display = "0"
        self.result = None
        self.memory = 0.0
        self.history = []  # store last few computations
        self.max_history = 5
        self.error_state = False

        # Dynamic layout (will be set based on screen size)
        self.screen_width = 1280
        self.screen_height = 720
        self.button_width = 90
        self.button_height = 70
        self.button_margin = 15
        
        # Animation states
        self.button_animations = {}  # button_name -> animation_frame
        self.particle_system = []    # list of particles for effects
        self.glow_intensity = 0.0
        self.last_pressed_time = 0
        self.press_ripples = []      # ripple effects
        
        # Advanced futuristic theme colors (BGR)
        self.color_bg_main = (15, 15, 25)
        self.color_bg_panel = (25, 25, 40)
        self.color_display_bg = (10, 10, 20)
        self.color_display_glow = (50, 150, 255)
        self.color_button_std = (45, 45, 60)
        self.color_button_op = (0, 100, 255)
        self.color_button_func = (120, 50, 200)
        self.color_button_mem = (0, 150, 180)
        self.color_button_eq = (0, 200, 100)
        self.color_button_warn = (50, 50, 200)
        self.color_text = (255, 255, 255)
        self.color_text_glow = (200, 255, 255)
        self.color_hover = (100, 255, 255)
        self.color_press = (0, 255, 150)
        self.color_particle = (100, 200, 255)

        # Dynamic button layout - will be calculated based on screen size
        self.buttons = []
        self.sci_buttons = []
        
        # Cached hover & press states
        self.hover_button = None
        self.pressed_button = None
        self.hover_intensity = 0.0
        self.press_intensity = 0.0

        # Precompute allowed math names for safe evaluation
        self.allowed_funcs = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,      # natural log (ln)
            'log10': math.log10,  # base 10
            'sqrt': math.sqrt,
            'pi': math.pi,
            'e': math.e,
        }

    def calculate_layout(self, screen_width, screen_height):
        """Calculate dynamic layout based on screen dimensions"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Responsive button sizing
        if screen_width > 1920:  # 4K
            self.button_width, self.button_height = 120, 90
            self.button_margin = 20
        elif screen_width > 1280:  # HD
            self.button_width, self.button_height = 100, 75
            self.button_margin = 18
        else:  # Standard
            self.button_width, self.button_height = 90, 70
            self.button_margin = 15
            
        # Calculate centered positions
        total_width = 4 * self.button_width + 3 * self.button_margin
        sci_width = 2 * self.button_width + self.button_margin
        start_x = (screen_width - total_width - sci_width - 50) // 2
        start_y = screen_height // 4
        
        # Main calculator buttons
        self.buttons = [
            # Row 1
            ("C", start_x, start_y, self.button_width, self.button_height),
            ("±", start_x + (self.button_width + self.button_margin), start_y, self.button_width, self.button_height),
            ("÷", start_x + 2*(self.button_width + self.button_margin), start_y, self.button_width, self.button_height),
            ("×", start_x + 3*(self.button_width + self.button_margin), start_y, self.button_width, self.button_height),
            # Row 2
            ("7", start_x, start_y + (self.button_height + self.button_margin), self.button_width, self.button_height),
            ("8", start_x + (self.button_width + self.button_margin), start_y + (self.button_height + self.button_margin), self.button_width, self.button_height),
            ("9", start_x + 2*(self.button_width + self.button_margin), start_y + (self.button_height + self.button_margin), self.button_width, self.button_height),
            ("-", start_x + 3*(self.button_width + self.button_margin), start_y + (self.button_height + self.button_margin), self.button_width, self.button_height),
            # Row 3
            ("4", start_x, start_y + 2*(self.button_height + self.button_margin), self.button_width, self.button_height),
            ("5", start_x + (self.button_width + self.button_margin), start_y + 2*(self.button_height + self.button_margin), self.button_width, self.button_height),
            ("6", start_x + 2*(self.button_width + self.button_margin), start_y + 2*(self.button_height + self.button_margin), self.button_width, self.button_height),
            ("+", start_x + 3*(self.button_width + self.button_margin), start_y + 2*(self.button_height + self.button_margin), self.button_width, self.button_height),
            # Row 4
            ("1", start_x, start_y + 3*(self.button_height + self.button_margin), self.button_width, self.button_height),
            ("2", start_x + (self.button_width + self.button_margin), start_y + 3*(self.button_height + self.button_margin), self.button_width, self.button_height),
            ("3", start_x + 2*(self.button_width + self.button_margin), start_y + 3*(self.button_height + self.button_margin), self.button_width, self.button_height),
            ("=", start_x + 3*(self.button_width + self.button_margin), start_y + 3*(self.button_height + self.button_margin), self.button_width, 2*self.button_height + self.button_margin),
            # Row 5
            ("0", start_x, start_y + 4*(self.button_height + self.button_margin), 2*self.button_width + self.button_margin, self.button_height),
            (".", start_x + 2*(self.button_width + self.button_margin), start_y + 4*(self.button_height + self.button_margin), self.button_width, self.button_height),
            ("⌫", start_x, start_y + 5*(self.button_height + self.button_margin), self.button_width, self.button_height)
        ]
        
        # Scientific panel (right side)
        sci_x = start_x + total_width + 50
        self.sci_buttons = [
            ("sin", sci_x, start_y, self.button_width, self.button_height//2 + 5),
            ("cos", sci_x, start_y + self.button_height//2 + 10, self.button_width, self.button_height//2 + 5),
            ("tan", sci_x, start_y + self.button_height + self.button_margin, self.button_width, self.button_height//2 + 5),
            ("log", sci_x, start_y + self.button_height + self.button_margin + self.button_height//2 + 10, self.button_width, self.button_height//2 + 5),
            ("ln", sci_x, start_y + 2*(self.button_height + self.button_margin), self.button_width, self.button_height//2 + 5),
            ("√", sci_x, start_y + 2*(self.button_height + self.button_margin) + self.button_height//2 + 10, self.button_width, self.button_height//2 + 5),
            
            ("x²", sci_x + self.button_width + self.button_margin, start_y, self.button_width, self.button_height//2 + 5),
            ("1/x", sci_x + self.button_width + self.button_margin, start_y + self.button_height//2 + 10, self.button_width, self.button_height//2 + 5),
            ("(", sci_x + self.button_width + self.button_margin, start_y + self.button_height + self.button_margin, self.button_width, self.button_height//2 + 5),
            (")", sci_x + self.button_width + self.button_margin, start_y + self.button_height + self.button_margin + self.button_height//2 + 10, self.button_width, self.button_height//2 + 5),
            ("π", sci_x + self.button_width + self.button_margin, start_y + 2*(self.button_height + self.button_margin), self.button_width, self.button_height//2 + 5),
            ("e", sci_x + self.button_width + self.button_margin, start_y + 2*(self.button_height + self.button_margin) + self.button_height//2 + 10, self.button_width, self.button_height//2 + 5),
            
            # Memory functions
            ("M+", sci_x, start_y + 3*(self.button_height + self.button_margin), self.button_width, self.button_height),
            ("M-", sci_x + self.button_width + self.button_margin, start_y + 3*(self.button_height + self.button_margin), self.button_width, self.button_height),
            ("MR", sci_x, start_y + 4*(self.button_height + self.button_margin), self.button_width, self.button_height),
            ("MC", sci_x + self.button_width + self.button_margin, start_y + 4*(self.button_height + self.button_margin), self.button_width, self.button_height)
        ]
        
        # Combine all buttons for unified processing
        self.buttons.extend(self.sci_buttons)

    def add_particle(self, x, y, color=None):
        """Add a particle effect at the given position"""
        if color is None:
            color = self.color_particle
        
        for _ in range(random.randint(3, 8)):
            particle = {
                'x': x + random.randint(-10, 10),
                'y': y + random.randint(-10, 10),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-3, -0.5),
                'life': 1.0,
                'color': color,
                'size': random.randint(2, 5)
            }
            self.particle_system.append(particle)
    
    def add_ripple(self, x, y):
        """Add ripple effect at button press"""
        ripple = {
            'x': x,
            'y': y,
            'radius': 0,
            'max_radius': 60,
            'life': 1.0,
            'color': self.color_press
        }
        self.press_ripples.append(ripple)

    def update_animations(self, dt=0.016):  # ~60fps
        """Update all animation states"""
        current_time = time.time()
        
        # Update hover/press intensities
        if self.hover_button:
            self.hover_intensity = min(1.0, self.hover_intensity + dt * 4)
        else:
            self.hover_intensity = max(0.0, self.hover_intensity - dt * 3)
            
        if self.pressed_button:
            self.press_intensity = min(1.0, self.press_intensity + dt * 8)
        else:
            self.press_intensity = max(0.0, self.press_intensity - dt * 4)
        
        # Update glow intensity (breathing effect)
        self.glow_intensity = 0.5 + 0.3 * math.sin(current_time * 2)
        
        # Update particles
        for particle in self.particle_system[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # gravity
            particle['life'] -= dt * 2
            if particle['life'] <= 0:
                self.particle_system.remove(particle)
        
        # Update ripples
        for ripple in self.press_ripples[:]:
            ripple['radius'] += dt * 120
            ripple['life'] -= dt * 2
            if ripple['life'] <= 0 or ripple['radius'] > ripple['max_radius']:
                self.press_ripples.remove(ripple)

    # ---------------- Drawing Utilities ----------------
        
    def draw_buttons(self, img):
        """Draw calculator UI with advanced futuristic effects and animations"""
        # Update animations
        self.update_animations()
        
        # Create overlay for alpha blending effects
        overlay = img.copy()
        effect_layer = np.zeros_like(img)
        
        # Fill background with gradient
        self._draw_background_gradient(overlay)
        
        # Calculate display area dimensions
        display_x, display_y = 50, 50
        display_w = self.screen_width - 100
        display_h = 80
        
        # Draw holographic display panel
        self._draw_holographic_display(overlay, display_x, display_y, display_w, display_h)
        
        # Draw history panel
        self._draw_history_panel(overlay, display_x, display_y + display_h + 20)
        
        # Draw all buttons with effects
        for button_text, x, y, w, h in self.buttons:
            self._draw_advanced_button(overlay, effect_layer, button_text, x, y, w, h)
        
        # Draw particle effects
        self._draw_particles(overlay)
        
        # Draw ripple effects
        self._draw_ripples(overlay)
        
        # Apply glow effects
        self._apply_glow_effects(overlay, effect_layer)
        
        # Blend everything together
        cv2.addWeighted(overlay, 0.95, img, 0.05, 0, img)
        return img

    def _draw_background_gradient(self, img):
        """Draw animated background gradient"""
        h, w = img.shape[:2]
        for i in range(h):
            intensity = int(15 + 10 * math.sin(i * 0.01 + time.time()))
            color = (intensity, intensity, max(25, intensity + 10))
            cv2.line(img, (0, i), (w, i), color, 1)

    def _draw_holographic_display(self, img, x, y, w, h):
        """Draw the main display with holographic effects"""
        # Background with glow
        glow_size = int(20 * self.glow_intensity)
        cv2.rectangle(img, (x-glow_size, y-glow_size), (x+w+glow_size, y+h+glow_size), 
                     self.color_display_glow, -1)
        
        # Main display background
        cv2.rectangle(img, (x, y), (x+w, y+h), self.color_display_bg, -1)
        
        # Holographic border
        border_colors = [(100, 255, 255), (50, 200, 255), (0, 150, 255)]
        for i, color in enumerate(border_colors):
            cv2.rectangle(img, (x-i-1, y-i-1), (x+w+i+1, y+h+i+1), color, 1)
        
        # Display text with glow
        expr_display = self.expression if self.expression else ("0" if self.result is None else str(self.result))
        if self.error_state:
            expr_display = "⚠ ERROR"
        
        # Limit display length for full screen
        max_chars = max(20, w // 25)
        if len(expr_display) > max_chars:
            expr_display = "..." + expr_display[-(max_chars-3):]
        
        # Text with neon effect
        font_scale = min(2.0, w / 400)
        text_size = cv2.getTextSize(expr_display, cv2.FONT_HERSHEY_DUPLEX, font_scale, 2)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        
        # Glow effect for text
        if not self.error_state:
            cv2.putText(img, expr_display, (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX, 
                       font_scale, self.color_text_glow, 4)
        cv2.putText(img, expr_display, (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX, 
                   font_scale, (0, 0, 255) if self.error_state else self.color_text, 2)

    def _draw_history_panel(self, img, x, y):
        """Draw computation history with fade effect"""
        if not self.history:
            return
            
        panel_h = min(60, len(self.history) * 20)
        cv2.rectangle(img, (x, y), (x + self.screen_width - 100, y + panel_h), 
                     (20, 20, 30), -1)
        
        for idx, item in enumerate(self.history[-3:][::-1]):
            alpha = 1.0 - (idx * 0.3)
            color = tuple(int(c * alpha) for c in (180, 180, 200))
            cv2.putText(img, item[:60], (x + 10, y + 20 + idx * 18), 
                       cv2.FONT_HERSHEY_PLAIN, 1.0, color, 1)

    def _draw_advanced_button(self, overlay, effect_layer, button_text, x, y, w, h):
        """Draw a button with advanced visual effects"""
        # Determine button category and base color
        if button_text in ["+", "-", "×", "÷"]:
            base_color = self.color_button_op
        elif button_text == "=":
            base_color = self.color_button_eq
        elif button_text in ["sin", "cos", "tan", "log", "ln", "√", "x²", "1/x", "(", ")", "π", "e"]:
            base_color = self.color_button_func
        elif button_text in ["M+", "M-", "MR", "MC"]:
            base_color = self.color_button_mem
        elif button_text in ["C", "⌫", "±"]:
            base_color = self.color_button_warn
        else:
            base_color = self.color_button_std
        
        # Animation intensity
        hover_factor = self.hover_intensity if self.hover_button == button_text else 0
        press_factor = self.press_intensity if self.pressed_button == button_text else 0
        
        # Enhanced color with animation
        enhanced_color = tuple(min(255, int(c + hover_factor * 50 + press_factor * 100)) for c in base_color)
        
        # Draw button with rounded corners effect
        self._draw_rounded_button(overlay, x, y, w, h, enhanced_color, hover_factor, press_factor)
        
        # Add glow effects to effect layer
        if hover_factor > 0:
            glow_radius = int(15 * hover_factor)
            cv2.circle(effect_layer, (x + w//2, y + h//2), glow_radius, self.color_hover, -1)
        
        if press_factor > 0:
            press_glow = int(20 * press_factor)
            cv2.circle(effect_layer, (x + w//2, y + h//2), press_glow, self.color_press, -1)
        
        # Button text with scaling animation
        font_scale = 0.7 + (hover_factor * 0.2) + (press_factor * 0.1)
        if len(button_text) > 2:
            font_scale *= 0.8
        elif len(button_text) == 1:
            font_scale *= 1.2
            
        text_size = cv2.getTextSize(button_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        
        # Text with glow
        if hover_factor > 0 or press_factor > 0:
            cv2.putText(overlay, button_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 
                       font_scale, self.color_text_glow, 3)
        cv2.putText(overlay, button_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 
                   font_scale, self.color_text, 2)

    def _draw_rounded_button(self, img, x, y, w, h, color, hover_factor, press_factor):
        """Draw a button with rounded corners and 3D effect"""
        # Main button body
        cv2.rectangle(img, (x, y), (x + w, y + h), color, -1)
        
        # 3D border effect
        highlight = tuple(min(255, int(c * 1.3)) for c in color)
        shadow = tuple(max(0, int(c * 0.7)) for c in color)
        
        # Top and left highlights
        cv2.line(img, (x, y), (x + w, y), highlight, 2)
        cv2.line(img, (x, y), (x, y + h), highlight, 2)
        
        # Bottom and right shadows
        cv2.line(img, (x, y + h), (x + w, y + h), shadow, 2)
        cv2.line(img, (x + w, y), (x + w, y + h), shadow, 2)
        
        # Outer glow border
        border_intensity = int(255 * (hover_factor + press_factor))
        if border_intensity > 0:
            border_color = tuple(min(255, int(c + border_intensity)) for c in (100, 255, 255))
            cv2.rectangle(img, (x-1, y-1), (x + w + 1, y + h + 1), border_color, 2)

    def _draw_particles(self, img):
        """Draw particle effects"""
        for particle in self.particle_system:
            if particle['life'] > 0:
                alpha = particle['life']
                color = tuple(int(c * alpha) for c in particle['color'])
                size = max(1, int(particle['size'] * alpha))
                cv2.circle(img, (int(particle['x']), int(particle['y'])), size, color, -1)

    def _draw_ripples(self, img):
        """Draw ripple effects from button presses"""
        for ripple in self.press_ripples:
            if ripple['life'] > 0:
                alpha = ripple['life']
                color = tuple(int(c * alpha) for c in ripple['color'])
                thickness = max(1, int(3 * alpha))
                cv2.circle(img, (int(ripple['x']), int(ripple['y'])), 
                          int(ripple['radius']), color, thickness)

    def _apply_glow_effects(self, overlay, effect_layer):
        """Apply gaussian blur glow effects"""
        if np.any(effect_layer):
            # Blur the effect layer for glow
            blurred = cv2.GaussianBlur(effect_layer, (21, 21), 0)
            # Blend with main overlay
            cv2.addWeighted(overlay, 1.0, blurred, 0.6, 0, overlay)
    
    def highlight_button(self, button_text, pressed=False):
        """Update highlight states (used externally)."""
        if pressed:
            self.pressed_button = button_text
        else:
            self.hover_button = button_text
    
    def check_button_press(self, finger_pos):
        """Return button under given finger position (id,x,y)."""
        if not finger_pos:
            return None
        x, y = finger_pos[1], finger_pos[2]
        for button_text, bx, by, bw, bh in self.buttons:
            if bx <= x <= bx + bw and by <= y <= by + bh:
                return button_text
        return None

    # ---------------- Expression / Logic Handling ----------------
    
    def process_button_press(self, button):
        """Process a button press for scientific / standard calculator"""
        if button is None:
            return

        # Add visual effects for button press
        button_pos = self.get_button_position(button)
        if button_pos:
            x, y, w, h = button_pos
            self.add_particle(x + w//2, y + h//2)
            self.add_ripple(x + w//2, y + h//2)
        
        self.pressed_button = button
        self.last_pressed_time = time.time()
        
        if self.error_state and button not in ["C", "⌫"]:
            return

        # Rest of the button processing logic remains the same
        if button.isdigit():
            self.expression += button
        elif button == ".":
            if not self.expression or not self.expression[-1] == '.':
                self.expression += '.'
        elif button in ["+", "-", "×", "÷"]:
            if not self.expression and self.result is not None:
                self.expression = str(self.result)
            if self.expression and self.expression[-1] in "+-*/":
                self.expression = self.expression[:-1]
            op_map = {"×": "*", "÷": "/"}
            self.expression += op_map.get(button, button)
        elif button in ["sin", "cos", "tan", "ln", "log", "√", "x²", "1/x", "(", ")", "π", "e"]:
            self._handle_function(button)
        elif button in ["M+", "M-", "MR", "MC"]:
            self._handle_memory(button)
        elif button == "⌫":
            if self.expression:
                self.expression = self.expression[:-1]
            else:
                self.result = None
            self.error_state = False
        elif button == "C":
            self.expression = ""
            self.result = None
            self.error_state = False
        elif button == "±":
            self._toggle_sign()
        elif button == "=":
            self._evaluate_expression()

        self.current_display = self.expression if self.expression else (str(self.result) if self.result is not None else "0")

    def get_button_position(self, button_text):
        """Get the position and dimensions of a button"""
        for text, x, y, w, h in self.buttons:
            if text == button_text:
                return (x, y, w, h)
        return None

    def _handle_function(self, button):
        if button == "sin":
            self.expression += "sin("
        elif button == "cos":
            self.expression += "cos("
        elif button == "tan":
            self.expression += "tan("
        elif button == "ln":
            self.expression += "log("  # natural log
        elif button == "log":
            self.expression += "log10("
        elif button == "√":
            self.expression += "sqrt("
        elif button == "x²":
            # square last token or append '**2'
            self.expression += "**2"
        elif button == "1/x":
            if self.expression:
                self.expression = f"1/({self.expression})"
        elif button == "π":
            self.expression += "pi"
        elif button == "e":
            self.expression += "e"
        elif button == "(":
            self.expression += "("
        elif button == ")":
            self.expression += ")"

    def _handle_memory(self, button):
        value = None
        # Evaluate current expression first (silently) to update value for M+/M-
        try:
            if self.expression:
                value = self._safe_eval(self.expression)
        except Exception:
            value = None
        if value is None and self.result is not None:
            value = self.result

        if button == "M+" and value is not None:
            self.memory += value
        elif button == "M-" and value is not None:
            self.memory -= value
        elif button == "MR":
            # recall memory into expression
            mem_str = ("%f" % self.memory).rstrip('0').rstrip('.')
            self.expression += mem_str
        elif button == "MC":
            self.memory = 0.0

    def _toggle_sign(self):
        if not self.expression:
            return
        # Find last number span
        i = len(self.expression) - 1
        while i >= 0 and (self.expression[i].isdigit() or self.expression[i] == '.'):  # basic numeric detection
            i -= 1
        # expression[i] is non-digit
        number = self.expression[i+1:]
        if not number:
            return
        # Remove old number
        self.expression = self.expression[:i+1]
        # Toggle sign
        if number.startswith("-"):
            number = number[1:]
        else:
            number = f"-{number}"
        self.expression += number

    def _safe_eval(self, expr: str):
        # Security: allow only certain characters
        filtered = ''.join(ch for ch in expr if ch in "0123456789.+-*/()eipalogstqrfx")  # coarse filter
        # Replace accidental unicode (e.g., ensure)**
        code = compile(filtered, "<expr>", "eval")
        return eval(code, {"__builtins__": {}}, self.allowed_funcs)

    def _evaluate_expression(self):
        if not self.expression:
            return
        try:
            # Replace potential unsafe repeated operators already handled
            result = self._safe_eval(self.expression)
            self.result = result
            # Format result nicely
            if isinstance(result, (int, float)):
                if float(result).is_integer():
                    disp = str(int(result))
                else:
                    disp = ("%0.10f" % float(result)).rstrip('0').rstrip('.')
            else:
                disp = str(result)
            # Add to history
            hist_entry = f"{self.expression} = {disp}"[:48]
            self.history.append(hist_entry)
            if len(self.history) > self.max_history:
                self.history = self.history[-self.max_history:]
            # Prepare for chaining
            self.expression = disp
            self.current_display = disp
            self.error_state = False
        except Exception:
            self.error_state = True
            self.current_display = "ERROR"

    
    # Legacy method kept for compatibility (no longer used directly)
    def calculate(self):  # pragma: no cover
        self._evaluate_expression()
