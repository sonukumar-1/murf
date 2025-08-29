import asyncio
import pygame
import sys
import pygame.gfxdraw
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Agent with Configurable API Keys")

# Colors
BACKGROUND = (22, 26, 38)        # Deep navy blue
SIDEBAR_BG = (30, 36, 54)        # Slightly lighter navy
ACCENT = (86, 207, 225)          # Bright cyan-blue
TEXT_PRIMARY = (232, 240, 253)   # Very light blue (almost white)
TEXT_SECONDARY = (152, 169, 206) # Medium blue-gray
INPUT_BG = (30, 36, 54, 220)     # Semi-transparent sidebar color
BUTTON_BG = (86, 207, 225, 40)   # Semi-transparent accent color
BUTTON_HOVER = (86, 207, 225, 120) # More opaque accent on hover
CHAT_USER_BG = (30, 36, 54, 220) # Semi-transparent sidebar color
CHAT_AI_BG = (86, 207, 225, 40)  # Semi-transparent accent color

# Fonts
font_large = pygame.font.SysFont("Segoe UI", 28)
font_medium = pygame.font.SysFont("Segoe UI", 20)
font_small = pygame.font.SysFont("Segoe UI", 16)

class InputBox:
    def __init__(self, x, y, w, h, text='', placeholder='', is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = TEXT_SECONDARY
        self.text = text
        self.placeholder = placeholder
        self.is_password = is_password
        self.txt_surface = font_medium.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = TEXT_PRIMARY if self.active else TEXT_SECONDARY
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = font_medium.render(
                    '*' * len(self.text) if self.is_password else self.text, 
                    True, self.color
                )
        return False

    def draw(self, screen):
        # Draw the input box background
        pygame.draw.rect(screen, INPUT_BG, self.rect, border_radius=5)
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=5)
        
        # Draw text or placeholder
        if self.text:
            screen.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + 10))
        elif not self.active:
            placeholder_surf = font_medium.render(self.placeholder, True, TEXT_SECONDARY)
            screen.blit(placeholder_surf, (self.rect.x + 10, self.rect.y + 10))

class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = BUTTON_BG
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            self.color = BUTTON_HOVER if self.is_hovered else BUTTON_BG
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

    def draw(self, screen):
        # Draw button background
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
        pygame.draw.rect(screen, ACCENT, self.rect, 2, border_radius=5)
        
        # Draw button text
        text_surf = font_medium.render(self.text, True, ACCENT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class ChatMessage:
    def __init__(self, text, is_user=False):
        self.text = text
        self.is_user = is_user
        self.lines = []
        self.render_text()

    def render_text(self):
        max_width = 400
        words = self.text.split(' ')
        current_line = []
        current_width = 0

        for word in words:
            word_surface = font_small.render(word, True, TEXT_PRIMARY)
            word_width = word_surface.get_width()
            
            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width + 5  # 5 pixels for space
            else:
                self.lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
        
        if current_line:
            self.lines.append(' '.join(current_line))

    def get_height(self):
        return len(self.lines) * 25 + 20

    def draw(self, screen, x, y):
        bg_color = CHAT_USER_BG if self.is_user else CHAT_AI_BG
        total_height = self.get_height()
        
        # Draw message background
        message_rect = pygame.Rect(x, y, 450, total_height)
        pygame.draw.rect(screen, bg_color, message_rect, border_radius=10)
        
        # Draw text lines
        for i, line in enumerate(self.lines):
            text_surface = font_small.render(line, True, TEXT_PRIMARY)
            screen.blit(text_surface, (x + 10, y + 10 + i * 25))

async def main():
    # Create UI elements
    openai_input = InputBox(30, 150, 260, 40, '', 'OpenAI API Key', True)
    google_input = InputBox(30, 220, 260, 40, '', 'Google API Key', True)
    huggingface_input = InputBox(30, 290, 260, 40, '', 'HuggingFace API Key', True)
    save_button = Button(30, 360, 260, 50, "Save API Keys")

    chat_input = InputBox(350, 640, 500, 40, '', 'Type your message here...')
    send_button = Button(870, 640, 80, 40, "Send")

    # Chat messages
    chat_messages = [
        ChatMessage("Hello! I'm your AI assistant. Please configure your API keys in the sidebar to get started."),
        ChatMessage("You can enter your OpenAI, Google, and HuggingFace keys to enable all functionalities.")
    ]

    # Status indicators
    status_indicators = {
        "OpenAI": False,
        "Google": False,
        "HuggingFace": False
    }

    # Main loop
    clock = pygame.time.Clock()
    running = True

    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle input events
            if openai_input.handle_event(event):
                google_input.active = True
                openai_input.active = False
                google_input.color = TEXT_PRIMARY
                openai_input.color = TEXT_SECONDARY
            
            if google_input.handle_event(event):
                huggingface_input.active = True
                google_input.active = False
                huggingface_input.color = TEXT_PRIMARY
                google_input.color = TEXT_SECONDARY
                
            if huggingface_input.handle_event(event):
                huggingface_input.active = False
                huggingface_input.color = TEXT_SECONDARY
            
            if chat_input.handle_event(event):
                if chat_input.text.strip():
                    chat_messages.append(ChatMessage(chat_input.text, True))
                    chat_input.text = ''
                    chat_input.txt_surface = font_medium.render('', True, TEXT_PRIMARY)
            
            if save_button.handle_event(event):
                if openai_input.text:
                    status_indicators["OpenAI"] = True
                if google_input.text:
                    status_indicators["Google"] = True
                if huggingface_input.text:
                    status_indicators["HuggingFace"] = True
                
                # Add confirmation message
                chat_messages.append(ChatMessage("API keys have been configured successfully!"))
            
            if send_button.handle_event(event):
                if chat_input.text.strip():
                    chat_messages.append(ChatMessage(chat_input.text, True))
                    chat_input.text = ''
                    chat_input.txt_surface = font_medium.render('', True, TEXT_PRIMARY)
        
        # Draw UI
        screen.fill(BACKGROUND)
        
        # Draw sidebar
        pygame.draw.rect(screen, SIDEBAR_BG, (0, 0, 320, SCREEN_HEIGHT))
        
        # Draw title
        title = font_large.render("AI Agent Config", True, ACCENT)
        screen.blit(title, (30, 30))
        
        # Draw section headers
        config_title = font_medium.render("API Keys Configuration", True, TEXT_PRIMARY)
        screen.blit(config_title, (30, 100))
        
        # Draw input boxes
        openai_input.draw(screen)
        google_input.draw(screen)
        huggingface_input.draw(screen)
        
        # Draw save button
        save_button.draw(screen)
        
        # Draw status indicators
        status_title = font_medium.render("Connection Status", True, TEXT_PRIMARY)
        screen.blit(status_title, (30, 430))
        
        y_offset = 470
        for service, status in status_indicators.items():
            pygame.draw.circle(screen, ACCENT if status else TEXT_SECONDARY, (30, y_offset + 10), 10)
            status_text = font_small.render(service, True, TEXT_PRIMARY)
            screen.blit(status_text, (50, y_offset))
            y_offset += 40
        
        # Draw chat area
        chat_title = font_large.render("AI Assistant", True, ACCENT)
        screen.blit(chat_title, (370, 30))
        
        # Draw chat messages
        y_pos = 80
        for message in chat_messages:
            if message.is_user:
                message.draw(screen, SCREEN_WIDTH - 470, y_pos)
            else:
                message.draw(screen, 350, y_pos)
            y_pos += message.get_height() + 10
        
        # Draw input area
        chat_input.draw(screen)
        send_button.draw(screen)
        
        # Draw horizontal line above input
        pygame.draw.line(screen, SIDEBAR_BG, (350, 620), (950, 620), 2)
        
        pygame.display.flip()
        clock.tick(30)
        await asyncio.sleep(0)  # Very important for pygbag/web deployment
        
    pygame.quit()
    sys.exit()

# This is the entry point for pygbag
if __name__ == "__main__":
    asyncio.run(main())