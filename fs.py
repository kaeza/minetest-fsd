#! /usr/bin/env python2.7

import re
import gfx

POS_PROPS = (
	("x", "Left", "num"),
	("y", "Top",  "num"),
)

SIZE_PROPS = (
	("w", "Width",  "num"),
	("h", "Height", "num"),
)

black =  (  0,   0,   0)
gray25 = ( 64,  64,  64)
gray50 = (128, 128, 128)
white =  (255, 255, 255)

# TODO
def escape(s):
	return s

def unescape(s):
	return s

class Widget:

	description = "Base Widget"
	properties = ()

	show_in_menu = True

	def __init__(self, **kw):
		for prop in self.properties:
			pname, plabel, ptype = prop
			if (pname in kw) and (kw[pname] is not None):
				try:
					setattr(self, pname, kw[pname])
				except ValueError:
					pass

	def create(cls):
		return cls()

	def __str__(self):
		return ""

	def get_description(self):
		return "%s - %s" % (self.description, str(self))

	def draw(self, g):
		pass

class FormConfig(Widget):

	show_in_menu = False

	properties = (
		( "slot_bg_normal_color", "Slot Normal Color",  "color" ),
		( "slot_bg_hover_color",  "Slot Hover Color",   "color" ),
		( "slot_border_color",    "Slot Border Color",  "color" ),
		( "tooltip_bg_color",     "Tooltip Background", "color" ),
		( "tooltip_font_color",   "Tooltip Font Color", "color" ),
	)

	def __init__(self,
	  slot_bg_normal_color="",
	  slot_bg_hover_color="",
	  slot_border_color="",
	  tooltip_bg_color="",
	  tooltip_font_color=""):
		Widget.__init__(self,
			slot_bg_normal_color=slot_bg_normal_color,
			slot_bg_hover_color=slot_bg_hover_color,
			slot_border_color=slot_border_color,
			tooltip_bg_color=tooltip_bg_color,
			tooltip_font_color=tooltip_font_color
		)

	def __str__(self):
		return ("listcolors[%s;%s;%s;%s;%s]" % (
			self.slot_bg_normal_color,
			self.slot_bg_hover_color,
			self.slot_border_color,
			self.tooltip_bg_color,
			self.tooltip_font_color,
		))

	def get_description(self):
		return "<Formspec>"

class Label(Widget):

	description = "Label"
	item_names = ("label",)
	properties = POS_PROPS + (
		("text", "Text", "str"),
	)

	def __init__(self, x=0, y=0, text="Label"):
		Widget.__init__(self, x=x, y=y, text=text)

	def __str__(self):
		return "label[%f,%f;%s]" % (self.x, self.y, escape(self.text))

	def get_description(self):
		return "Label - %s" % self.text

	def draw(self, g):
		g.text(self.text, self.x, self.y, white, gfx.NW)

class Button(Widget):

	description = "Button"
	properties = POS_PROPS + SIZE_PROPS + (
		("name", "Name", "str"),
		("text", "Text", "str"),
	)

	def __init__(self, x=0, y=0, w=1, h=1, name="button", text="Button", exit=False):
		Widget.__init__(self, x=x, y=y, w=w, h=h, name=name, text=text, exit=exit)

	def __str__(self):
		return "button%s[%r,%r;%r,%r;%s;%s]" % (
			"_exit" if self.exit else "",
			self.x, self.y, self.w, self.h,
			escape(self.name), escape(self.text),
		)

	def get_description(self):
		return "Button [%s] - %s" % (self.name, self.text)

	def draw(self, g):
		x1, y1, x2, y2 = self.x, self.y, self.x+self.w, self.y+self.h
		g.rect(x1, y1, x2, y2, gray50)
		g.line(x1, y1, x1, y2, white)
		g.line(x1, y1, x2, y1, white)
		g.line(x2, y1, x2, y2, black)
		g.line(x1, y2, x2, y2, black)
		g.text(self.text, (x1+x2)/2, (y1+y2)/2, white, gfx.C)

class ImageButton(Widget):

	description = "Image Button"
	properties = POS_PROPS + SIZE_PROPS + (
		("texture", "Texture", "str"),
		("name",    "Name",    "str"),
		("text",    "Text",    "str"),
	)

	def __init__(self,
	  x=0, y=0,
	  w=1, h=1,
	  texture="default_wood.png",
	  name="button",
	  text="Button",
	  exit=False):
		Widget.__init__(self,
			x=x, y=y,
			w=w, h=h,
			texture=texture,
			name=name,
			text=text,
			exit=exit
		)

	def __str__(self):
		return "image_button%s[%r,%r;%r,%r;%s;%s]" % (
			"_exit" if self.exit else "",
			self.x, self.y, self.w, self.h,
			escape(self.texture), escape(self.name), escape(self.text),
		)

	def get_description(self):
		return "Button [%s] - %s" % (self.name, self.text)

	def draw(self, g):
		x1, y1, x2, y2 = self.x, self.y, self.x+self.w, self.y+self.h
		g.rect(x1, y1, x2, y2, gray50)
		g.line(x1, y1, x1, y2, white)
		g.line(x1, y1, x2, y1, white)
		g.line(x2, y1, x2, y2, black)
		g.line(x1, y2, x2, y2, black)
		g.text(self.text, (x1+x2)/2, (y1+y2)/2, white, gfx.C)

classes = (
	Label,
	Button,
)

name_to_class = { }
for c in classes:
	name_to_class[c.__name__] = c

class Form:

	def __init__(self, w, h, config=None):
		self.w = w
		self.h = h
		config = config or FormConfig()
		self.items = [ config ]
		self.config = config

	def add_item(self, item):
		self.items.append(item)

	def del_item(self, item):
		if isinstance(item, int) and (item > 0):
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
