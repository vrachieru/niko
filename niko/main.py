# -*- coding: utf-8 -*-

import os
import functools
from bottle import jinja2_view, route, run, get, post
import bottle


import logging
import inspect
import imp

import operator
import re
import sys
import time
import traceback
from clint.textui import colored, puts, indent
from os.path import abspath, dirname
from multiprocessing import Process, Queue


PROJECT_ROOT = abspath(os.path.join(dirname(__file__)))
PLUGINS_ROOT = abspath(os.path.join(PROJECT_ROOT, "plugins"))
TEMPLATES_ROOT = abspath(os.path.join(PROJECT_ROOT, "templates"))


from core.cache import Cache
from core.chatclient import ChatClient
from core.dispatcher import Dispatcher

class NikoMain(ChatClient, Dispatcher, Cache):
	def __init__(self, **kwargs):
		self.plugins_dirs = {}
		self.plugins = [
			'niko.plugins.admin',
			'niko.plugins.friendly',
			'niko.plugins.web'
			]

		for plugin in self.plugins:
			path_name = None
			for mod in plugin.split('.'):
				if path_name is not None:
					path_name = [path_name]
				file_name, path_name, description = imp.find_module(mod, path_name)

			# Add, uniquely.
			self.plugins_dirs[os.path.abspath(path_name)] = plugin

		# Key by module name
		self.plugins_dirs = dict(zip(self.plugins_dirs.values(), self.plugins_dirs.keys()))

	def bootstrap(self):
		banner()

		self.bootstrap_plugins()
		self.bootstrap_cache()
		# self.verify_plugin_settings()


		self.save('test', 'test')
		puts(self.load('test'))

		puts("Bootstrapping complete.")
		puts("\nStarting core processes:")

		# Threads
		# threads = {}
		# threads['webserver'] = Process(target=self.bootstrap_webserver)
		# threads['scheduler'] = Process(target=self.bootstrap_scheduler)
		# threads['chatclient'] = Process(target=self.bootstrap_chatclient)

		webserver_thread = Process(target=self.bootstrap_webserver)				
		scheduler_thread = Process(target=self.bootstrap_scheduler)
		chatclient_thread = Process(target=self.bootstrap_chatclient)

		with indent(2):
			try:
				webserver_thread.start()
				scheduler_thread.start()
				chatclient_thread.start()

				while True:
					time.sleep(100)
			except (KeyboardInterrupt, SystemExit):
				webserver_thread.terminate()
				scheduler_thread.terminate()
				chatclient_thread.terminate()

				print '\n\nReceived keyboard interrupt, quitting threads.',
				while (webserver_thread.is_alive() or scheduler_thread.is_alive() or chatclient_thread.is_alive()):
					sys.stdout.write(".")
					sys.stdout.flush()
					time.sleep(0.5)
				print '\n'

	def bootstrap_webserver(self):
		def route_plugins():
			for cls, function_name in self.bottle_routes:
				instantiated_cls = cls()
				instantiated_fn = getattr(instantiated_cls, function_name)
				bottle_route_args = {}
				for k, v in instantiated_fn.metadata.items():
					if "bottle_" in k and k != "bottle_route":
						bottle_route_args[k[len("bottle_"):]] = v
					bottle.route(instantiated_fn.metadata["bottle_route"], **bottle_route_args)(instantiated_fn)

		def start_server():
			bottle.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), quiet=True)

		bootstrapped = True
		try:
			route_plugins()
			start_server()
		except Exception, e:
			print e
			# self.startup_error("Error bootstrapping bottle", e)
			bootstrapped = False
			pass

		# if bootstrapped == True:
		success("Web server started")
			
	def bootstrap_scheduler(self):
		bootstrapped = False
		try:
			bootstrapped = True
		except Exception, e:
			# self.startup_error("Error bootstrapping scheduler", e)
			pass
		if bootstrapped:
			success("Scheduler started.")
			# self.scheduler.start_loop(self)
			
	def bootstrap_plugins(self):
		puts("Bootstrapping plugins...")

		OTHER_HELP_HEADING = "Other"
		plugin_modules = {}
		plugin_modules_library = {}

		with indent(2):
			for plugin_name, plugin_root in self.plugins_dirs.items():
				for root, dirs, files in os.walk(plugin_root, topdown=False):
					for f in files:
						if f[-3:] == ".py" and f != "__init__.py":
							try:
								module_path = os.path.join(root, f)
								path_components = os.path.split(module_path)
								module_name = path_components[-1][:-3]
								full_module_name = ".".join(path_components)
								# Need to pass along module name, path all the way through
								combined_name = ".".join([plugin_name, module_name])

								# # Check blacklist.
								blacklisted = False
								try:
									plugin_modules[full_module_name] = imp.load_source(module_name, module_path)
								except Exception, e:
									error(module_name)
									error(e)
								parent_mod = path_components[-2].split("/")[-1]
								parent_help_text = parent_mod.title()
								try:
									parent_root = os.path.join(root, "__init__.py")
									parent = imp.load_source(parent_mod, parent_root)
									parent_help_text = getattr(parent, "MODULE_DESCRIPTION", parent_help_text)
								except:
									# If it's blacklisted, don't worry if this blows up.
									if blacklisted:
										pass
									else:
										raise

								plugin_modules_library[full_module_name] = {
									"full_module_name": full_module_name,
									"file_path": module_path,
									"name": module_name,
									"parent_name": plugin_name,
									"parent_module_name": parent_mod,
									"parent_help_text": parent_help_text,
									"blacklisted": blacklisted
								}
							except Exception, e:
								puts(e)
								pass

				self.plugins = []
				for name, module in plugin_modules.items():
					try:
						for class_name, cls in inspect.getmembers(module, predicate=inspect.isclass):
							try:
								if class_name != "NikoPlugin":
									self.plugins.append({
										"name": class_name,
										"class": cls,
										"module": module,
										"full_module_name": name,
										"parent_name": plugin_modules_library[name]["parent_name"],
										"parent_module_name": plugin_modules_library[name]["parent_module_name"],
										"parent_help_text": plugin_modules_library[name]["parent_help_text"],
										"blacklisted": plugin_modules_library[name]["blacklisted"]
									})
							except Exception, e:
								error(e)
								pass
					except Exception, e:
						pass

			self._plugin_modules_library = plugin_modules_library

			def register_listeners():
				pass

			# Sift and Sort.
			self.message_listeners = []
			self.periodic_tasks = []
			self.random_tasks = []
			self.bottle_routes = []
			self.all_listener_regexes = []
			self.help_modules = {}
			self.help_modules[OTHER_HELP_HEADING] = []
			self.some_listeners_include_me = False
			self.plugins.sort(key=operator.itemgetter("parent_module_name"))
			self.required_settings_from_plugins = {}

			last_parent_name = None
			for plugin_info in self.plugins:
				try:
					if last_parent_name != plugin_info["parent_help_text"]:
						friendly_name = "%(parent_help_text)s " % plugin_info
						module_name = " %(parent_name)s" % plugin_info
						# Justify
						friendly_name = friendly_name.ljust(50, '-')
						module_name = module_name.rjust(40, '-')
						puts("")
						puts("%s%s" % (friendly_name, module_name))

						last_parent_name = plugin_info["parent_help_text"]
					with indent(2):
						plugin_name = plugin_info["name"]
						# Just a little nicety
						if plugin_name[-6:] == "Plugin":
							plugin_name = plugin_name[:-6]
						if plugin_info["blacklisted"]:
							puts("✗ %s (blacklisted)" % plugin_name)
						else:
							plugin_instances = {}
							for function_name, fn in inspect.getmembers(
								plugin_info["class"],
								predicate=inspect.ismethod
							):
								try:
									# Check for required_settings
									with indent(2):
										if hasattr(fn, "metadata"):
											meta = fn.metadata
											if "required_settings" in meta:
												for s in meta["required_settings"]:
													self.required_settings_from_plugins[s] = {
														"plugin_name": plugin_name,
														"function_name": function_name,
														"setting_name": s,
													}
											if (
												"listens_to_messages" in meta and
												meta["listens_to_messages"] and
												"listener_regex" in meta
											):
												regex = meta["listener_regex"]
												if not meta["case_sensitive"]:
													regex = "(?i)%s" % regex
												help_regex = meta["listener_regex"]
												if meta["listens_only_to_direct_mentions"]:
													pass
													# help_regex = "@%s %s" % (settings.HANDLE, help_regex)
												# self.all_listener_regexes.append(help_regex)
												if meta["__doc__"]:
													pht = plugin_info.get("parent_help_text", None)
													if pht:
														if pht in self.help_modules:
															self.help_modules[pht].append(meta["__doc__"])
														else:
															self.help_modules[pht] = [meta["__doc__"]]
													else:
														self.help_modules[OTHER_HELP_HEADING].append(meta["__doc__"])

												compiled_regex = re.compile(regex)

												if plugin_info["class"] in plugin_instances:
													instance = plugin_instances[plugin_info["class"]]
												else:
													instance = plugin_info["class"]()
													plugin_instances[plugin_info["class"]] = instance

												self.message_listeners.append({
													"function_name": function_name,
													"class_name": plugin_info["name"],
													"regex_pattern": meta["listener_regex"],
													"regex": compiled_regex,
													"fn": getattr(instance, function_name),
													"args": meta["listener_args"],
													"direct_mentions_only": meta["listens_only_to_direct_mentions"]
												})
											elif "periodic_task" in meta and meta["periodic_task"]:
												self.periodic_tasks.append((plugin_info, fn, function_name))
											elif "random_task" in meta and meta["random_task"]:
												self.random_tasks.append((plugin_info, fn, function_name))
											elif "bottle_route" in meta:
												self.bottle_routes.append((plugin_info["class"], function_name))
								except Exception, e:
									error(e)
									pass
							success(plugin_name)
				except Exception, e:
					pass
		puts("")


def success(success_str):
	puts(colored.green(u"✓ %s" % success_str))


def warn(warn_string):
	puts(colored.yellow("! Warning: %s" % warn_string))


def error(err_string):
	puts(colored.red(u"✗ %s" % err_string))


def note(warn_string):
	puts(colored.cyan("- Note: %s" % warn_string))

def banner():
	f = open(os.path.join('niko', 'static', 'banner.txt'))
	puts(f.read())