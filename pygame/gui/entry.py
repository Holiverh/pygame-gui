
import pygame
import pygame.gui.window

class Entry(pygame.gui.window.Window):
	
	default_padding = 2
	default_background = (0xff, 0xff, 0xff)
	default_border_width = 1
	default_border_style = pygame.gui.window.Window.BORDER_STYLE_INSET
	
	def __init__(self, parent, **kwargs):
		pygame.gui.window.Window.__init__(self, parent, **kwargs)
		
		self.height = self.font.get_height()
		self.max_length = kwargs.get("max_length", -1)
		self.buffer = u""
		
		self.bind(Entry.CLICK, lambda: self.focus())
		self.bind(Entry.FOCUS, self._on_focus)
		self.bind(Entry.BLUR, self._on_blur)
		self.bind(Entry.KEYDOWN, self._on_keydown)
	
	def _on_focus(self): pass
	def _on_blur(self): pass
	
	def _on_keydown(self, unicode, key, mod):
			
		if key == pygame.K_BACKSPACE:
			self.buffer = self.buffer[:-1]
		else:
			if len(self.buffer) < self.max_length or self.max_length < 0:
				self.buffer += unicode
	
		self.redraw = True
	
	def draw(self):
		text = self.font.render(self.buffer, self.font_aa, self.font_colour, self.background)
		text_rect = text.get_rect()
		self.surface = text
		
		if text_rect.width > self.content_rect.width:
			self.surface_area = pygame.Rect(
							(text_rect.width - self.content_rect.width, 0),
							self.content_rect.size)
		else:
			self.surface_area = None
