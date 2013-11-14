#! /usr/bin/env python2.7

import os
import re

from Tkinter import *
import tkMessageBox
import tkFileDialog
import tkColorChooser

import fs
import gfx

DATADIR = (os.path.dirname(__file__) or ".")+"/data"

GRID_SIZE = 40

VERSION = (0, 1, 0)
VERSION_STR = "%d.%d.%d" % VERSION

class Prop(Frame):

	def __init__(self, master, fsitem, propname):
		Frame.__init__(self, master)
		self.item = fsitem
		self.name = propname

	def get(self):
		pass

	def set(self, value):
		pass

	def commit(self):
		setattr(self.item, self.name, self.get())

class StringProp(Prop):

	def __init__(self, master, fsitem, propname):
		Prop.__init__(self, master, fsitem, propname)
		v = self.var = StringVar(value=getattr(fsitem, propname))
		ent = Entry(self, textvariable=v)
		ent.pack(side=LEFT, fill=BOTH, expand=True)

	def get(self):
		return self.var.get()

	def set(self, value):
		self.var.set(str(value))

class FloatProp(StringProp):

	def get(self):
		return float(self.var.get())

	def set(self, value):
		self.var.set(str(float(value)))

class BoolProp(Prop):

	def __init__(self, master, fsitem, propname):
		Prop.__init__(self, master, fsitem, propname)
		v = self.var = IntVar(value=int(getattr(fsitem, propname)))
		cb = Checkbox(self, variable=v)
		cb.pack(side=LEFT, fill=BOTH, expand=True)

	def get(self):
		return bool(self.var.get())

	def set(self, value):
		self.var.set(int(bool(value)))

class Color:

	regex = re.compile("#"
		+r'(?P<r>[0-9a-fA-F][0-9a-fA-F])'
		+r'(?P<g>[0-9a-fA-F][0-9a-fA-F])'
		+r'(?P<b>[0-9a-fA-F][0-9a-fA-F])'
		+r'(?P<a>[0-9a-fA-F][0-9a-fA-F])?'
	)

	mode = "color"

	def __init__(self, s=None, r=0, g=0, b=0, a=None):
		if s:
			m = self.regex.match(s)
			if not m:
				raise ValueError, "invalid color format"
			self.r = int(m.group("r"), 16)
			self.g = int(m.group("g"), 16)
			self.b = int(m.group("b"), 16)
			a = m.group("a")
			if a:
				self.a = int(a, 16)
			else:
				self.a = None
		else:
			self.r = r
			self.g = g
			self.b = b
			self.a = a

	def __str__(self):
		a = "" if self.a is None else "%02X" % self.a
		return "#%02X%02X%02X%s" % (self.r, self.g, self.b, a)

class ColorProp(Prop):

	def __init__(self, master, fsitem, propname):
		Prop.__init__(self, master, fsitem, propname)
		c = self.color = Color(getattr(fsitem, propname))
		v = self.var = StringVar(value=str(c))
		ent = Entry(self, textvariable=v)
		ent.pack(side=LEFT, fill=BOTH, expand=True)
		b = Button(self, text="...", command=lambda ent=ent: self.show_more(ent))
		b.pack(side=RIGHT)

	def show_more(self, ent):
		c = tkColorChooser.askcolor(color=ent.var.get())
		if c[1]:
			self.var.set(c[1])

	def get(self):
		return self.var.get()

	def set(self, value):
		c = Color(value)
		self.color = c
		self.var.set(str(c))

prop_types = {
	"str":   StringProp,
	"num":   FloatProp,
	"bool":  BoolProp,
	"color": ColorProp,
}

def not_implemented(*args, **kw):
	tkMessageBox.showwarning(message="Not implemented yet.")

class MainFrame(Frame):

	def __init__(self, parent):
		Frame.__init__(self, parent)
		self.parent = parent
		self.init_menu()
		self.init_view()
		self.formspec = fs.Form(4, 4)
		self.selection = None
		self.update_property_list()
		self.update_item_list()
		self.redraw_canvas()
		self.parent.bind("reconfigure", self.handle_reconfigure)

	def init_menu(self):
		menubar = Frame(self)
		menubar.pack(side=TOP, fill=X)

		mb = self.menu_file = Menubutton(menubar, text="File")
		mb.pack(side=LEFT)
		mb.menu = mb["menu"] = Menu(mb, tearoff=0)
		mb.menu.add_command(label="New", command=new_window)
		mb.menu.add_command(label="Open...", command=open_file)
		mb.menu.add_command(label="Save", command=self.mcb_file_save)
		mb.menu.add_command(label="Save as...", command=self.mcb_file_save_as)
		mb.menu.add_separator()
		mb.menu.add_command(label="Quit", command=self.parent.destroy)

		mb = self.menu_edit = Menubutton(menubar, text="Edit")
		mb.pack(side=LEFT)
		mb.menu = mb["menu"] = Menu(mb, tearoff=0)
		mb.menu.add_command(label="Undo", command=self.mcb_edit_undo)
		mb.menu.add_command(label="Redo", command=self.mcb_edit_redo)
		mb.menu.add_separator()
		mb.menu.add_command(label="Copy", command=self.mcb_edit_copy)
		mb.menu.add_command(label="Cut", command=self.mcb_edit_cut)
		mb.menu.add_command(label="Paste", command=self.mcb_edit_paste)

		mb = self.menu_form = Menubutton(menubar, text="Form")
		mb.pack(side=LEFT)
		mb.menu = mb["menu"] = Menu(mb, tearoff=0)
		mb.menu.add_command(label="Properties...", command=self.mcb_form_props)
		mb.menu.add_separator()
		for i in fs.classes:
			mb.menu.add_command(label="Add %s" % i.description,
				command=lambda i=i: self.mcb_form_add(i)
			)

		mb = self.menu_help = Menubutton(menubar, text="Help")
		mb.pack(side=RIGHT)
		mb.menu = mb["menu"] = Menu(mb, tearoff=0)
		mb.menu.add_command(label="About...", command=self.mcb_help_about)

	def init_view(self):
		hbox = Frame(self)
		hbox.pack(side=BOTTOM, fill=BOTH, expand=True)
		vbox = Frame(hbox)
		vbox.pack(side=LEFT, fill=BOTH)
		l = self.prop_list = Frame(vbox)
		l.pack(side=TOP, fill=BOTH)
		l = self.item_list = Listbox(vbox)
		l.pack(side=BOTTOM, fill=BOTH)
		l.bind("<Button-1>", self.item_list_select)

		vbox = Frame(hbox)
		vbox.pack(side=RIGHT, fill=BOTH, expand=True)
		toolbar = self.toolbar = Frame(vbox)
		toolbar.pack(side=TOP, fill=X)
		for i in fs.classes:
			try:
				image = PhotoImage(file=DATADIR+"/"+i.__name__+".gif")
				b = Button(toolbar,
					text=i.__name__,
					image=image,
					command=lambda i=i: self.mcb_form_add(i)
				)
				b.image = image
				b.pack(side=LEFT)
			except TclError, e:
				print e
				pass
		c = self.canvas = Canvas(vbox)
		c["bg"] = "#0000C0"
		c.pack(side=TOP, fill=BOTH, expand=True)
		t = self.fsbox = Text(vbox, height=4)
		t.pack(side=BOTTOM, fill=BOTH, expand=False)

	def item_list_select(self, event):
		idx = self.item_list.index("@%d,%d" % (event.x, event.y))
		self.select_item(idx)

	def handle_reconfigure(self, event):
		self.redraw_canvas()

	def update_item_list(self):
		l = self.item_list
		l.delete(0, "end")
		for item in self.formspec.items:
			l.insert(END, item.get_description())
		try:
			l.activate(self.formspec.items.index(self.selection))
		except ValueError:
			pass

	def update_property_list(self):
		for wid in self.prop_list.grid_slaves():
			wid.grid_forget()
		l = Label(self.prop_list, text="Properties")
		l.grid(column=0, row=0, columnspan=2)
		if not self.selection: return
		n = 1
		props = self.props = [ ]
		for prop in self.selection.properties:
			pname, plabel, ptype = prop
			if ptype in prop_types:
				ptype = prop_types[ptype]
				lbl = Label(self.prop_list, text=plabel)
				f = ptype(self.prop_list, self.selection, pname)
				lbl.grid(column=0, row=n)
				f.grid(column=1, row=n)
				n += 1
				props.append(f)
		b = Button(self.prop_list, text="Apply", command=self.apply_props)
		b.grid(column=0, row=n)
		b = Button(self.prop_list, text="Revert", command=self.update_property_list)
		b.grid(column=1, row=n)

	def apply_props(self):
		if not self.selection: return
		for prop in self.props:
			try:
				prop.commit()
			except ValueError:
				pass
		self.redraw_canvas()
		self.update_item_list()

	def mcb_form_add(self, cls):
		print "Creating %s..." % cls.__name__
		i = cls()
		print(str(i))
		self.add_item(i)

	def add_item(self, item):
		self.formspec.add_item(item)
		self.redraw_canvas()
		self.select_item(item)
		self.update_item_list()

	def del_item(self, item):
		self.formspec.del_item(item)

	def select_item(self, item):
		if isinstance(item, int):
			try:
				self.selection = self.formspec.items[item]
			except IndexError:
				pass
		else:
			self.selection = item
		self.update_property_list()

	def redraw_canvas(self):
		cw = self.canvas.winfo_width()
		ch = self.canvas.winfo_height()
		scale=(cw/12, ch/12)
		translate = (
			(cw - (self.formspec.w * scale[0])) / 2,
			(ch - (self.formspec.h * scale[1])) / 2,
		)
		g = gfx.TkGraphics(self.canvas, translate=translate, scale=scale)
		g.clear()
		self.formspec.draw(g)
		self.fsbox.delete("0.0", END)
		self.fsbox.insert(END, str(self.formspec))

	def mcb_file_save(self):
		if not self.filename:
			filename = tkFileDialog.asksavefilename()
			if filename:
				try:
					f = open(filename, "wt")
					
				except IOError as e:
					tkMessageBox.showerror(message=str(e))

	mcb_file_save_as = \
	mcb_edit_undo = \
	mcb_edit_redo = \
	mcb_edit_copy = \
	mcb_edit_cut = \
	mcb_edit_paste = \
	mcb_form_props = \
	mcb_help_about = \
		not_implemented

root = None

def new_window(filename=None):
	win = Toplevel(root)
	win.title("Formspec Designer %s" % VERSION_STR)
	win.minsize(800, 600)
	mf = MainFrame(win)
	mf.pack(fill=BOTH, expand=True)
	win.mainloop()

def open_file():
	filename = tkFileDialog.askopenfilename()
	if filename:
		new_window(filename)

def main():
	global root
	root = Tk()
	root.title("Formspec Designer %s" % VERSION_STR)
	bb = Frame(root)
	bb.pack(side=TOP, fill=X)
	Button(bb, text="New",     command=new_window).pack(side=LEFT)
	Button(bb, text="Open...", command=open_file).pack(side=LEFT)
	Button(bb, text="Quit",    command=exit).pack(side=LEFT)
	root.mainloop()

if __name__ == "__main__":
	main()
