import threading
import pickle
import random
import os
import vlc
import time
import sys
import subprocess
import tkinter as tk

def edit_active_series():
	def add_item():
		active = p.ACTIVE_SERIES
		if type(active) == tuple:
			active = list(active)
		indexes = listbox_all_series.curselection()
		for idx in indexes:
			item = listbox_all_series.get(idx)
			if item not in active:
				listbox_active_series.insert(tk.END, item)
				active.append(item)
			else:
				print("Item already in active:", item)
		update_list(listbox_active_series, active)
		p.set_active_series(active)
		return active
	def del_item():
		indexes = listbox_active_series.curselection()
		print("indexes:", indexes)
		for idx in indexes:
			item = listbox_active_series.get(idx)
			if item in active:
				idx = active.index(item)
				_ = active.pop(idx)
			else:
				print("Item not in active???", item)
		update_list(listbox_active_series, active)
		p.set_active_series(active)
		return active
	def update_active(active_items=None):
		if active_items is None:
			active_items = listbox_active_series.get(0, tk.END)
			if len(active_items) != len(p.ACTIVE_SERIES):
				print("Length is different! Updating player option ('ACTIVE_SERIES')...")
				p.set_active_series(series_names=active_items)
		root.destroy()
		return active_items
	def update_list(lb, items):
		lb.delete(0, tk.END)
		for item in items:
			lb.insert(tk.END, item)
	if p is None:
		p = Player()
	active = p.ACTIVE_SERIES
	root = tk.Tk()
	active_frame = tk.Frame(root)
	all_frame = tk.Frame(root)
	txt_active = tk.Label(active_frame, text='Active Series Names')
	txt_active.pack(side='top')
	txt_all = tk.Label(all_frame, text='All Series')
	txt_all.pack(side='top')
	listbox_active_series = tk.Listbox(active_frame)
	listbox_all_series = tk.Listbox(all_frame)
	listbox_active_series.pack(side='top')
	listbox_all_series.pack(side='top')
	btn_add = tk.Button(all_frame, text='Add!', command=add_item)
	btn_add.pack(side='top')
	btn_del = tk.Button(active_frame, text='Del!', command=del_item)
	btn_del.pack(side='top')
	btn_ok = tk.Button(root, text='Ok!', command=update_active)
	active_frame.pack(side='left')
	all_frame.pack(side='right')
	btn_ok.pack(side='right')
	active = p.ACTIVE_SERIES
	update_list(listbox_active_series, active)
	all_series = list(p.PLAYLIST._list_series().keys())
	update_list(listbox_all_series, all_series)

def get_screen_res():
	w, h = subprocess.check_output("xrandr | grep '*' | xargs | cut -d ' ' -f 1", shell=True).decode().strip().split('x')
	return int(w), int(h)
	

class MediaGuesser():
	def __init__(self, filepath=None):
		self.FILEPATH = filepath
	def _get_years(self):
		return self._get_list(1900, 2040)
	def _get_list(self, min_val=0, max_val=333):
		l = []
		for i in range(min_val, max_val):
			l.append(i)
		return l
	def _get_seasons(self):
		out = []
		sl = self._get_list(0, 333)
		el = sl
		for s in sl:
			if len(str(s)) == 1:
				s2 = f"S0{s}"
				s1 = f"S{s}"
			else:
				s2 = f"S{s}"
				s1 = None
			for e in el:
				if len(str(e)) == 1:
					e2 = f"E0{e}"
					e1 = f"E{e}"
				else:
					e2 = f"E{e}"
					e1 = None
				if e2 is not None and s2 is not None:
					out.append(f"{s2}{e2}")
				if e1 is not None and s1 is not None:
					out.append(f"{s1}{e1}")
		return out

	def se_isin(self, filepath, return_data=False):
		for s in self._get_seasons():
			if s in filepath:
				if not return_data:
					return True
				else:
					return s
	
	def year_in(self, filepath, return_data=False):
		for y in self._get_years():
			if f"({y})" in filepath:
				if not return_data:
					return True
				else:
					return y

	def guess_media_type(self, filepath=None, return_data=False):
		if filepath is None:
			filepath = self.FILEPATH
		if self.se_isin(filepath):
			if not return_data:
				return 'Series'
			else:
				return self.se_isin(filepath, return_data=True)
		if self.year_in(filepath):
			if  not return_data:
				return 'Movies'
			else:
				return self.year_in(filepath, return_data=True)

	def get_info_from_filepath(self, filepath=None, media_type=None):
		if filepath is None:
			filepath = self.FILEPATH
		out = {}
		out['filepath'] = filepath
		fname = os.path.basename(filepath)
		fname, ext = os.path.splitext(fname)
		dname = os.path.dirname(filepath)
		if media_type is None:
			media_type = self.guess_media_type(filepath)
		out['media_type'] = media_type
		if media_type == 'Movies':
			out['year'] = self.year_in(filepath, return_data=True)
			out['title'] = fname.split(f"({out['year']})")[0].strip()
		elif media_type == 'Series':
			s = self.se_isin(filepath, return_data=True)
			out['series_name'] = fname.split(s)[0]
			out['season'] = s.split("S")[1].split("E")[0]
			out['episode_number'] = s.split('E')[1]
		return out

class Media():
	def __init__(self, data):
		self.data = data
		for k in data:
			self.__dict__[k] = data[k]
		try:
			#print("Media created as type:", self.media_type)
			mt = self.media_type
		except:
			self.media_type = MediaGuesser().guess_media_type(filepath=self.filepath)
			print("Media type not provided! Guessing...", self.media_type)
	def __str__(self):
		l = []
		for k in self.data:
			l.append(f"{k}={self.data[k]}")
		return ", ".join(l)
	def match(self, key, val=None, return_object=False):
		keys = list(self.data.keys())
		if key in keys:
			if val is None:
				if not return_object:
					return True
				else:
					return self
			else:
				v = self.data[key]
				if v == val:
					if not return_object:
						return True
					else:
						return self
		else:
			pass



class Playlist():
	def __init__(self, media_path='/media/monkey/usbhd/Media', playback_types=None, active_series=None):
		"""
		TDDO - add episode_number to movie files for ordering list in a set/trilogy/etc.
		TODO - function - auto determine media type
		TODO - function - parse Media class data dict from filepath depending on media type
		"""
		try:
			self.HISTORY = self.load_history()
		except:
			self.HISTORY = self._init_history()
		if playback_types is None:
			playback_types = ['Series']
		self.ACTIVE_PLAYBACK_TYPES = playback_types
		self.MEDIA_DIR = media_path
		self.SERIES_DIR = os.path.join(self.MEDIA_DIR, 'Series')
		self.MOVIES_DIR = os.path.join(self.MEDIA_DIR, 'Movies')
		self.MUSIC_DIR = os.path.join(self.MEDIA_DIR, 'Music')
		if active_series is not None:#if active series list provided (i.e. loaded from Player settings)...
			self.ACTIVE_SERIES = active_series
		else:
			self.ACTIVE_SERIES = list(self._list_series().keys())#default to all in series list, overridden by Player settings.conf
		self.SERIES = self.get_series(active_series=self.ACTIVE_SERIES)
		self.MOVIES = self.get_movies()
		self.Guesser = MediaGuesser()
		self.LAST = None
		try:
			self.NEXT = self.get_next()
		except Exception as e:
			self.NEXT = None
	def _guess_media_type(self, filepath):
		return self.Guesser.guess_media_type(filepath)
	def _get_info(self, filepath):
		return self.Guesser.get_info_from_filepath(filepath)
	def _init_history(self):
		self.HISTORY = {}
		self.HISTORY['Movies'] = {}
		self.HISTORY['Series'] = {}
		self.HISTORY['Music'] = {}
		return self.HISTORY
	def _list_series(self, series_name=None, season=None, return_seasons_as_int=False):
		out = {}
		names = os.listdir(self.SERIES_DIR)
		if series_name is None:
			targets = names
		else:
			targets = [series_name]
		for series_name in targets:
			if series_name in names:
				out[series_name] = {}
				path = os.path.join(self.SERIES_DIR, series_name)
				if not os.path.isdir(path):
					print(f"Not a directory: {path}")
				else:
					dirs = os.listdir(path)
					if season is None:
						if return_seasons_as_int:
							seasons = [d.split('S')[1] for d in dirs]
						else:
							seasons = dirs
					else:
						seasons = [season]
					for s in seasons:
						if 'S' in str(s):
							sint = int(s.split('S')[1])
						out[series_name][sint] = {}
						path = os.path.join(self.SERIES_DIR, series_name, s)
						files = os.listdir(path)
						for filepath in files:
							en = filepath.split(f"{s}E")[1].split('.')[0]
							if '-' in str(en):
								n1 = int(en.split('-')[0])
								n2 = int(en.split('-E')[1])
								en = ",".join(self._get_list_range(n1, n2))
							else:
								en = int(en)
							out[series_name][sint][en] = {}
							out[series_name][sint][en]['series_name'] = series_name
							out[series_name][sint][en]['season'] = sint
							out[series_name][sint][en]['episode_number'] = en
							out[series_name][sint][en]['filepath'] = os.path.join(path, filepath)
							out[series_name][sint][en]['media_type'] = 'Series'
		return out
	def _list_movies(self, title=None, year=None):
		out = {}
		exts = ['.mkv', '.mp4', '.avi', '.mpg', '.mov', '.flv', '.swf']
		if title is not None:
			names = [title]
		else:
			names = os.listdir(self.MOVIES_DIR)
		for name in names:
			path = os.path.join(self.MOVIES_DIR, name)
			files = os.listdir(path)
			for filepath in files:
				ext = os.path.splitext(filepath)[1]
				if ext in exts:
					title = filepath.split(' (')[0]
					try:
						year = filepath.split(' (')[1].split(')')[0]
					except Exception as e:
						print(f"{e}: {filepath}")
						year = None
					out[title] = {}
					out[title]['title'] = title
					out[title]['year'] = year
					out[title]['filepath'] = os.path.join(path, filepath)
		return out
	def _get_list_range(self, start_num, end_num):
		l = []
		for i in range(start_num, end_num+1):
			l.append(str(i))
		return l
	def get_movies(self, title=None, year=None):
		objects = {}
		movies = self._list_movies()
		for title in movies:
			objects[title] = Media(data=movies[title])
		return objects
	def get_series(self, filter_by_name=None, active_series=None):
		"""
		main getter function for populating playlist object with series.
		Uses self.ACTIVE_SERIES (defaults as all in media list) to filter active/inactive
		playlist items and only returns those in the ACTIVE_SERIES list.
		TODO - Add this to movie series/sagas/trilogies/etc.
		"""
		series = self._list_series()
		if active_series is None:
			try:
				active_series = self.ACTIVE_SERIES
			except:
				print("Series names list not provided to playlist object. Initializing as *...")
				self.ACTIVE_SERIES = list(series.keys())
				active_series = self.ACTIVE_SERIES
		else:
			self.ACTIVE_SERIES = active_series
		objects = {}
		for series_name in active_series:
			objects[series_name] = {}
			for season in series[series_name]:
				objects[series_name][season] = {}
				for episode_number in series[series_name][season]:
					d = series[series_name][season][episode_number]
					objects[series_name][season][episode_number] = Media(data=d)
		if filter_by_name is not None:
			out = {}
			out[filter_by_name] = obects[filter_by_name]
			return out
		else:
			return objects
	def _get_random_series(self):
		names = self._list_series()
		ct = len(names)
		return random.randint(1, ct)
	def _filter_objects(self, key, val=None):
		l = []
		for name in self.SERIES:
			for s in self.SERIES[name]:
				for en in self.SERIES[name][s]:
					d = self.SERIES[name][s][en]
					keys = list(d.__dict__.keys())
					if key in keys:
						if val is not None:
							if d.__dict__[key] == val:
								print("Match:", key, val)
								l.append(d)
						else:
							l.append(d)
		for t in self.MOVIES:
			d = self.MOVIES[t]
			keys = list(d.__dict__.keys())
			if key in keys:
				if val is not None:
					if d.__dict__[key] == val:
						print("Match:", key, val)
						l.append(d)
				else:
					l.append(d)
		return l
	def filter_objects(self, objects=None, data={}, **kwargs):
		out = []
		if objects is not None:
			objs = objects
		else:
			objs = self._get_all()
		if len(kwargs) > 0:
			for k in kwargs:
				if k == 'key':
					k = kwargs[k]
					data[k] = None
				else:
					data[k] = kwargs[k]
		keys = list(data.keys())
		ct = len(keys)
		for o in objs:
			l = []
			hits = 0
			for key, val in data.items():
				if o.match(key=key, val=val):
					hits += 1
					l.append(o)
			if hits == ct:
				for i in l:
					if i not in out:
						out.append(i)
		return out
	def sort_movies(self):
		l = sorted([m for m in list(self.MOVIES.keys())])
		return [self.MOVIES[i] for i in l]
	def sort_series_names(self):
		return sorted([sn for sn in list(self.SERIES.keys())])
	def sort_seasons(self, series_name):
		return sorted([s for s in list(self.SERIES[series_name].keys())])
	def sort_episode_numbers(self, series_name, season):
		return sorted([en for en in list(self.SERIES[series_name][season].keys())])
	def get_first_s_en_series(self, series_name=None):
		if series_name is None:
			print(f"No series name provided! Randomizing...")
			series_name = self.get_random_series_name()
		season = self.sort_seasons(series_name=series_name)[0]
		en = self.sort_episode_numbers(series_name=series_name, season=season)[0]
		return self.SERIES[series_name][season][en]
	def get_random_series_name(self):
		names = self.sort_series_names()
		random.shuffle(names)
		return names[0]
	def get_last_played_series(self, series_name):
		try:
			return self.HISTORY['Series'][series_name]
		except Exception as e:
			print(f"Series not in history ({series_name}) {e}. Starting with first...")
			obj = self.get_first_s_en_series(series_name=series_name)
			self.HISTORY['Series'][series_name] = obj
			return obj
	def save_history(self, history=None):
		if history is not None:
			self.HISTORY = history
		d = {}
		for media_type in self.HISTORY:
			d[media_type] = {}
			for t in self.HISTORY[media_type]:
				obj = self.HISTORY[media_type][t]
				d[media_type][t] = obj.__dict__
		with open('mediaplayer_history.dat', 'wb') as f:
			pickle.dump(d, f)
			f.close()
	def load_history(self):
		h = {}
		with open('mediaplayer_history.dat', 'rb') as f:
			data = pickle.load(f)
			f.close()
		for media_type in data:
			h[media_type] = {}
			for t in data[media_type]:
				h[media_type][t] = Media(data[media_type][t])
		self.HISTORY = h
		return h
	def get_random_type(self, types=['Movies', 'Series']):
		random.shuffle(types)
		return types[0]
	def get_random_movie(self):
		movies = list(self.MOVIES.values())
		random.shuffle(movies)
		return movies[0]
	def _get_all(self):
		l = []
		for sn in self.SERIES:
			for s in self.SERIES[sn]:
				for en in self.SERIES[sn][s]:
					l.append(self.SERIES[sn][s][en])
		for t in self.MOVIES:
			l.append(self.MOVIES[t])
		return l

	def get_next_playback_type(self):
		t = self.ACTIVE_PLAYBACK_TYPES
		random.shuffle(t)
		return t[0]

	def get_next_movies(self, title=None, obj=None):
		"""
		gets the next movie from list to play.
			if no object provided, randomize list and return first.
			if object provided, assume from history and use to split movie titles and select next (for series progression, not yet implemented)
		"""
		if obj is None:
			if title is not None:
				return self.PLAYLIST.MOVIES[title]
			titles = sorted(list(self.PLAYLIST.MOVIES.keys()))
			random.shuffle(titles)
			return self.PLAYLIST.MOVIES[titles[0]]
		else:
			objects = list(self.PLAYLIST.MOVIES.values())
			idx = objects.index(obj)+1
			try:
				return objects[idx]
			except Exception as e:
				print(f"End of movie list reached! Returning 0...")
				return objects[0]

	def get_next_music(self):
		pass

	def get_random_series_name(self):
		names = list(self.SERIES.keys())
		random.shuffle(names)
		return names[0]

	def get_last_episode(self, series_name):
		try:
			return self.HISTORY[series_name]
		except Exception as e:
			print(f"Series not in history. Grabbing last to increment to first..")
			seasons = sorted(list(self.SERIES[series_name].keys()))
			sidx = len(seasons)-1
			season = seasons[sidx]
			ens = sorted(list(self.SERIES[series_name][season].keys()))
			eidx = len(ens)-1
			en = ens[eidx]
			return self.SERIES[series_name][season][en]

	def _get_seasons(self, series_name):
		return sorted(list(self.SERIES[series_name].keys()))

	def _get_episodes(self, series_name, season):
		return sorted(list(self.SERIES[series_name][season].keys()))

	def get_next_season(self, series_name, season):
		seasons = self._get_seasons(series_name=series_name)
		try:
			return seasons[seasons.index(season)+1]
		except Exception as e:
			print(f"End of season list? {e}")
			return seasons[0]	
	

	def get_next_episode(self, series_name, season, episode_number):
		ens = self._get_episodes(series_name=series_name, season=season)
		eidx = ens.index(episode_number)+1
		if len(ens) == eidx:
			print("Reached end of season!")
			season = self.get_next_season(series_name=series_name, season=season)
			ens = self._get_episodes(series_name=series_name, season=season)
			en = ens[0]
		else:
			en = ens[eidx]
		print("Set episode:", season, en)
		return self.SERIES[series_name][season][en]


	def get_next_series(self, obj=None, series_name=None):
		def get_from_history(series_name):
			try:
				return self.HISTORY['Series'][series_name]
			except:
				print("Series not in history:", series_name)
				return self.get_last_episode(series_name=series_name)
		if obj is None:
			if series_name is None:
				series_name = self.get_random_series_name()
			try:
				obj = self.HISTORY['Series'][series_name]
			except Exception as e:
				series_name = self.get_random_series_name()
				obj = self.get_last_episode(series_name=series_name)
				print(f"Error - {e}")
		return self.get_next_episode(series_name=obj.series_name, season=obj.season, episode_number=obj.episode_number)		

	def get_next(self, query=None, media_type=None):
		if media_type is None:
			media_type = self.get_next_playback_type()
		if media_type == 'Series':
			return self.get_next_series(series_name=query)
		elif media_type == 'Movies':
			return self.get_next_movies(title=query)
		elif media_type == 'Music':
			return self.get_next_music()




class Player():
	def __init__(self, width=None, height=None, cache_size=6000, scale_video=1.0, run_mainloop=False, new_player_window=True, vlc_verbosity=0, fullscreen=False):
		"""
		Main player class
		args:
			keyboard_events - if True, will eventually capture and react to keyboard events. STILL IN PROGRESS, NOT YET IMPLEMENTED.
			run_mainloop - if True, runs tkinter.Tk().mainloop after all else is done. Currently unused (default=False)
			new_player_window - whether or not to show player window. set to False to init player with no tkinter viewer window
		"""
		self.SCALE = scale_video
		self.FULLSCREEN = fullscreen
		self.PLAY_NEXT = None
		self.EVENT = None
		self.DATA_DIR = os.path.join(os.path.expanduser("~"), '.nplayerv2')
		if not os.path.exists(self.DATA_DIR):
			os.makedirs(self.DATA_DIR, exist_ok=True)
		self.CONF_PATH = os.path.join(self.DATA_DIR, 'settings.conf')
		self.STATE = 'Unloaded'
		if width is None and height is None:
			width, height = get_screen_res()
		self.WIDTH = width
		self.HEIGHT = height
		#opts = '--no-xlib --audio-filter=normvol --norm-buff-size=20 --norm-max-level=2'
		self.CACHE_SIZE = cache_size
		self.VLC_VERBOSITY = vlc_verbosity
		self.VLC_OPTIONS = f"--verbose={self.VLC_VERBOSITY} --file-caching={self.CACHE_SIZE} --network-caching={self.CACHE_SIZE}"
		self.VLC = vlc.Instance(self.VLC_OPTIONS)
		self.PLAYER = self.VLC.media_player_new()
		if new_player_window:
			self.VIEWER = tk.Tk()
			self.STATUS_STRINGVAR = tk.Stringvar(self.VIEWER, value=self.STATE)
			self.VIEWER.config(menu=self.get_menu())
			self.VIEWER.title("Media Player")
			w, h = get_screen_res()
			self.VIEWER.geometry(f"{w}x{h}")
			self.VIEWER.bind("<Configure>", self.set_scale)
			frame = tk.Frame(self.VIEWER, width=w, height=h, bg='black')
			#frame = tk.Frame(self.VIEWER, width=self.WIDTH, height=self.HEIGHT, bg='black')
			#frame.pack(fill="both", expand=True)
			frame.pack()
			self.VIEWER.update() # Important to update to ensure the window is created
			self.VIEWER_WINDOW_ID = frame.winfo_id()
			self.PLAYER.set_xwindow(self.VIEWER_WINDOW_ID)
		self.attach_events()
		self.EVENTS = {260: 'Playing', 261: 'Paused', 262: 'Stopped', 265: 'Playback Ended'}
		self.ALL_EVENTS = [i for i in dir(vlc.Event().type) if '_' not in i]
		self.ACTIVE_SERIES = None
		config = self.get_config(apply_changes=True)
		try:
			self.ACTIVE_SERIES = config['ACTIVE_SERIES']
		except:
			config['ACTIVE_SERIES'] = self.ACTIVE_SERIES
			self.save_current_config(config)
		#print("Allowing vlc to load, 5 seconds!")
		#self.wait(5)
		self.PLAYLIST = Playlist(active_series=self.ACTIVE_SERIES)
		if self.PLAY_NEXT is None:
			self.PLAY_NEXT = self.PLAYLIST.NEXT
		self.ACTIVE_SERIES = self.PLAYLIST.ACTIVE_SERIES
		if run_mainloop:
			self.start_loop()
			self.VIEWER.mainloop()
	def get_menu(self):
		menubar = tk.Menu(self.VIEWER)
		controlls_menu = tk.Menu(menubar, tearoff=0) # tearoff=0 prevents a detachable menu
		edit_menu = tk.Menu(menubar, tearoff=0)
		menubar.add_cascade(label="Controlls", menu=controlls_menu)
		menubar.add_cascade(label="Edit", menu=edit_menu)
		controlls_menu.add_command(label="Play/Pause", command=lambda: self.pause())
		controlls_menu.add_command(label="Skip Next", command=lambda: self.playnext())
		controlls_menu.add_command(label="Fullscreen", command=lambda: self.toggle_fullscreen())
		controlls_menu.add_separator() # Add a separator line
		controlls_menu.add_command(label="Toggle Mute", command=lambda: self.PLAYER.audio_toggle_mute())
		controlls_menu.add_separator() # Add a separator line
		controlls_menu.add_command(label="Volume Up", command=lambda: self.PLAYER.audio_set_volume(self.PLAYER.audio_get_volume()+10))
		controlls_menu.add_command(label="Volume Down", command=lambda: self.PLAYER.audio_set_volume(self.PLAYER.audio_get_volume()-10))
		controlls_menu.add_command(label="Exit", command=exit)
		edit_menu.add_command(label="Set Active Series", command=edit_active_series)
		edit_menu.add_command(label="Pirate Bay Downloader", command=lambda: print("NOT IMPLEMENTED"))
		edit_menu.add_command(label="Metadata Tag Editor", command=lambda: print("NOT IMPLEMENTED"))
		return menubar
	def _set_attr(self, key, value):
		self.__dict__[key] = value
		config = self.get_config(apply_changes=False)
		config[key] = value
		self.save_current_config(config=config)
		print("Attribute set!", key, value)
	def get_resolution_nowPlaying(self):
		try:
			width, height = self.PLAYER.video_get_size()
		except Exception as e:
			print(f"Unable to get resolution: (Nothing playing???")
			width, height = 1024, 768
		return width, height
	def setResolution(self, width=None, height=None, fullscreen=None):
		if fullscreen is not None:
			self._set_attr(key='FULLSCREEN', value=fullscreen)
			if fullscreen:
				width, height = get_screen_res()
			else:
				width, height = self.get_resolution_nowPlaying()
		else:
			if not self.FULLSCREEN:
				w, h = self.get_resolution_nowPlaying()
			else:
				w, h = get_screen_res()
			if width is None:
				width = w
			if height is None:
				height = h
		self._set_attr(key='WIDTH', value=width)
		self._set_attr(key='HEIGHT', value=height)
		print(f"Resolution set: {self.WIDTH}x{self.HEIGHT} ({width}, {height})")
		return width, height
	def wait(self, secs=2):
		time.sleep(secs)
	def get_scale(self, vidres=None, sres=None):
		pcnt = 0
		if vidres is None:
			vidres = self.get_resolution_nowPlaying()
		if sres is None:
			#sres = get_screen_res()
			sres = self.VIEWER.winfo_width(), self.VIEWER.winfo_height()
		if vidres[0] >= sres[0] and vidres[1] >= sres[1]:
			w, h = sres
			w2, h2 = vidres
		else:
			w, h = vidres
			w2, h2 = sres
		if w > h:
			pcnt = w / w2
		elif h > w:
			pcnt = h / h2
		elif h == w:
			pcnt = w / w2
		else:
			print(w, h, w2, h2)
		return pcnt
	def set_scale(self, scale=None):
		if scale is None:
			scale = self.get_scale()
		if str(type(scale)) == "<class 'tkinter.Event'>":
			scale = self.get_scale()
		self.PLAYER.video_set_scale(scale)
		self.SCALE = scale
	def set_active_series(self, series_names=None):
		self.ACTIVE_SERIES = series_names
		conf = self.load_config()
		conf['ACTIVE_SERIES'] = self.ACTIVE_SERIES
		self.save_current_config(config=conf)
		print("Active series updated!")
	def load_config(self):
		with open(self.CONF_PATH, 'rb') as f:
			config = pickle.load(f)
			f.close() 
		return config
	def get_config(self, apply_changes=False):
		try:
			conf = self.load_config()
		except Exception as e:
			print(f"Unable to load config file! Re-initializing...")
			conf = self._init_config()
		if apply_changes:
			self.apply_config(config=conf)
		if type(conf) == list:
			print("conf was list of tuples, converted to dict!")
			conf = dict(conf)
		return conf
	def _init_config(self):
		d = {}
		d['ALL_PLAYBACK_TYPES'] = ['Movies', 'Series', 'Music']
		d['ACTIVE_PLAYBACK_TYPES'] = ['Series']
		d['SHUFFLE_TYPES'] = ['Random', 'Series', None]
		d['DATA_DIR'] = self.DATA_DIR
		d['CONF_PATH'] = self.CONF_PATH
		d['PLAY_NEXT'] = None
		d['NOW_PLAYING'] = None
		d['MUTE'] = False
		d['ACTIVE_SERIES'] = self.ACTIVE_SERIES
		d['VLC_VERBOSITY'] = 0
		d['CACHE_SIZE'] = 6000
		d['FULLSCREEN'] = False
		return d
	def save_current_config(self, config=None):
		if config is None:
			types = [None, bool, str, int, list, dict]
			config = [(k, v) for k, v in self.__dict__.items() if type(v) in types]
		with open(self.CONF_PATH, 'wb') as f:
			pickle.dump(config, f)
			f.close() 
		print("Current config exported and saved!")
	def apply_config(self, config=None):
		if config is None:
			print("Configuration dictionary not provided")
			config = self.__dict__
		for k in config:
			if type(k) == tuple:
				key, v = k
				self._set_attr(key=key, value=v)
				#self.__dict__[key] = v
				#print("Attribute set:", key, v)
			else:
				#print("k:", k)
				self._set_attr(key=k, value=config[k])
				#self.__dict__[k] = config[k]
				#print("Attribute set:", k, config[k])
		print("Config applied!")
	def event_callback(self, event):
		e = str(event.type)
		if e == 'EventType.MediaMPPlaying' or e == 'EventType.MediaPlayerPlaying':
			self.STATE = 'Playing'
		elif e == 'EventType.MediaMPPaused' or e == 'EventType.MediaPlayerPaused':
			self.STATE = 'Paused'
		elif e == 'EventType.MediaMPStopped' or e == 'EventType.MediaPlayerStopped':
			print("Stop event received. Current value:", self.STATE)
			self.STATE = 'Stopped'
		elif e == 'EventType.MediaMPEndReached' or e == 'EventType.MediaPlayerEndReached':
			self.STATE = 'Playback Ended'
		elif e == 'EventType.MediaMPEncounteredError' or e == 'EventType.MediaPlayerEncounteredError':
			print(f"Error on playback!")
			self.STATE = 'Stopped'
		print("State changed:", self.STATE)
		return self.STATE
	def attach_events(self, events=None):
		if events is None:
			events = ['260:EventType.MediaMPPlaying', '261:EventType.MediaMPPaused', '262:EventType.MediaMPStopped', '265:EventType.MediaMPEndReached']
		for evt in events:
			evid = int(evt.split(':')[0])
			event = vlc.EventType(evid)
			self.PLAYER.event_manager().event_attach(event, self.event_callback)
	def play(self, obj=None, filepath=None):
		if obj is None:
			if filepath is not None:
				self.PLAY_NEXT = filepath
				data = self.PLAYLIST._get_info(filepath=self.PLAY_NEXT)
				obj = Media(data)
			else:
				print("object is None! Getting next from playlist...")
				obj = self.PLAYLIST.get_next()
		if obj.media_type == 'Series':
			self.PLAYLIST.HISTORY[obj.media_type][obj.series_name] = obj
			self.PLAYLIST.save_history(self.PLAYLIST.HISTORY)
		elif obj.media_type == 'Movies':
			self.PLAYLIST.HISTORY[obj.media_type][obj.title] = obj
			self.PLAYLIST.save_history(self.PLAYLIST.HISTORY)
		elif obj.media_type == 'Music':
			self.PLAYLIST.HISTORY[obj.media_type][obj.title] = obj
			self.PLAYLIST.save_history(self.PLAYLIST.HISTORY)
		media = self.VLC.media_new(obj.filepath)
		self.PLAYER.set_media(media)
		#self.wait(2)
		#self.PLAYER.video_set_key_input(self.KEYBOARD)
		self.set_scale(0.5)
		self.PLAYER.play()
		self.NOW_PLAYING = obj
		self.set_scale()
		print(f"Now Playing: {self.NOW_PLAYING.__str__()}")
	def playnext(self, query=None, media_type=None):
		self.play(self.PLAYLIST.get_next(query=query, media_type=media_type))
	def stop(self):
		self.PLAYER.stop()
	def pause(self):
		self.PLAYER.pause()
		print("Pause triggered!")
	def toggle_fullscreen(self, val=None):
		if val is None:
			val = self.PLAYER.get_fullscreen()
			if val == 1:
				val = 0
			elif val == 0:
				val = 1
		self.PLAYER.set_fullscreen(val)
		self.VIEWER.attributes("-fullscreen", val)
		self.FULLSCREEN = val
		print("Fullscreen toggled:", self.FULLSCREEN)
	def loop(self):
		def get_play_type():
			types = self.ACTIVE_PLAYBACK_TYPES
			random.shuffle(types)
			return types[0]
		self.RUN = True
		media_type = get_play_type()
		while self.RUN:
			if self.STATE == 'Unloaded':
				self.playnext(media_type=media_type)
				self.LAST_STATE = self.STATE
			if self.STATE is not None and self.STATE != self.LAST_STATE:
				print("Loop state changed:", self.STATE)
				self.LAST_STATE = self.STATE
			if self.STATE == 'Playback Ended':
				self.STATE = None
				self.playnext(media_type=media_type)
			if self.EVENT == 'Stop':
				print("Stop event received!")
				self.stop()
			elif self.EVENT == 'Play':
				print("Play event received!")
				self.PLAYER.play()
			elif self.EVENT == 'Pause':
				print("Pause event received!")
				self.PLAYER.pause()
			elif self.EVENT == 'SkipNext':
				print("Skip next received!")
				self.playnext()
			elif self.EVENT == 'SkipPrevious':
				print("Unhandled event!", self.EVENT)
			elif self.EVENT == 'Exit':
				print("loop exiting...")
				self.save_current_config()
				self.RUN = False
				break
			elif self.EVENT == 'Fullscreen':
				if self.FULLSCREEN:
					self.FULLSCREEN = False
				else:
					self.FULLSCREEN = True
				self.toggle_fullscreen(val=self.FULLSCREEN)
			elif self.EVENT == 'Mute':
				if self.MUTE:
					self.MUTE = False
				else:
					self.MUTE = True
				self.PLAYER.audio_set_mute(self.MUTE)
				print("Mute toggled:", self.MUTE)
	def start_loop(self, daemon=True):
		self.THREAD = threading.Thread(target=self.loop)
		self.THREAD.daemon = daemon
		self.THREAD.start()
		print("Thread started!")
		#self.VIEWER.mainloop()


if __name__ == "__main__":
	import sys
	try:
		media_type = sys.argv[1]
	except:
		media_type = 'Series'
	try:
		query = sys.argv[2]
	except:
		query = None
	p = Player(run_mainloop=True)


