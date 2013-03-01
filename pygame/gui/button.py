
import ui.window
import ui.label

class Button(ui.window.Window):
	
	def __init__(self, parent, **kwargs):
		ui.window.Window.__init__(self, parent, **kwargs)
		
		self.label = ui.label.Label(self, **kwargs)
		self.label.background = ui.window.background_colour((0xFF, 0, 0))
		self.label.border_width = 0
	
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
