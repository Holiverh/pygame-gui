
import weakref
import warnings

import pygame.gui.window

TOP = 0
MIDDLE = 1
BOTTOM = 2
LEFT = 3
RIGHT = 4

str_id_map = {
	"top": TOP,
	"middle": MIDDLE,
	"bottom": BOTTOM,
	"left": LEFT,
	"right": RIGHT,			
	}

class Poser(object):
	
	def __init__(self, window):
		self.window = window

	def _bind_windows(self, windows, callback):
		for window in windows:
			window.bind(pygame.gui.window.Window.RECONFIGURE, callback)
			window.trigger(pygame.gui.window.Window.RECONFIGURE)

	def centre(self):
		""" Centre window on its parent """
		
		def _centre(parent):
			self.window.x = (parent.actual_width / 2) - (self.window.actual_width / 2)
			self.window.y = (parent.actual_height / 2) - (self.window.actual_height / 2)
		
		self._bind_windows([self.window.parent], _centre)
		
		return self
	
	def above(self, *windows):
		"""
			Positions the window above all the others. All specified
			windows should be siblings of the one being posed.
		"""
		
		def _above(win):
			swin = max(windows, key=lambda w: w.requested_y)
			self.window.y = swin.requested_y - self.window.actual_height
		
		self._bind_windows(windows, _above)
		
	def below(self, *windows):
		""" Positions the window underneath all the others. All specified
			windows should be siblings of the one being posed.
		"""
		
		def _below(win):
			swin = max(windows, key=lambda w: w.requested_y + w.actual_height)
			self.window.y = swin.requested_y + swin.actual_height
		
		self._bind_windows(windows, _below)	
		return self
		
	def right_of(self, *others):
		"""
			Positions the window to the right of the rightmost selection
			of windows. All specified windows should be siblings of the
			one being posed.
		"""
		
		def _right_of(win):
			swin = max(others, key=lambda w: w.requested_x + w.actual_width)
			self.window.x = swin.requested_x + swin.actual_width
		
		self._bind_windows(others, _right_of)
		return self
	
	def left_of(self, *windows):
		"""
			Positions the window to the left of the leftmost selection
			of windows. All specified windows should be siblings of the
			one being posed.
		"""
		
		def _left_of(win):
			swin = min(windows, key=lambda w: w.requested_x)
			self.window.x = swin.requested_x - self.window.actual_width
			
		self._bind_windows(windows, _left_of)
		return self
	
	def align_vertical(self, window, rel=TOP):
		
		if rel in str_id_map:
			rel = str_id_map[rel]
		
		def _align_vertical(win):
			
			if rel == TOP:
				self.window.y = window.y
			elif rel == MIDDLE:
				self.window.y = window.y - ((self.window.actual_height - window.actual_height) / 2)
			elif rel == BOTTOM:
				max_h = max(window.actual_height, self.window.actual_height)
				min_h = min(window.actual_height, self.window.actual_height)
				self.window.y = window.y + (max_h - min_h)

		self._bind_windows([window], _align_vertical)
		return self
