
import ui.window

class Label(ui.window.Window):
	
	def __init__(self, parent, **kwargs):
		ui.window.Window.__init__(self, parent, **kwargs)
		
		self.text = unicode(kwargs.get("text", ""))
	
	@property
	def requested_width(self):
		return self.font.size(self.text)[0]
	
	@property
	def requested_height(self):
		return self.font.size(self.text)[1]
	
	def draw(self):
		return self.font.render(self.text, self.font_aa, self.font_colour)
