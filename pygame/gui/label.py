
import pygame.gui.window

class Label(pygame.gui.window.Window):
	
	default_padding = 2
	
	def __init__(self, parent, **kwargs):
		pygame.gui.window.Window.__init__(self, parent, **kwargs)
		
		self.text = unicode(kwargs.get("text", ""))
		self.bold = kwargs.get("bold", False)
		self.italic = kwargs.get("italic", False)
		self.underline = kwargs.get("underline", False)
	
	@property
	def font(self):
		font = pygame.gui.window.Window.font.fget(self)
		font.set_bold(self.bold)
		font.set_italic(self.italic)
		font.set_underline(self.underline)
		return font
	
	@property
	def requested_width(self):
		return int(self.font.size(self.text)[0] + (2 * self.padding) + (2 * self.border_width))
	
	@property
	def requested_height(self):
		return int(self.font.size(self.text)[1] + (2 * self.padding) + (2 * self.border_width))
	
	def draw(self):
		self.surface = self.font.render(self.text, self.font_aa, self.font_colour)
