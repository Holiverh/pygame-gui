
import logging
log = logging.getLogger(__name__)

import types

import pygame

_current_event_id = -1
def generate_event_id():
	global _current_event_id
	_current_event_id += 1
	return _current_event_id

class Window(object):
	
	MOUSEOVER = generate_event_id()
	MOUSEOUT = generate_event_id()
	CLICK = generate_event_id()
	FOCUS = generate_event_id()
	BLUR = generate_event_id()
	KEYDOWN = generate_event_id()
	KEYUP = generate_event_id()
	KEYPRESS = generate_event_id()
	MOUSEDOWN = generate_event_id()
	MOUSEUP = generate_event_id()
	
	BORDER_STYLE_SOLID = 1
	BORDER_STYLE_INSET = 2
	BORDER_STYLE_OUTSET = 3
	
	default_background = (0xd3, 0xd1, 0xcb)
	default_border_colour = (0x48, 0x48, 0x48)
	default_border_width = 0
	default_border_style = BORDER_STYLE_SOLID
	default_padding = 0
	default_font_name = "Tahoma"
	default_font_size = 14
	default_font_colour = (0, 0, 0)
	default_font_aa = True
	
	_font_cache = {}
	
	def __init__(self, parent=None, **kwargs):
		
		self.surface = None
		self.surface_area = None
		self.redraw = True
		# Whether the RootWindow should let the Window redraw it self.
		# Is set to False if the call to draw() completes without
		# errors. Redraw only occurs once the RootWindow needs it to;
		# to force a redraw call draw() directly.
		
		self.parent = parent
		self.children = []
		self.callbacks = {}

		self.reparent(parent)
		
		self._kwargs = kwargs
		
		# Float for relative dimensions/positions, integer for absolute
		self.width = kwargs.get("width", 1.0)
		self.height = kwargs.get("height", 0)
		self.x = kwargs.get("x", 0)
		self.y = kwargs.get("y", 0)
		
		self.background = kwargs.get("background", self.__class__.default_background)
		self.border_width = kwargs.get("border_width", self.__class__.default_border_width)
		self.border_colour = kwargs.get("border_colour", self.__class__.default_border_colour)
		self.border_style = kwargs.get("border_style", self.__class__.default_border_style)
		self.padding = kwargs.get("padding", self.__class__.default_padding)
		self.font_name = kwargs.get("font", self.__class__.default_font_name)
		self.font_colour = kwargs.get("font_colour", self.__class__.default_font_colour)
		self.font_size = kwargs.get("font_size", self.__class__.default_font_size)
		self.font_aa = kwargs.get("font_aa", self.__class__.default_font_aa)
	
	def __setattr__(self, attr, value):
		object.__setattr__(self, "redraw", True)
		object.__setattr__(self, attr, value)
	
	def _print_graph(self, indent=0):
		
		print "{}{} ({}, {}) {}x{}".format(
						" "*indent,
						self.__class__.__name__,
						self.actual_x,
						self.actual_y,
						self.actual_width,
						self.actual_height)
		for child in self.children:
			child._print_graph(indent+2)
	
	@property
	def decendants(self):
		windows = self.children[:]
			
		for child in self.children:
			windows.extend(child.decendants)
		
		return windows
		
	@property
	def leaves(self):
		""" Returns generator for the leaves of the subtree starting at this window. """
		for child in self.children:
			if len(child.children) == 0:
				yield child
			else:
				for leaf in child.leaves:
					yield leaf
	
	@property
	def font(self):
		font_config = (self.font_name, self.font_size)
		
		if font_config not in Window._font_cache:
			try:
				Window._font_cache[font_config] = pygame.font.Font(*font_config)
			except IOError:
				Window._font_cache[font_config] = pygame.font.SysFont(*font_config)
		
		font = Window._font_cache[font_config]
		font.set_bold(False)
		font.set_italic(False)
		font.set_underline(False)
		
		return font
	
	@font.setter
	def font(self, values):
		for value, attr in zip(values,
				["font_name", "font_colour", "font_size", "font_aa"]):
			setattr(self, attr, value)
	
	def reparent(self, new_parent):
		"""
			Removes self from current parent's list of children and
			then adds it self to the new parent's, updating the parent
			attribute as appropriate.
		"""
		if self.parent is not None:
			try:
				self.parent.children.remove(self)
			except ValueError:
				pass
				
		self.parent = new_parent
		if self.parent is not None:
			self.parent.children.append(self)
	
	def focus(self):
		""" Sets the window to recieve keyboard input. """
		
		self.root_window.focus = self
		
	@property
	def root_window(self):
		""" Returns the root window of the tree. """
		
		window = self.parent
		while window.parent is not None:
			window = window.parent
			
		return window
	
	@property
	def requested_width(self):
		if type(self.width) is types.FloatType:
			return int(round(self.width * self.parent.actual_width) + 2 * (self.padding + self.border_width))
		else:
			return int(self.width + 2 * (self.padding + self.border_width))
	
	@property
	def requested_height(self):
		if type(self.height) is types.FloatType:
			return int(round(self.height * self.parent.actual_height) + 2 * (self.padding + self.border_width))
		else:
			return int(self.height + 2 * (self.padding + self.border_width))
	
	@property
	def available_width(self):
		return self.actual_width - 2 * (self.padding + self.border_width)
	
	@property
	def available_height(self):
		return self.actual_height - 2 * (self.padding + self.border_width)
	
	@property
	def actual_height(self):
		return self.requested_height if self.requested_height <= self.parent.available_height else self.parent.available_height
	
	@property
	def actual_width(self):
		return self.requested_width if self.requested_width <= self.parent.available_width else self.parent.available_width
	
	@property
	def requested_x(self):
		if type(self.x) is types.FloatType:
			return int(round(self.x * self.parent.actual_width)) + self.parent.padding + self.parent.border_width
		else:
			return int(self.x) + self.parent.padding + self.parent.border_width
	
	@property
	def requested_y(self):
		if type(self.y) is types.FloatType:
			return int(round(self.y * self.parent.actual_height)) + self.parent.padding + self.parent.border_width
		else:
			return int(self.y) + self.parent.padding + self.parent.border_width
	
	@property
	def actual_x(self):
		return self.parent.actual_x + self.requested_x
	
	@property
	def actual_y(self):
		return self.parent.actual_y + self.requested_y
	
	@property
	def rect(self):
		""" pygame.Rect encompassing the entire window (including padding, etc) """
		return pygame.Rect((self.actual_x, self.actual_y), (self.actual_width, self.actual_height))
	
	@property
	def content_rect(self):
		""" Same as Window.rect but position adjusted for content padding """
		rect = self.rect.move(self.padding + self.border_width, self.padding + self.border_width)
		rect.height -= int(2 * (self.padding + self.border_width))
		rect.width -= int(2 * (self.padding + self.border_width))
		return rect
	
	def centre(self):
		""" Centre window within parent """
		self.x = (self.parent.actual_width / 2) - (self.actual_width / 2)
		self.y = (self.parent.actual_height / 2) - (self.actual_height / 2)
	
	def draw(self):
		"""
			To be implemented by subclasses. Renders the window contents
			to the Window instance's surface. 
		"""
		raise NotImplementedError
	
	def grab_focus(self):
		self.root_window.focus = self
	
	def bind(self, event_type, callback):
		if event_type not in self.callbacks:
			self.callbacks[event_type] = []
		
		self.callbacks[event_type].append(callback)
		
	def trigger(self, event_type, *args):
		if event_type in self.callbacks:
			for callback in self.callbacks[event_type]:
				callback(*args)
	
class RootWindow(Window):
	
	def __init__(self):
		
		self.debug_draw = False
		self._focus = None # Which window has keyboard focus
		
		self._previous_mouse_pos = pygame.mouse.get_pos()
		self._mousedown_win = None
		
		Window.__init__(self, None,
							width=pygame.display.get_surface().get_width(),
							height=pygame.display.get_surface().get_height(),
							background=None,
						)
		
		self.surface = pygame.display.get_surface()
		
	@property
	def focus(self):
		return self._focus
	
	@focus.setter
	def focus(self, window):
		if self._focus is not None:
			self._focus.trigger(Window.BLUR)
			
		self._focus = window
		
		if self._focus is not None:
			self._focus.trigger(Window.FOCUS)
		
	@property
	def requested_width(self):
		return int(self.width)
	
	@property
	def requested_height(self):
		return int(self.height)
	
	@property
	def actual_height(self):
		return self.requested_height
	
	@property
	def actual_width(self):
		return self.requested_width
	
	@property
	def actual_x(self):
		return self.x
	
	@property
	def actual_y(self):
		return self.y
	
	def process_events(self, events=None):
		
		if events is None:
			events = pygame.event.get()
		
		for event in events:
		
			if self.focus is not None:
				try:				
					if event.type == pygame.KEYDOWN:
						self.focus.trigger(Window.KEYDOWN, event.unicode, event.key, event.mod)
					elif event.type == pygame.KEYUP:
						self.focus.trigger(Window.KEYUP, event.key, event.mod)
						self.focus.trigger(Window.KEYPRESS, event.key, event.mod)
				except NotImplementedError:
					pass
			
			if event.type == pygame.MOUSEMOTION:
				
				current_pos = event.pos
				previous_pos = self._previous_mouse_pos
				
				for window in self.decendants:
					
					try:
						if not window.rect.collidepoint(previous_pos) and window.rect.collidepoint(event.pos):
							window.trigger(Window.MOUSEOVER)
						elif window.rect.collidepoint(previous_pos) and not window.rect.collidepoint(event.pos):
							window.trigger(Window.MOUSEOUT)
					except NotImplementedError:
						pass
					
				self._previous_mouse_pos = current_pos
			
			elif event.type == pygame.MOUSEBUTTONDOWN:
				
				for window in self.decendants:
					if window.rect.collidepoint(event.pos):
						window.trigger(Window.MOUSEDOWN)
						
						# Top-most window should receive the click event
						# due to the way Window.decendants returns windows
						if event.button == 1:
							self._mousedown_win = window
						
			elif event.type == pygame.MOUSEBUTTONUP:
				
				for window in self.decendants:
					if window.rect.collidepoint(event.pos):
						window.trigger(Window.MOUSEUP)
						
						if event.button == 1 and window is self._mousedown_win:
							window.trigger(Window.CLICK)
	
	def draw_window_background(self, window):
		if window.background is not None:
			pygame.draw.rect(self.surface, window.background, window.rect)
	
	def draw_window_border(self, window):

		if window.border_width < 1:
			return
			
		if window.border_style == Window.BORDER_STYLE_SOLID:
			pygame.draw.rect(self.surface, window.border_colour, window.rect, window.border_width)
			
		elif window.border_style == Window.BORDER_STYLE_OUTSET:

			lolight = window.border_colour
			hilight = [sum(cs) / len(cs) for cs in zip(lolight, (255, 255, 255), (255, 255, 255))]
			
			pygame.draw.line(self.surface, hilight, window.rect.topleft, window.rect.topright, window.border_width)
			pygame.draw.line(self.surface, hilight, window.rect.topleft, window.rect.bottomleft, window.border_width)
			pygame.draw.line(self.surface, lolight, window.rect.bottomleft, window.rect.bottomright, window.border_width)
			pygame.draw.line(self.surface, lolight, window.rect.bottomright, window.rect.topright, window.border_width)
		
		elif window.border_style == Window.BORDER_STYLE_INSET:

			lolight = window.border_colour
			hilight = [sum(cs) / len(cs) for cs in zip(lolight, (255, 255, 255), (255, 255, 255))]
			
			pygame.draw.line(self.surface, lolight, window.rect.topleft, window.rect.topright, window.border_width)
			pygame.draw.line(self.surface, lolight, window.rect.topleft, window.rect.bottomleft, window.border_width)
			pygame.draw.line(self.surface, hilight, window.rect.bottomleft, window.rect.bottomright, window.border_width)
			pygame.draw.line(self.surface, hilight, window.rect.bottomright, window.rect.topright, window.border_width)
		
	def draw_window_contents(self, window):
		if window.redraw:
			try:
				window.draw()
				window.redraw = False
			except NotImplementedError:
				pass
		
		if window.content_rect.width > 0  and window.content_rect.height > 0:
			if window.surface is not None:
				if (window.surface.get_height() > window.content_rect.height
					or window.surface.get_width() > window.content_rect.width):
					# If the window's surface exceeds the allocated space
					# clip it down to correct size. Does mean is surface_area
					# specifies an area smaller than the content_rect it will
					# be ignored.
					surface = pygame.Surface(window.content_rect.size)
					surface.blit(window.surface, (0, 0), window.surface_area)
					self.surface.blit(surface, window.content_rect)
				else:
					self.surface.blit(window.surface, window.content_rect, window.surface_area)
			
	def draw(self):
		
		for window in self.decendants:
			try:
				self.draw_window_background(window)
				self.draw_window_contents(window)
				self.draw_window_border(window)
			except:
				print "Couldn't draw {}".format(window.__class__.__name__)
				import pprint
				pprint.pprint(window.__dict__)
				raise
			
			if self.debug_draw:
				pygame.draw.rect(self.surface, (0, 255, 0), window.rect, 1)
				pygame.draw.rect(self.surface, (0, 0, 255), window.content_rect, 1)

class SurfaceWindow(Window):
	"""
		Simple wrapper around PyGame's Surface. Takes a surface and
		displays it within the window. Overides default width and
		height values to be those of the source surface.
	"""
	
	def __init__(self, parent, source, **kwargs):
		Window.__init__(self, parent, **kwargs)
		
		self.source_surface = source
		
		if "width" not in kwargs:
			self.width = source.get_width()
		if "height" not in kwargs:
			self.height = source.get_height()
		
	def draw(self):
		self.surface = pygame.transform.smoothscale(self.source_surface, (self.actual_width, self.actual_height))
		
class ScrollableWindow(Window):
	
	SCROLLUP = generate_event_id()
	SCROLLDOWN = generate_event_id()
	
	def __init__(self, parent=None, **kwargs):
		raise NotImplementedError
