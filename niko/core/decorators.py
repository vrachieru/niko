# import functools
from bottle import jinja2_view

from niko.core.dispatcher import Dispatcher

# Events

def trigger(event):
	print event
	def wrapper(ofn):
		print 'trigger'
		def nfn(*args, **kwds):
			print ofn(*args, **kwds)
		return nfn
	return wrapper

# # Chat

def respond_to(regex, case_sensitive=False):
	def wrapper(fn):
		def wrapped_fn(*args, **kwargs):
			fn(*args, **kwargs)
			# on ?
		wrapped_fn.metadata = getattr(fn, "metadata", {})
		wrapped_fn.metadata["listener_regex"] = regex
		wrapped_fn.metadata["case_sensitive"] = case_sensitive
		return wrapped_fn
	return wrapper

# def default_reply():
# 	pass

# # Scheduler

# def periodic():
# 	pass

# def randomly():
# 	pass

# # Web

# def api(path):
# 	pass

# def web():
# 	pass

# def template():
# 	pass

# view = functools.partial(jinja2_view, template_lookup=['templates'])


def api(path, *args, **kwargs):
	return route(''.join(['/api', path]), args, kwargs)

def web(path, *args, **kwargs):
	return route(path, args, kwargs)

def route(path, *args, **kwargs):
	def wrapper(fn):
		fn.metadata = getattr(fn, "metadata", {})
		fn.metadata["bottle_route"] = path
		for k, v in kwargs.items():
			fn.metadata["bottle_%s" % k] = v
		return fn
	return wrapper

def template(template_name, context=None):
	import os
	from jinja2 import Environment, FileSystemLoader

	template_dirs = ['/home/victor/workspace/niko-niko/niko/templates']
	loader = FileSystemLoader(template_dirs)
	env = Environment(loader=loader)

	if context is not None:
		this_template = env.get_template(template_name)
		return this_template.render(**context)
	else:
		def wrap(f):
			def wrapped_f(*args, **kwargs):
				context = f(*args, **kwargs)
				if type(context) == type({}):
					template = env.get_template(template_name)
					return template.render(**context)
				else:
					return context
			wrapped_f.metadata = getattr(f, "metadata", {})
			return wrapped_f
		return wrap