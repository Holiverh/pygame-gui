
import pygame.gui.window
import pygame.gui.label

class Button(pygame.gui.window.Window):
	
	def __init__(self, parent, **kwargs):
		pygame.gui.window.Window.__init__(self, parent, **kwargs)
		
		self.label = pygame.gui.label.Label(self, **{k: v for k, v in 
						kwargs.iteritems() if k not in {"x", "y", "border_width"}})
		self._border_width = self.border_width
		
		self.bind(Button.MOUSEOVER, self._on_mouseover)
		self.bind(Button.MOUSEOUT, self._on_mouseout)
		
	@property
	def requested_width(self):
		return self.label.requested_width
	
	@property
	def requested_height(self):
		return self.label.requested_height
	
	def _on_mouseover(self):
		self.border_width = self._border_width + 2
		
	def _on_mouseout(self):
		self.border_width = self._border_width
