
import pygame.gui.window

class Label(pygame.gui.window.Window):
	
	def __init__(self, parent, **kwargs):
		pygame.gui.window.Window.__init__(self, parent, **kwargs)
		
		self.text = unicode(kwargs.get("text", ""))
	
	@property
	def requested_width(self):
		return int(self.font.size(self.text)[0] + (2 * self.padding) + (2 * self.border_width))
	
	@property
	def requested_height(self):
		return int(self.font.size(self.text)[1] + (2 * self.padding) + (2 * self.border_width))
	
	def draw(self):
		return self.font.render(self.text, self.font_aa, self.font_colour)
