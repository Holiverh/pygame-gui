
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
	
	default_background = (0xB7, 0xB7, 0xB7)
	default_border_colour = (0xC8, 0xC8, 0xC8)
	default_border_width = 1
	default_padding = 0
	default_font_name = "Tahoma"
	default_font_size = 14
	default_font_colour = (0, 0, 0)
	default_font_aa = True
	
	_font_cache = {}
	
	def __init__(self, parent=None, **kwargs):
		
		self.parent = parent
		self.children = []
		self.callbacks = {}
		
		if self.parent is not None:
			self.parent.add_window(self)
		
		self._kwargs = kwargs
		
		# Float for relative dimensions/positions, integer for absolute
		self.width = kwargs.get("width", 1.0)
		self.height = kwargs.get("height", 1.0)
		self.x = kwargs.get("x", 0)
		self.y = kwargs.get("y", 0)
		
		self.background = kwargs.get("background", self.__class__.default_background)
		self.border_width = kwargs.get("border_width", self.__class__.default_border_width)
		self.border_colour = kwargs.get("border_colour", self.__class__.default_border_colour)
		self.padding = kwargs.get("padding", self.__class__.default_padding)
		self.font_name = kwargs.get("font", self.__class__.default_font_name)
		self.font_colour = kwargs.get("font_colour", self.__class__.default_font_colour)
		self.font_size = kwargs.get("font_size", self.__class__.default_font_size)
		self.font_aa = kwargs.get("font_aa", self.__class__.default_font_aa)
	
	def _print_graph(self, indent=0):
		
		print "{}{} ({}, {}) {}x{}".format(
						" "*indent,
						self.__class__.__name__,
						self.actual_x,
						self.actual_y,
						self.actual_width,
						self.actual_height)
		for child in self.children:
			child._print_graph(indent+4)
	
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
			
		return Window._font_cache[font_config]
	
	@font.setter
	def font(self, values):
		for value, attr in zip(values,
				["font_name", "font_colour", "font_size", "font_aa"]):
			setattr(self, attr, value)
	
	def add_window(self, window):
		""" Adds the window to the list of children and sets its parent attribute. """
		
		window.parent = self
		self.children.append(window)
	
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
			return int(round(self.width * self.parent.actual_width) + (2 * self.padding) + (2 * self.border_width))
		else:
			return int(self.width + (2 * self.padding) + (2 * self.border_width))
	
	@property
	def requested_height(self):
		if type(self.height) is types.FloatType:
			return int(round(self.height * self.parent.actual_height) + (2 * self.padding) + (2 * self.border_width))
		else:
			return int(self.height + (2 * self.padding) + (2 * self.border_width))
	
	@property
	def actual_height(self):
		# TODO: Overflow rules; clip, cull
		return self.requested_height if self.requested_height <= self.parent.actual_height else self.parent.actual_height
	
	@property
	def actual_width(self):
		# TODO: Overflow rules
		return self.requested_width if self.requested_width <= self.parent.actual_width else self.parent.actual_width
	
	@property
	def requested_x(self):
		if type(self.x) is types.FloatType:
			return int(round(self.x * self.parent.actual_width))
		else:
			return int(self.x)
	
	@property
	def requested_y(self):
		if type(self.y) is types.FloatType:
			return int(round(self.y * self.parent.actual_height))
		else:
			return int(self.y)
	
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
	
	def draw_background(self, surface):
		if self.background is not None:
			pygame.draw.rect(surface, self.background, self.rect)
	
	def draw_border(self, surface):
		pygame.draw.rect(surface, self.border_colour, self.rect, self.border_width)
	
	def draw(self): raise NotImplementedError
	
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
		self.surface = pygame.display.get_surface()
		self._focus = None # Which window has keyboard focus
		
		self._previous_mouse_pos = pygame.mouse.get_pos()
		
		Window.__init__(self, None,
							width=self.surface.get_width(),
							height=self.surface.get_height(),
							background=None,
							border_width=0
						)
		
	@property
	def focus(self):
		return self._focus
	
	@focus.setter
	def focus(self, window):
		self._focus.trigger(BLUR)
		self._focus = window
		self._focus.trigger(FOCUS)
		
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
				pass
			
	def draw(self):
		
		for window in self.decendants:
			window.draw_background(self.surface)
			try:
				self.surface.blit(window.draw(), window.content_rect)
			except NotImplementedError:
				pass
			window.draw_border(self.surface)
			
			if self.debug_draw:
				pygame.draw.rect(self.surface, (0, 255, 0), window.rect, 1)
				pygame.draw.rect(self.surface, (0, 0, 255), window.content_rect, 1)
	
class ScrollableWindow(Window):
	
	SCROLLUP = generate_event_id()
	SCROLLDOWN = generate_event_id()
	
	def __init__(self, parent=None, **kwargs):
		raise NotImplementedError
