
import pygame.gui.window
import pygame.gui.label

class Button(pygame.gui.window.Window):
	
	default_border_width = 1
	default_border_style = pygame.gui.window.Window.BORDER_STYLE_OUTSET
	
	def __init__(self, parent, **kwargs):
		pygame.gui.window.Window.__init__(self, parent, **kwargs)
		
		self.label = pygame.gui.label.Label(self, **{k: v for k, v in 
						kwargs.iteritems() if k not in {"x", "y", "border_width"}})
		self._border_width = self.border_width
		
	@property
	def requested_width(self):
		return self.label.requested_width
	
	@property
	def requested_height(self):
		return self.label.requested_height
