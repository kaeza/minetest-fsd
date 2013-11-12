#! /usr/bin/env python2.7

C = 0
W = (1 << 0)
N = (1 << 1)
E = (1 << 2)
S = (1 << 3)

NW = N|W
NE = N|E
SW = S|W
SE = S|E

class Graphics:

	def __init__(self, translate=None, scale=None):
		self.set_translate(translate)
		self.set_scale(scale)

	def set_translate(self, translate):
		self.translate = translate or (0, 0)

	def set_scale(self, scale):
		self.scale = scale or (1, 1)

	def line(self, x1, y1, x2, y2, color=None):
		x1 = (x1 * self.scale[0]) + self.translate[0]
		y1 = (y1 * self.scale[1]) + self.translate[1]
		x2 = (x2 * self.scale[0]) + self.translate[0]
		y2 = (y2 * self.scale[1]) + self.translate[1]
		self.raw_line(x1, y1, x2, y2, color)

	def rect(self, x1, y1, x2, y2, color=None, fill=None):
		x1 = (x1 * self.scale[0]) + self.translate[0]
		y1 = (y1 * self.scale[1]) + self.translate[1]
		x2 = (x2 * self.scale[0]) + self.translate[0]
		y2 = (y2 * self.scale[1]) + self.translate[1]
		self.raw_rect(x1, y1, x2, y2, color, fill)

	def text(self, text, x, y, color=None, anchor=C):
		x = (x * self.scale[0]) + self.translate[0]
		y = (y * self.scale[1]) + self.translate[1]
		self.raw_text(text, x, y, color, anchor)

	# These should be overriden by subclasses.
	def clear(self, color=None): pass
	def raw_line(self, x1, y1, x2, y2, color=None): pass
	def raw_rect(self, x1, y1, x2, y2, color=None, fill=None): pass
	def raw_text(self, text, x, y, color=None, anchor=C): pass

class TkGraphics(Graphics):

	def __init__(self, canvas, translate=None, scale=None):
		Graphics.__init__(self, translate, scale)
		self.canvas = canvas

	@staticmethod
	def _to_tk_anchor(anchor):
		if anchor == 0: return "center"
		l = [ ]
		if anchor & N: l.append("n")
		if anchor & S: l.append("s")
		if anchor & W: l.append("w")
		if anchor & E: l.append("e")
		return "".join(l)

	@staticmethod
	def _to_tk_color(color):
		return "#%02X%02X%02X" % color

	def clear(self, color=None):
		self.canvas.delete("all")
		if color is not None: self.canvas["bg"] = self._to_tk_color(color)

	def raw_line(self, x1, y1, x2, y2, color=None):
		if color is not None: color = self._to_tk_color(color)
		self.canvas.create_line(x1, y1, x2, y2, fill=color)

	def raw_rect(self, x1, y1, x2, y2, color=None, fill=None):
		if color is not None: color = self._to_tk_color(color)
		if fill is not None: fill = self._to_tk_color(fill)
		self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill)

	def raw_text(self, text, x, y, color=None, anchor=C):
		if color is not None: color = self._to_tk_color(color)
		if anchor is not None: anchor = self._to_tk_anchor(anchor)
		self.canvas.create_text(x, y, fill=color, text=text, anchor=anchor)
