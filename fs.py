#! /usr/bin/env python2.7

import re
import gfx

POS_PROPS = (
	("x",    "Left", float),
	("y",    "Top",  float),
)

SIZE_PROPS = (
	("w",    "Width",  float),
	("h",    "Height", float),
)

black =  (  0,   0,   0)
gray25 = ( 64,  64,  64)
gray50 = (128, 128, 128)
white =  (255, 255, 255)

def escape(s):
	return s

def unescape(s):
	return s

class Widget:

	description = "Base Widget"
	properties = ()

	def __init__(self, **kw):
		for prop in self.properties:
			pname, plabel, ptype = prop
			if (pname in kw) and (kw[pname] is not None):
				setattr(self, pname, kw[pname])

	def create(cls):
		return cls()

	def get_description(self):
		return "%s - %s" % (self.description, str(self))

	def __str__(self):
		return ""

	def draw(self, canvas):
		pass

class Label(Widget):

	description = "Label"
	item_names = ("label",)
	properties = POS_PROPS + (
		("text", "Text", str),
	)

	def __init__(self, x=0, y=0, text="Label"):
		Widget.__init__(self, x=x, y=y, text=text)

	def get_description(self):
		return "Label - %s" % self.text

	def __str__(self):
		return "label[%f,%f;%s]" % (self.x, self.y, escape(self.text))

	def draw(self, g):
		g.text(self.text, self.x, self.y, white, gfx.NW)

class Button(Widget):

	description = "Button"
	properties = POS_PROPS + SIZE_PROPS + (
		("name", "Name", str),
		("text", "Text", str),
	)

	def __init__(self, x=0, y=0, w=1, h=1, name="button", text="Button", exit=False):
		Widget.__init__(self, x=x, y=y, w=w, h=h, name=name, text=text, exit=exit)

	def get_description(self):
		return "Button [%s] - %s" % (self.name, self.text)

	def __str__(self):
		return "button[%r,%r;%r,%r;%s;%s]" % (
			self.x, self.y, self.w, self.h,
			escape(self.name), escape(self.text),
		)

	def draw(self, g):
		x1, y1, x2, y2 = self.x, self.y, self.x+self.w, self.y+self.h
		g.rect(x1, y1, x2, y2, gray50)
		g.line(x1, y1, x1, y2, white)
		g.line(x1, y1, x2, y1, white)
		g.line(x2-1, y1, x2-1, y2, black)
		g.line(x1, y2-1, x2, y2-1, black)
		g.text(self.text, (x1+x2)/2, (y1+y2)/2, white, gfx.C)

classes = (
	Label,
	Button,
)

class Form:

	def __init__(self, w, h, listcolors=None):
		self.w = w
		self.h = h
		self.items = [ ]
		self.listcolors = listcolors

	def add_item(self, item):
		self.items.append(item)

	def del_item(self, item):
		if isinstance(item, int):
			self.items.remove(item)
		else:
			try:
				self.items.remove(self.items.index(item))
			except IndexError:
				pass

	def draw(self, g):
		g.rect(0, 0, self.w, self.h, fill=gray25)
		for item in self.items:
			item.draw(g)

	def __str__(self):
		l = [ "size[%f,%f]" % (self.w, self.h) ]
		for item in self.items:
			l.append(str(item))
		return "".join(l)

	@classmethod
	def from_string(cls, s):
		# TODO
		pass
