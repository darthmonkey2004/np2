#!/usr/bin/python3

import threading
import pickle
import random
import os
import vlc
import time
import sys
import subprocess
#P.set_xwindow(UI.WINDOW2['-VID_OUT-'].Widget.winfo_id())
import tkinter as tk
from tkinter import ttk, filedialog
p = None

"""
Destop launcher data: ("$USER/.local/share/applications/np.desktop")
---------------
[Desktop Entry]
		Version=1.0
		Name=NPlayer V2
		Comment=Media player/downloader/metadata manager for python3 (tkinter)
		Exec=/home/monkey/mediaplayer.py > ~/.nplayerv2/log.txt
		Path=/home/monkey/.nplayerv2
		Icon=/home/monkey/.nplayerv2/Media_Player.png
		Terminal=false
		Type=Application
		Categories=Utility;Development;

"""

class Searcher():
	def __init__(self, filepath=None):
		self.filepath = filepath
	def search_series(self, series_name, season=None, episode_number=None):
		url = f"http://www.omdbapi.com/?apikey=8aa45e85"
		out = {}
		media_type = 'Series'
		r = requests.get(f"{url}&t={series_name.replace(' ', '+')}&type=series")
		data = r.json()
		imdbid = data['imdbID']
		series_name = data['Title']
		year = data['Year']
		plot = data['Plot']
		poster = data['Poster']
		out[series_name] = {}
		if season is not None:
			seasons = [season]
		else:
			seasons = data['totalSeasons']
		for season in seasons:
			out[series_name][season] = {}
			r = requests.get(f"{url}&i={imdbid}&season={season}&type=episode")
			ret = r.json()
			for line in ret['Episodes']:
				episode_name, episode_number, release_date = line['Title'], line['Episode'], line['imdbID'], line['Released']
				out['media_type'] = media_type
				out['imdbid'] = imdbid
				out['series_name'] = series_name
				out['season'] = season
				out['episode_number'] = episode_number
				out['episode_name'] = episode_name
				out['release_date'] = release_date
				out['year'] = year
				out['plot'] = plot
				out['poster'] = poster
				out[series_name][season][episode_number] = out
		return out
	def search_movies(self, title, year=None):
		url = f"http://www.omdbapi.com/?apikey=8aa45e85"
		title = title.replace(' ', '+')
		if year is None:
			r = requests.get(f"{url}&t={title}&type=movie")
		else:
			r = requests.get(f"{url}&t={title}&type=movie&year={year}")
		out = {}
		data = r.json()
		return {'title': data['Title'], 'year': data['Year'], 'release_date': data['Released'], 'plot': data['Plot'], 'poster': data['Poster'], 'imdbid': data['imdbID']}
	def search_by_filepath(self, filepath=None):
		info = MediaGuesser(filepath=filepath).get_info_from_filepath(filepath)
		if filepath is None:
			filepath = self.filepath
		media_type = MediaGuesser(filepath=filepath).guess_media_type(os.path.basename(filepath))
		if media_type == 'Series':	
			return self.search_series(info['series_name'], season=info['season'], episode_number=info['episode_number'])
		elif media_type == 'Movies':
			return self.search_movies(info['title'], year=info['year'])
		else:
			print("Not movie or series! Search will fail, skipping...")
			return {'filepath': filepath, 'media_type': media_type}
		

class DataPoller():
	"""
	this class handles polling the player object to retreive playback states
	and media details.
	poll() - grabs all data
	get(key): returns a specific value from all data.
	The following still need finished...

	audio_setters = ['audio_output_device_set', 'audio_output_set', 'audio_set_callbacks', 'audio_set_channel', 'audio_set_delay', 'audio_set_format', 'audio_set_format_callbacks', 'audio_set_mute', 'audio_set_track', 'audio_set_volume', 'audio_set_volume_callback', 'audio_toggle_mute']
	setters = ['set_agl', 'set_android_context', 'set_chapter', 'set_equalizer', 'set_evas_object', 'set_fullscreen', 'set_hwnd', 'set_media', 'set_mrl', 'set_nsobject', 'set_pause', 'set_position', 'set_rate', 'set_renderer', 'set_role', 'set_time', 'set_title', 'set_video_title_display', 'set_xwindow']
	video_getters = ['get_full_chapter_descriptions', 'get_full_chapter_descriptions', 'get_full_title_descriptions', 'video_get_marquee_int', video_get_marquee_string', 'video_get_title_description']
	"""
	def __init__(self, player):
		self.player = player
		self.DATA = None
	def poll(self):
		"""
		grabs all data and organizes into dictionary. to filter, use 'get(<filter_query>)'
		"""
		out = {}
		out['video'] = self.get_video_data()
		out['audio'] = self.get_audio_data()
		out['player'] = self.get_player_data()
		return out
	def get_player_data(self, export=False):
		"""
		gets player data from current player object.
		"""
		player_getters = ['get_agl', 'get_chapter', 'get_chapter_count', 'get_chapter_count_for_title', 'get_fps', 'get_full_chapter_descriptions', 'get_full_title_descriptions', 'get_fullscreen', 'get_hwnd', 'get_instance', 'get_length', 'get_media', 'get_nsobject', 'get_position', 'get_rate', 'get_role', 'get_state', 'get_time', 'get_title', 'get_title_count', 'get_xwindow']
		out = {}
		for g in player_getters:
			if g == 'get_agl':
				f = self.player.get_agl
			elif g == 'get_chapter':
				f = self.player.get_chapter
			elif g == 'get_chapter_count':
				f = self.player.get_chapter_count
			elif g == 'get_chapter_count_for_title':
				f = self.player.get_chapter_count
			elif g == 'get_fps':
				f = self.player.get_fps
			elif g == 'get_fullscreen':
				f = self.player.get_fullscreen
			elif g == 'get_hwnd':
				f = self.player.get_hwnd
			elif g == 'get_length':
				f = self.player.get_length
			elif g == 'get_media':
				f = self.player.get_media
			elif g == 'get_nsobject':
				f = self.player.get_nsobject
			elif g == 'get_position':
				f = self.player.get_position
			elif g == 'get_rate':
				f = self.player.get_rate
			elif g == 'get_role':
				f = self.player.get_role
			elif g == 'get_state':
				f = self.player.get_state
			elif g == 'get_time':
				f = self.player.get_time
			elif g == 'get_title':
				f = self.player.get_title
			elif g == 'get_title_count':
				f = self.player.get_title_count
			elif g == 'get_xwindow':
				f = self.player.get_xwindow
			try:
				out[g] = f()
			except Exception as e:
				out[g] = f"FAILED:{e}"
				print("error getting player data:", e)
		if export:#if exporting, delete live Media obect from dict (un-pickle-able)
			del out['get_media']
		return out
	def get_audio_data(self, export=False):
		"""
		gets audio data from currently playing player object
		"""
		audio_getters = ['audio_get_track_count', 'audio_get_track_description', 'audio_get_volume', 'audio_output_device_enum', 'audio_output_device_get']
		out = {}
		for g in audio_getters:
			if g == 'audio_get_track_count':
				f = self.player.audio_get_track_count
			elif g == 'audio_get_track_description':
				f = self.player.audio_get_track_description
			elif g == 'audio_get_volume':
				f = self.player.audio_get_volume
			elif g == 'audio_output_device_enum':
				f = self.player.audio_output_device_enum
			elif g == 'audio_output_device_get':
				f = self.player.audio_output_device_get
			out[g] = f()
		if export:#if exporting, remove live audio obect (like above)
			del out['audio_output_device_enum']
		return out
	def get_video_data(self):
		"""
		gets video data from currently playing player object.
		"""
		video_getters = ['video_get_marquee_int', 'video_get_marquee_string', 'video_get_scale', 'video_get_size', 'video_get_spu', 'video_get_spu_count', 'video_get_spu_delay', 'video_get_spu_description', 'video_get_teletext', 'video_get_title_description', 'video_get_track', 'video_get_track_count', 'video_get_track_description', 'video_get_width']
		out = {}
		f = None
		for g in video_getters:
			if g == 'video_get_scale':
				f = self.player.video_get_scale
			elif g == 'video_get_size':
				f = self.player.video_get_size
			elif g == 'video_get_spu':
				f = self.player.video_get_spu
			elif g == 'video_get_spu_count':
				f = self.player.video_get_spu_count
			elif g == 'video_get_spu_delay':
				f = self.player.video_get_spu_delay
			elif g == 'video_get_spu_description':
				f = self.player.video_get_spu_description
			elif g == 'video_get_teletext':
				f = self.player.video_get_teletext
			elif g == 'video_get_track':
				f = self.player.video_get_track
			elif g == 'video_get_track_count':
				f = self.player.video_get_track_count
			elif g == 'video_get_track_description':
				f = self.player.video_get_track_description
			elif g == 'video_get_width':
				f = self.player.video_get_width
			if f is not None:
				out[g] = f()
		return out
	def get(self, key):
		"""
		vlc player class getter
		filters .data by key to return one or more filtered parameters.
		"""
		data = self.poll()
		if key in list(data['audio'].keys()):
			return data['audio'][key]
		elif key in list(data['video'].keys()):
			return data['video'][key]
		elif key in list(data['player'].keys()):
			return data['player'][key]
		else:
			print(f"Unknown key: {key}!")
			return None

def get_screen_res():
	w, h = subprocess.check_output("xrandr | grep '*' | xargs | cut -d ' ' -f 1", shell=True).decode().strip().split('x')
	return int(w), int(h)
	

class MediaEditor():
	def __init__(self, obj, cols, rename_file=True):
		self.RENAME_FILE = rename_file
		self.obj = obj
		self.EDITOR = self.get_editor(cols=cols)
	def get_editor(self, cols):
		out = {}
		self.root = tk.Tk()
		#cols = m._get_columns(media_type=self.obj.media_type)
		for c in cols:
			out[c] = {}
			out[c]['label'] = tk.Label(self.root, text=c)
			out[c]['label'].pack()
			out[c]['entry'] = tk.Entry(self.root)
			try:
				v = self.obj.__dict__[c]
			except:
				v = f"Unknown {c.title()}"
			if v == "":
				v = f"Unknown {c.title()}"
			out[c]['entry'].insert(0, v)
			out[c]['entry'].pack()
		self.UPDATE_BTN = tk.Button(self.root, text='Update!', command=self.update_object)
		self.UPDATE_BTN.pack()
		self.CLOSE_BTN = tk.Button(self.root, text='Exit', command=exit)
		self.CLOSE_BTN.pack()
		return out
	def get_data(self):
		out = {}
		cols = list(self.EDITOR.keys())
		for c in cols:
			out[c] = self.EDITOR[c]['entry'].get()
		return out
	def update_object(self):
		data = self.get_data()
		for k in data:
			self.obj.__dict__[k] = data[k]
		if self.RENAME_FILE:
			self.obj.update_filepath(migrate=True)
		return self.obj

class MediaManager():
	def __init__(self, playlist=None):
		self.Guesser = MediaGuesser()
		if playlist is None:
			playlist = Playlist(init_empty=True)
		self.PLAYLIST = playlist
		self.MEDIA_MANAGER = tk.Tk()
		self.TREE = {}
		self.TREE['Series'] = self.get_tree(media_type='Series')
		self.TREE['Movies'] = self.get_tree(media_type='Movies')
		try:
			self.TREE['Music'] = self.get_tree(media_type='Music')
		except Exception as e:
			print(f"No music files??? {e}")
			self.TREE['Music'] = None
		self.build()
		self.obj = None

	def _get_column_series(self, sn='Solar Opposites', season=4, en=1):
		data = self.PLAYLIST.SERIES[sn][season][en]
		if isinstance(data, Media):
			data = dict(data.__dict__)
		return data

	def _get_column_movie(self, title):
		data = self.PLAYLIST.MOVIES[title]
		if isinstance(data, Media):
			data = dict(data.__dict__)
		return data

	def _get_column_music(self, filepath):
		data = self.PLAYLIST.MUSIC[filepath]
		if isinstance(data, Media):
			data = dict(data.__dict__)
		return data

	def _get_column_other(self, filepath):
		data = self.PLAYLIST.MOVIES[filepath]
		if isinstance(data, Media):
			data = dict(data.__dict__)
		return data

	def _get_columns(self, filepath=None, media_type=None):
		self.PLAYLIST.update()
		if media_type is None:
			media_type = self.Guesser.guess_media_type(filepath)
		if filepath is None:
			if media_type == 'Series':
				d = self.PLAYLIST.SERIES[list(self.PLAYLIST.SERIES.keys())[0]]
				season = list(d.keys())[0]
				en = list(d[season].keys())[0]
				if type(d[season][en]) == dict:
					return [k for k in list(d[season][en].keys()) if k != 'data']
				else:
					return [k for k in list(d[season][en].__dict__.keys()) if k != 'data']
			else:
				d = self.__dict__[media_type.upper()]
				return [k for k in list(list(d.values())[0].__dict__.keys()) if k != 'data']




		info = self.Guesser.get_info_from_filepath(filepath)
		if media_type == 'Series':
			return self._get_column_series(sn=info['series_name'], season=info['season'], en=info['episode_number'])
		elif media_type == 'Movies':
			return self._get_column_movie(title=info['title'])
		elif media_type == 'Music':
			#return self._get_column_music(filepath=filepath)
			return ['title', 'youtube_id', 'artist', 'album', 'filepath']
		elif media_type == 'Other':
			return self._get_column_other(filepath=filepath)
		else:
			print("Unhandled media type:", media_type, filepath, info)
	
			
	def get_tree(self, media_type='Series', columns=None):
		if columns is None:
			columns = self._get_columns(media_type=media_type)
		print("columns:", columns)
		t = ttk.Treeview(self.MEDIA_MANAGER, show='headings', columns=columns)
		if media_type == 'Series':
			t.bind("<<TreeviewSelect>>", self.series_tree_selected)
		elif media_type == 'Movies':
			t.bind("<<TreeviewSelect>>", self.movies_tree_selected)
		elif media_type == 'Music':
			t.bind("<<TreeviewSelect>>", self.music_tree_selected)
		for c in columns:
			print("c, text:", c)
			t.heading(c, text=c)
		t.pack(fill="both", expand=True)
		return t
	def add_item(self, obj):
		cols = self._get_columns(media_type=obj.media_type)
		t = self.TREE[obj.media_type]
		vals = []
		for c in cols:
			try:
				vals.append(obj.__dict__[c])
			except:
				vals.append("Unknown")
				print("Key not found:", c)
		t.insert("", tk.END, values=tuple(vals))
	def build_series_tree(self):
		for series_name in self.PLAYLIST.SERIES:
			for season in self.PLAYLIST.sort_seasons(series_name):
				for en in self.PLAYLIST.sort_episode_numbers(series_name, season):
					try:
						obj = self.PLAYLIST.SERIES[series_name][season][en]
						self.add_item(obj)
					except Exception as e:
						print(f"Error adding series object: {e}, {obj.filepath}")
	def build_movies_tree(self):
		for title in self.PLAYLIST.MOVIES:
			obj = self.PLAYLIST.MOVIES[title]
			self.add_item(obj)
	def build_music_tree(self):
		for title in self.PLAYLIST.MUSIC:
			obj = self.PLAYLIST.MUSIC[title]
			self.add_item(obj)
	def build(self):
		self.build_series_tree()
		self.build_movies_tree()
		self.build_music_tree()
	def series_tree_selected(self, event):
		d = self.TREE['Series'].item(self.TREE['Series'].selection())
		vals = d['values']
		sn = vals[0]
		s = vals[1]
		en = vals[2]
		self.obj = self.PLAYLIST.SERIES[sn][s][en]
		cols = self._get_columns(media_type=self.obj.media_type)
		self.editor = MediaEditor(obj=self.obj, cols=cols)
		return self.obj
	def movies_tree_selected(self, event):
		d = self.TREE['Movies'].item(self.TREE['Movies'].selection())
		vals = d['values']
		self.obj = self.PLAYLIST.MOVIES[vals[0]]
		self.editor = MediaEditor(obj=self.obj)
		return self.obj
	def music_tree_selected(self, event):
		d = self.TREE['Music'].item(self.TREE['Music'].selection())
		vals = d['values']
		self.obj = self.PLAYLIST.MUSIC[vals[0]]
		self.editor = MediaEditor(obj=self.obj)
		return self.obj


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
		l = sl = self._get_list(0, 100)
		eps = [f"E{i}" for i in l]
		eps += [f"S0{i}" for i in self._get_list(0, 9)]
		seasons = [f"S{i}" for i in l]
		seasons += [f"S0{i}" for i in self._get_list(0, 9)]
		out = []
		for s in seasons:
			for e in eps:
				out.append(f"{s}{e}")
		return out
	def se_isin(self, filepath, return_data=False):
		out = []
		for s in self._get_seasons():
			if s in filepath:
				if not return_data:
					return True
				else:
					out.append(s)
		out.sort(key=len, reverse=True)
		try:
			return out[0]
		except:
			return None
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
		if '.mp3' in filepath or '.wav' in filepath:
			if not return_data:
				return 'Music'
			else:
				return os.path.splitext(os.path.basename(filepath))[0]
		else:
			if not return_data:
				return 'Other'
			else:
				return filepath

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
			if '.' in os.path.splitext(filepath)[0]:
				splitter = f".{s}"
			else:
				splitter = s
			out['series_name'] = fname.split(splitter)[0].strip()
			out['season'] = s.split("S")[1].split("E")[0]
			print("out:", out)
			if str(out['season'])[0] == '0' and int(out['season']) != 0:
				out['season'] = int(str(out['season'])[1:])
			else:
				out['season'] = int(out['season'])
			out['episode_number'] = int(s.split('E')[1])
		return out

class Media():
	def __init__(self, **data):
		t = list(data.values())[0]
		if isinstance(t, Media):
			data = t.__dict__
			self.data = data
		else:
			self.data = data
		for k in data:
			self.__dict__[k] = data[k]
		try:
			#print("Media created as type:", self.media_type)
			mt = self.media_type
		except:
			try:
				self.media_type = MediaGuesser().guess_media_type(filepath=self.filepath)
				print("Media type not provided! Guessing...", self.media_type)
			except Exception as e:
				print("Couldn't get media type! data dict might be incomplete...")
				print("data:", data)
	def _update_filepath_series(self):
		ext = os.path.splitext(self.filepath)[1].split('.')[1]
		path = os.path.dirname(self.filepath)
		media_dir = self.th.split(self.series_name)[0]
		newdir = os.path.join(media_dir, self.series_name, f"S{self.season}")
		fname = f"{self.series_name}.S{self.season}E{self.episode_number}.{ext}"
		return os.path.join(newdir, fname)
	def _update_filepath_movies(self):
		ext = os.path.splitext(self.filepath)[1].split('.')[1]
		dirname = f"{self.title} ({self.year})"
		media_dir = os.path.join(self.filepath.split('Movies')[0], 'Movies')
		fname = f"{self.title} ({self.year}).{self.ext}"
		return os.path.join(media_dir, dirname, fname)
	def _update_filepath_music(self):
		ext = os.path.splitext(self.filepath)[1].split('.')[1]
		l = []
		l.append(self.title)
		if self.artist == '':
			self.artist = 'UNKNOWN_ARTIST'
		if self.album == '':
			self.album = 'UNKNOWN_ALBUM'
		try:
			l.append(self.artist)
		except:
			pass
		try:
			l.append(self.album)
		except:
			pass
		try:
			l.append(self.youtube_id)
		except:
			pass
		f = ".".join(l)
		fname = f"{f}.{ext}"
		media_dir = os.path.join(self.filepath.split('Music')[0], 'Music')
		return os.path.join(media_dir, fname)
	def update_filepath(self, migrate=False):
		if self.media_type == 'Series':
			f = self._update_filepath_series()
		elif self.media_type == 'Movies':
			f = self._update_filepath_movies()
		elif self.media_type == 'Music':
			f = self._update_filepath_music()
		if migrate:
			if self.filepath != f:
				com = f"mv '{self.filepath}' '{f}'"
				#print("command:", com)
				out = subprocess.check_output(com, shell=True).decode().strip()
				if out == '':
					self.filepath = f#if successfull, set attribute to new path after migration
				else:
					print(f"Error - Move failed! {out}")
					print("Command was:", com)
			else:
				print(f"File names are the same! Old:{self.filepath}, New:{f}")
				print("aborting file renaming...")
		return self.filepath
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
	def __init__(self, media_path='/media/monkey/usbhd/Media', playlist_file=None, playback_types=None, active_series=None, init_empty=False):
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
		self.Guesser = MediaGuesser()
		if playlist_file is not None:
			self.apply_playlist(playlistfile=playlist_file)
		else:
			if init_empty:
				self.ACTIVE_SERIES = []
				self.SERIES = {}
				self.MOVIES = {}
				self.MUSIC = {}
				self.OTHER = {}
				self.LAST = None
				self.NEXT = None
			else:
				if active_series is not None:#if active series list provided (i.e. loaded from Player settings)...
					self.ACTIVE_SERIES = active_series
					print("Active series provided to playlist!", self.ACTIVE_SERIES)
				else:
					print("Unable to set active series from config or arguments! Setting to None...")
					self.ACTIVE_SERIES = None#default to all in series list, overridden by Player settings.conf
				self.SERIES = self.get_series()
				self.MOVIES = self.get_movies()
				self.MUSIC = self.get_music()
				self.OTHER = {}
				self.LAST = None
			try:
				self.NEXT = self.get_next()
			except Exception as e:
				self.NEXT = None
	def object_to_dict(self, obj):
		return obj.__dict__
	def dict_to_object(self, d):
		return Media(**d)
	def dict_to_objects(self, d):
		objects = {}
		objects['Series'] = {}
		objects['Movies'] = {}
		objects['Music'] = {}
		objects['Other'] = {}
		for sn in d['Series']:
			if sn not in list(objects['Series'].keys()):
				objects['Series'][sn] = {}
			for season in list(d['Series'][sn].keys()):
				if season not in list(objects['Series'][sn].keys()):
					objects['Series'][sn][season] = {}
				for en in list(d['Series'][sn][season].keys()):
					objects['Series'][sn][season][en] = Media(**d['Series'][sn][season][en])
		for title in d['Movies']:
			objects['Movies'][title] = Media(**d['Movies'][title])
		for filepath in d['Music']:
			objects['Music'][filepath] = Media(**d['Music'][filepath])
		for filepath in d['Other']:
			objects['Other'][filepath] = Media(**d['Other'][filepath])
		return objects
	def objects_to_dict(self, data=None):
		out = {}
		out['Series'] = {}
		out['Movies'] = {}
		out['Music'] = {}
		out['Other'] = {}
		if data is None:
			movies = self.MOVIES
			series = self.SERIES
			other = self.OTHER
			music = self.MUSIC
		else:
			movies = data['Movies']
			series = data['Series']
			music = data['Music']
			other = data['Other']
		for sn in series:
			out['Series'][sn] = {}
			for season in series[sn]:
				if season not in list(out['Series'][sn].keys()):
					out['Series'][sn][season] = {}
				for en in series[sn][season]:
					obj = series[sn][season][en]
					out['Series'][sn][season][en] = obj.__dict__
			for title in movies:
				obj = movies[title]
				out['Movies'][obj.title] = obj.__dict__
			for filepath in music:
				obj = music[filepath]
				out['Music'][obj.filepath] = obj.__dict__
			for filepath in other:
				obj = other[filepath]
				out['Other'][obj.filepath] = obj.__dict__
		return out
	def update(self, series=None, movies=None, music=None):
		if series is None:
			self.SERIES = self.get_series()
		else:
			self.SERIES = series
		if movies is None:
			self.MOVIES = self.get_movies()
		else:
			self.MOVIES = movies
		if music is None:
			self.MUSIC = self.get_music()
		else:
			self.MUSIC = music
		print("Playlist reloaded!")
	def apply_playlist(self, playlistfile='testplaylist.txt'):
		self.SERIES = {}
		self.MOVIES = {}
		self.MUSIC = {}
		self.OTHER = {}
		for obj in [Media(d) for d in list(self.load_playlist_file(playlistfile).values())]:
			names = list(self.SERIES.keys())
			if obj.media_type == 'Series':
				if obj.series_name in names:
					self.SERIES[obj.series_name][obj.season][obj.episode_number] = obj
				else:
					self.SERIES[obj.series_name] = {}
					self.SERIES[obj.series_name][obj.season] = {}
					self.SERIES[obj.series_name][obj.season][obj.episode_number] = obj
			elif obj.media_type == 'Movies':
				self.MOVIES[obj.title] = obj
			elif obj.media_type == 'Music':
				self.MUSIC[obj.artist][obj.title] = obj
			else:
				self.OTHER[obj.filepath] = obj
		print("Done!")
	def load_playlist_file(self, filepath):
		files = self.read_playlist_file(filepath)
		out = {}
		for filepath in files:
			out[filepath] = self.Guesser.get_info_from_filepath(filepath)
		return out
	def read_playlist_file(self, filepath=None):
		if filepath is None:
			filepath = self.PLAYLIST_FILE
		f = open(filepath, 'r')
		data = f.read().splitlines()
		f.close()
		return data
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
	def _list_series(self, series_name=None, season=None):
		self.SERIES = {}
		series = {}
		names = os.listdir(self.SERIES_DIR)
		if series_name is None:
			targets = names
		else:
			targets = [series_name]
		for series_name in targets:
			season = None
			en = None
			if series_name in names:
				series[series_name] = {}
				path = os.path.join(self.SERIES_DIR, series_name)
				if not os.path.isdir(path):
					print(f"Not a directory: {path}")
				else:
					dirs = os.listdir(path)
					if season is None:
						seasons = dirs
					else:
						seasons = [f"S{season}"]
					for sdir in seasons:
						s = sdir
						if 'S' in str(s):
							sint = int(s.split('S')[1])
							sstring = s
						else:
							sint = s
							sstring = f"S{sint}"
						series[series_name][sint] = {}
						path = os.path.join(self.SERIES_DIR, series_name, sdir)
						print("Scanning path:", path)
						files = os.listdir(path)
						for filepath in files:
							info = self.Guesser.get_info_from_filepath(filepath)
							series_name, season, episode_number = info['series_name'], info['season'], info['episode_number']
							if series_name not in list(series.keys()):
								series[series_name] = {}
							if season not in list(series[series_name].keys()):
								series[series_name][season] = {}
							if episode_number not in list(series[series_name][season].keys()):
								out = {}
								out['media_type'] = 'Series'
								out['series_name'] = series_name
								out['season'] = season
								out['filepath'] = os.path.join(path, filepath)
								out['episode_number'] = episode_number
								series[series_name][season][episode_number] = Media(**out)
							else:
								print("Episode already in database!", series_name, season, episode_number, filepath)
		self.SERIES = series
		return series
	def _list_movies(self, title=None, year=None):
		self.MOVIES = {}
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
					out = {}
					out['title'] = title
					out['year'] = year
					out['media_type'] = 'Movies'
					out['filepath'] = os.path.join(path, filepath)
					self.MOVIES[title] = Media(**out)
		return self.MOVIES
	def _list_music(self, title=None, artist=None, album=None):
		self.MUSIC = {}
		exts = ['.mp3', '.wav']
		files = [os.path.join(self.MUSIC_DIR, f) for f in os.listdir(self.MUSIC_DIR)]
		for filepath in files:
			ext = os.path.splitext(filepath)[1]
			if ext in exts:
				fname = os.path.basename(filepath)
				if '[' in fname and ']' in fname:
					title = fname.split(' [')[0]
					try:
						ytid = fname.split(' [')[1].split(']')[0]
					except Exception as e:
						print(f"{e}: {filepath}")
						ytid = None
					d = {}
					d['title'] = title
					d['youtube_id'] = ytid
					d['filepath'] = filepath
					d['media_type'] = 'Music'
					self.MUSIC[title] = Media(**d)
				else:
					title, artist, album, ytid, ext = fname.split('.')
					d = {}
					d['title'] = title
					d['artist'] = artist
					d['album'] = album
					d['youtube_id'] = ytid
					d['media_type'] = 'Music'
					d['filepath'] = filepath
					self.MUSIC[title] = Media(**d)
		return self.MUSIC
	def _get_list_range(self, start_num, end_num):
		l = []
		for i in range(start_num, end_num+1):
			l.append(str(i))
		return l
	def get_movies(self, title=None, year=None):
		objects = {}
		self.MOVIES = self._list_movies()
		return self.MOVIES
	def get_music(self, title=None, artist=None, album=None):
		objects = {}
		self.MUSIC = self._list_music()
		return self.MUSIC
	def get_series(self, **args):
		"""
		main getter function for populating playlist object with series.
		Uses self.ACTIVE_SERIES (defaults as all in media list) to filter active/inactive
		playlist items and only returns those in the ACTIVE_SERIES list.
		TODO - Add this to movie series/sagas/trilogies/etc.
		"""
		return self._list_series()
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
			print(f"episodes in {series_name}:{season} - {len(ens)}")
			print(f"Current index of episode {episode_number}(+1): {eidx}")
			print("Reached end of season!")
			season = self.get_next_season(series_name=series_name, season=season)
			ens = self._get_episodes(series_name=series_name, season=season)
			en = ens[0]
		else:
			en = ens[eidx]
		print("Set episode:", series_name, season, en)
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
				print(f"get_next_series - Error: couldn't retreive last entry with series {series_name} - {e}")
		if type(obj) == dict:
			obj = Media(**obj)
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

class Scanner():
	def __init__(self, path="/media/monkey/usbhd/Media"):
		self.MEDIA_DIR = path
		self.DATA_DIR = os.path.join(os.path.expanduser("~"), '.nplayerv2')
		self.SAVEFILE = os.path.join(self.DATA_DIR, 'media.dat')
		self.SERIES_DIR = os.path.join(self.MEDIA_DIR, 'Series')
		self.MOVIES_DIR = os.path.join(self.MEDIA_DIR, 'Movies')
		self.MUSIC_DIR = os.path.join(self.MEDIA_DIR, 'Music')
		self.OTHER_DIR = os.path.join(self.MEDIA_DIR, 'Other')
		self.SERIES = {}
		self.MOVIES = {}
		self.MUSIC = {}
		self.OTHER = {}
		self.Guesser = MediaGuesser()
	def _find(self, path, ext):
		try:
			ret = subprocess.check_output(f"find \"{path}\" -name \"*{ext}\"", shell=True).decode().strip().splitlines()
			if ret == '':
				ret = []
			return ret
		except Exception as e:
			print(F"Error - {e}")
			return []
	def find(self, path='/media/monkey/usbhd/Media/Series'):
		out = []
		exts = ['.mov', '.avi', '.mp4', '.wmv', '.mkv', '.flv', '.wav', '.mp3', '.ac3']
		for ext in exts:
			files = self._find(path=path, ext=ext)
			for filepath in files:
				out.append(filepath)
		return out
	def _list_series_names(self):
		names = os.listdir(self.SERIES_DIR)
		return names
	def add_series(self, filepath):
		if type(filepath) == str:
			info = self.Guesser.get_info_from_filepath(filepath)
		else:
			info = filepath
			filepath = info['filepath']
		obj = Media(**info)
		if obj.series_name not in list(self.SERIES.keys()):
			self.SERIES[obj.series_name] = {}
		if obj.season not in list(self.SERIES[obj.series_name].keys()):
			self.SERIES[obj.series_name][obj.season] = {}
		if obj.episode_number not in list(self.SERIES[obj.series_name][obj.season].keys()):
			self.SERIES[obj.series_name][obj.season][obj.episode_number] = obj
			print(f"Episode added: {obj.filepath}")
		else:
			print("Already added!", obj.__dict__)
		return self.SERIES
	def _list_series(self):
		self.SERIES = {}
		names = self._list_series_names()
		for series_name in names:
			path = os.path.join(self.SERIES_DIR, series_name)
			files = self.find(path=path)
			for filepath in files:
				self.add_series(filepath)
		return self.SERIES
	def _list_movies(self, path=None):
		self.MOVIES = {}
		if path is None:
			path = self.MOVIES_DIR
		self.MOVIES = {}
		files = self.find(path=path)
		for filepath in files:
			obj = Media(**self.Guesser.get_info_from_filepath(filepath))
			self.MOVIES[obj.title] = obj
		return self.MOVIES
	def _list_music(self, path=None):
		self.MUSIC = {}
		if path is None:
			path = self.MOVIES_DIR
		files = self.find(path=path)
		for filepath in files:
			obj = Media(**self.Guesser.get_info_from_filepath(filepath))
			self.MUSIC[obj.title] = obj
		return self.MUSIC
	def _list_all_media(self, path=None):
		out = {}
		out['Series'] = {}
		out['Movies'] = {}
		out['Music'] = {}
		out['Other'] = {}
		if path is None:
			path = self.MEDIA_DIR
		files = self.find(path=path)
		for filepath in files:
			obj = Media(**self.Guesser.get_info_from_filepath(filepath))
			if obj.media_type == 'Music':
				out['Music'][obj.filepath] = obj
			elif obj.media_type == 'Movies':
				out['Movies'][obj.title] = obj
			elif obj.media_type == 'Other':
				out['Other'][obj.filepath] = obj
			elif obj.media_type == 'Series':
				out['Series'] = self.add_series(obj.filepath)
		return out
	def object_to_dict(self, obj):
		return obj.__dict__
	def dict_to_object(self, d):
		return Media(**d)
	def dict_to_objects(self, d):
		objects = {}
		objects['Series'] = {}
		objects['Movies'] = {}
		objects['Music'] = {}
		objects['Other'] = {}
		for sn in d['Series']:
			if sn not in list(objects['Series'].keys()):
				objects['Series'][sn] = {}
			for season in list(d['Series'][sn].keys()):
				if season not in list(objects['Series'][sn].keys()):
					objects['Series'][sn][season] = {}
				for en in list(d['Series'][sn][season].keys()):
					objects['Series'][sn][season][en] = Media(**d['Series'][sn][season][en])
		for title in d['Movies']:
			objects['Movies'][title] = Media(**d['Movies'][title])
		for filepath in d['Music']:
			objects['Music'][filepath] = Media(**d['Music'][filepath])
		for filepath in d['Other']:
			objects['Other'][filepath] = Media(**d['Other'][filepath])
		return objects
	def objects_to_dict(self, data=None):
		out = {}
		out['Series'] = {}
		out['Movies'] = {}
		out['Music'] = {}
		out['Other'] = {}
		if data is None:
			movies = self.Movies
			series = self.Series
			other = self.Other
			music = self.Music
		else:
			movies = data['Movies']
			series = data['Series']
			music = data['Music']
			other = data['Other']
		for sn in series:
			out['Series'][sn] = {}
			for season in series[sn]:
				if season not in list(out['Series'][sn].keys()):
					out['Series'][sn][season] = {}
				for en in series[sn][season]:
					obj = series[sn][season][en]
					out['Series'][sn][season][en] = obj.__dict__
			for title in movies:
				obj = movies[title]
				out['Movies'][obj.title] = obj.__dict__
			for filepath in music:
				obj = music[filepath]
				out['Music'][obj.filepath] = obj.__dict__
			for filepath in other:
				obj = other[filepath]
				out['Other'][obj.filepath] = obj.__dict__
		return out
	def save_media(self, data=None):
		t = list(data['Movies'].values())[0]
		if isinstance(t, Media):
			data = self.ojects_to_dict(data)
		with open(self.SAVEFILE, 'wb') as f:
			pickle.dump(data, f)
			f.close()
		print(f"Media saved to {self.SAVEFILE}!")
	def load_media(self):
		try:
			with open(self.SAVEFILE, 'rb') as f:
				data = pickle.load(f)
				f.close()
		except Exception as e:
			print(f"Error loading media: {e}")
			return None
		self.SERIES = data['Series']
		self.MOVIES = data['Movies']
		self.MUSIC = data['Music']
		self.OTHER = data['Other']
		return self.dict_to_objects(data)

class Player():
	def __init__(self, width=None, height=None, cache_size=6000, scale_video=1.0, run_mainloop=False, new_player_window=True, vlc_verbosity=0, fullscreen=False, playlistfile=None, seek_percentage=0.1):
		"""
		Main player class
		args:
			keyboard_events - if True, will eventually capture and react to keyboard events. STILL IN PROGRESS, NOT YET IMPLEMENTED.
			run_mainloop - if True, runs tkinter.Tk().mainloop after all else is done. Currently unused (default=False)
			new_player_window - whether or not to show player window. set to False to init player with no tkinter viewer window
		"""
		self.NOW_PLAYING = None
		self.MUTE = False
		self.SHUFFLE_TYPES = ['Series', 'Random', 'Movies', 'All', 'Music']
		self.ALL_PLAYBACK_TYPES = ['Series', 'Movies', 'Music']
		self.ACTIVE_PLAYBACK_TYPES = ['Series']
		self.SEEK = seek_percentage
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
			self.VIEWER.config(menu=self.get_menu())
			self.VIEWER.title("Media Player")
			self.WIDTH, self.HEIGHT = get_screen_res()
			self.VIEWER.geometry(f"{self.WIDTH}x{self.HEIGHT}")
			self.VIEWER.bind("<Configure>", self.set_scale)
			iconpath = os.path.join(self.DATA_DIR, "Media_Player.png")
			self.VIEWERICON = tk.PhotoImage(file=iconpath)
			self.VIEWER.iconphoto(True, self.VIEWERICON)
			frame = tk.Frame(self.VIEWER, width=self.WIDTH, height=self.HEIGHT, bg='black')
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
		try:
			config = self.get_config(apply_changes=True)
			self.ACTIVE_SERIES = config['ACTIVE_SERIES']
		except:
			config = self._init_config()
			#if active series names attribute is not in config, re-init with entire series list.
			print("ACTIVE_SERIES key not in settings file! Defaulting to 'all'...")
			config['ACTIVE_SERIES'] = Playlist()._list_series().keys()
			self.save_current_config(config)
		self.PLAYLISTFILE = playlistfile
		if playlistfile is not None:
			self.PLAYLIST = self.load_playlist(playlistfile)
		else:
			self.PLAYLIST = Playlist(init_empty=True)
			self.load_media()
		if self.PLAYLISTFILE is None:
			self.PLAYLISTFILE = 'testplaylist.txt'
		if self.PLAY_NEXT is None:
			if self.PLAYLIST.NEXT is None:
				pass
			else:
				self.PLAY_NEXT = self.PLAYLIST.NEXT
		if self.ACTIVE_SERIES is None:	
			self.ACTIVE_SERIES = self.PLAYLIST.ACTIVE_SERIES
		self.Poller = DataPoller(player=self.PLAYER)
		if run_mainloop:
			self.start_loop()
			self.VIEWER.mainloop()
	def scan(self, path=None):
		if path is None:
			path = self.MEDIA_DIR
		self.Scanner = Scanner(path=path)
	def filter_series(self, active_series_names=None):
		out = {}
		if active_series_names is None:
			active_series_names = self.ACTIVE_SERIES
		for sn in active_series_names:
			 if sn not in list(out.keys()):
				 print(self.Scanner.SERIES.keys())
				 out[sn] = self.Scanner.SERIES[sn]
		return out
	def load_media(self):
		self.Scanner = Scanner(path=self.PLAYLIST.MEDIA_DIR)
		media = self.Scanner.load_media()
		if self.ACTIVE_SERIES is None or self.ACTIVE_SERIES == []:
			self.ACTIVE_SERIES = list(media['Series'].keys())
		self.SERIES = self.PLAYLIST.get_series()
		self.MOVIES = self.PLAYLIST.get_movies()
		self.MUSIC = self.PLAYLIST.get_movies()
		self.OTHER = [{d['filepath']: Media(**d)} for d in list(self.Scanner.OTHER.values())]
		filtered = self.filter_series(self.ACTIVE_SERIES)
		if filtered == {}:
			print("Failed to filter series!")
		else:
			print("Series filtered!")
			self.SERIES = filtered
		self.PLAYLIST.SERIES = self.SERIES
		self.PLAYLIST.MOVIES = self.MOVIES
		self.PLAYLIST.MUSIC = self.MUSIC
		self.PLAYLIST.OTHER = self.OTHER
	def get_player_data(self):
		return self.Poller.poll()
	def get_player_attr(self, key):
		return self.Poller.get(key=key)
	def get_menu(self):
		menubar = tk.Menu(self.VIEWER)
		controlls_menu = tk.Menu(menubar, tearoff=1) # tearoff=1 means menu can be dragged to a floating object.
		edit_menu = tk.Menu(menubar, tearoff=0)
		playlist_menu = tk.Menu(menubar, tearoff=0)
		menubar.add_cascade(label="Controlls", menu=controlls_menu)
		menubar.add_cascade(label="Edit", menu=edit_menu)
		menubar.add_cascade(label="Playlist", menu=playlist_menu)
		controlls_menu.add_command(label="Play/Pause", command=lambda: self.pause())
		controlls_menu.add_command(label="Skip Next", command=lambda: self.playnext())
		controlls_menu.add_command(label="Seek Forward", command=self.seek_fwd)
		controlls_menu.add_command(label="Seek Backwards", command=self.seek_rev)
		controlls_menu.add_command(label="Fullscreen", command=lambda: self.toggle_fullscreen())
		controlls_menu.add_separator() # Add a separator line
		controlls_menu.add_command(label="Toggle Mute", command=lambda: self.PLAYER.audio_toggle_mute())
		controlls_menu.add_separator() # Add a separator line
		controlls_menu.add_command(label="Volume Up", command=lambda: self.PLAYER.audio_set_volume(self.PLAYER.audio_get_volume()+10))
		controlls_menu.add_command(label="Volume Down", command=lambda: self.PLAYER.audio_set_volume(self.PLAYER.audio_get_volume()-10))
		controlls_menu.add_command(label="Exit", command=exit)
		edit_menu.add_command(label="Set Active Series", command=self.edit_active_series)
		edit_menu.add_command(label="Media Manager", command=self.run_media_manager)
		edit_menu.add_command(label="Pirate Bay Downloader", command=lambda: print("NOT IMPLEMENTED"))
		edit_menu.add_command(label="Metadata Tag Editor", command=lambda: print("NOT IMPLEMENTED"))
		playlist_menu.add_command(label="Load Playlist File...", command=self.load_playlist)
		playlist_menu.add_command(label="Export Current Playlist...", command=self.export_current_playlist)
		playlist_menu.add_separator()
		playlist_menu.add_command(label="Open File(s)...", command=self.open_files)
		playlist_menu.add_command(label="Open Directory...", command=self.open_directory)
		return menubar
	def run_media_manager(self):
		self.PLAYLIST.update()
		self.MEDIA_MANAGER = MediaManager(playlist=self.PLAYLIST)
		print("Media manager loaded!")
	def _set_attr(self, key, value, write_config_file=False):
		if value is None:
			print(f"_set_attr received a value of None for key {key}! Skipping...")
			return False
		else:
			self.__dict__[key] = value
			config = self.get_config(apply_changes=False)
			config[key] = value
			if write_config_file:
				print("_set_attr() - write_config_file=True, saving current config!")
				self.save_current_config(config=config)
			print("Attribute set!", key)
			return True
	def get_resolution_nowPlaying(self):
		try:
			width, height = self.PLAYER.video_get_size()
		except Exception as e:
			print(f"Unable to get resolution: (Nothing playing???")
			width, height = self.WIDTH, self.HEIGHT
		return width, height
	def setResolution(self, width=None, height=None, fullscreen=None):
		if fullscreen is not None:
			self._set_attr(key='FULLSCREEN', value=fullscreen)
		width, height = self.WIDTH, self.HEIGHT
		if width is None:
			width = self.get_screen_res()[0]
		if height is None:
			height = self.get_screen_res()[1]
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
		config = self.load_config()
		d = dict(config)
		d['ACTIVE_SERIES'] = series_names
		self.save_current_config(config=d)
		self._set_attr('ACTIVE_SERIES', series_names)
		print("Active series updated!", series_names)
	def load_config(self):
		with open(self.CONF_PATH, 'rb') as f:
			config = pickle.load(f)
			f.close() 
		return config
	def get_config(self, apply_changes=False):
		try:
			conf = self.load_config()
		except Exception as e:
			print(f"Unable to load config file! Re-initializing...({e})")
			conf = self._init_config()
		if apply_changes:
			self.apply_config(config=conf)
		if type(conf) == list:
			print("conf was list of tuples, converted to dict!")
			conf = dict(conf)
		return conf
	def _init_config(self):
		d = {}
		try:
			d['ALL_PLAYBACK_TYPES'] = self.ALL_PLAYBACK_TYPES
			d['ACTIVE_PLAYBACK_TYPES'] = self.ACTIVE_PLAYBACK_TYPES
			d['SHUFFLE_TYPES'] = self.SHUFFLE_TYPES
			d['DATA_DIR'] = self.DATA_DIR
			d['CONF_PATH'] = self.CONF_PATH
			d['PLAY_NEXT'] = self.PLAY_NEXT
			d['NOW_PLAYING'] = self.NOW_PLAYING
			d['MUTE'] = self.MUTE
			d['ACTIVE_SERIES'] = self.ACTIVE_SERIES
			d['VLC_VERBOSITY'] = self.VLC_VERBOSITY
			d['CACHE_SIZE'] = self.CACHE_SIZE
			d['FULLSCREEN'] = self.FULLSCREEN
			d['SEEK'] = self.SEEK
		except Exception as e:
			print(f"One or more class attributes (globals) failed to export! Loading defaults..", e)
			d['ALL_PLAYBACK_TYPES'] = ['Movies', 'Series', 'Music']
			d['ACTIVE_PLAYBACK_TYPES'] = ['Series']
			d['SHUFFLE_TYPES'] = ['Random', 'Series', None]
			d['DATA_DIR'] = os.path.join(os.path.expanduser("~"), '.nplayerv2')
			d['CONF_PATH'] = os.path.join(self.DATA_DIR, 'settings.conf')
			d['PLAY_NEXT'] = None
			d['NOW_PLAYING'] = None
			d['MUTE'] = False
			d['ACTIVE_SERIES'] = list(Playlist()._list_series().keys())#in case of new init (first run), use a new playlist to generate this.
			d['VLC_VERBOSITY'] = 0
			d['CACHE_SIZE'] = 6000
			d['FULLSCREEN'] = False
			d['SEEK'] = 0.1
		self.save_current_config(config=d)
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
		if type(obj) == dict:
			obj = Media(**obj)
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
		self.PLAYER.play()
		self.NOW_PLAYING = obj
		print(f"Now Playing: {self.NOW_PLAYING.__str__()}")
		time.sleep(1)
		self.set_scale()
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
	def write_playlist_file(self, playlistfile=None, objects=[], filepaths=[], return_playlist_object=False):
		if filepaths == []:
			filepaths = [o.filepath for o in objects]
		data = "\n".join(filepaths)	
		if playlistfile is None:
			playlistfile = filedialog.asksaveasfilename()
		try:
			f = open(playlistfile, 'w')
			f.write(data)
			f.close()
			print("Playlist file written!")
			self.PLAYLISTFILE = self.aylistfile
			if return_playlist_object:
				self.PLAYLIST = self.aylist(playlist_file=playlistfile)
				return self.PLAYLIST
			else:
				return True
		except Exception as e:
			print(f"Error writing playlist file: {e}")
			if return_playlist_object:
				return None
			else:
				return False
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
				print("Skipping previous...")
			elif self.EVENT == 'SeekFwd':
				print("Fast forwarding...")
				self.seek_fwd()
			elif self.EVENT == 'SeekRev':
				print("Rewinding...")
				self.seek_rev()
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
			elif self.EVENT == 'SAVE_CURRENT_PLAYLIST':
				self.export_current_playlist()
			elif self.EVENT == 'LOAD_PLAYLIST':
				self.load_playlist()
			elif self.EVENT == 'OPEN_FILES':
				self.open_files()
			elif self.EVENT == 'OPEN_DIRECTORY':
				self.open_directory()
			else:
				if self.EVENT is not None:
					print("unhandled event:", self.EVENT)
	def load_playlist(self, playlistfile=None, play_on_load=True):
		if playlistfile is not None:
			self.PLAYLISTFILE = self.aylistfile
		else:
			self.PLAYLISTFILE = filedialog.askopenfilename()
		self.PLAYLIST = self.aylist(playlist_file=self.PLAYLISTFILE)
		if play_on_load:
			self.playnext()
		print("Playlist loaded!")
	def open_files(self, files=None, play_on_load=True):
		if files is None:
			files = filedialog.askopenfilenames()
		self.PLAYLIST = self.write_playlist_file(playlistfile=self.PLAYLISTFILE, filepaths=files, return_playlist_object=True)
		if play_on_load:
			self.playnext()
		print("Files loaded!")
	def open_directory(self, path=None, play_on_load=True):
		if path is None:
			path = filedialog.askdirectory()
		files = [os.path.join(path, f) for f in os.listdir(path)]
		self.PLAYLIST = self.write_playlist_file(playlistfile=self.PLAYLISTFILE, filepaths=files, return_playlist_object=True)
		if play_on_load:
			self.playnext()
		print("Directory loaded!")
	def export_current_playlist(self):
		ret = self.write_playlist_file(playlistfile=self.PLAYLISTFILE, objects=self.PLAYLIST._get_all(), return_playlist_object=False)
		if ret:
			print("Playlist exported!")
		else:
			print("Playlist export failed!")
	def start_loop(self, daemon=True):
		self.THREAD = threading.Thread(target=self.loop)
		self.THREAD.daemon = daemon
		self.THREAD.start()
		print("Thread started!")
		#self.VIEWER.mainloop()
	def set_position(self, pos=None, direction='fwd', position_incremental=0.1):
		if pos is None:
			pos = self.Poller.get('get_position')
			if direction == 'fwd':
				pos += position_incremental
			elif direction == 'rev':
				pos -= position_incremental
			else:
				print(f"Unknown seek diretion: {direction}!")
		else:
			print(f"Skipping to position: {pos}...")
		if pos <= 0:
			print("Reached start! Set to 0...")
			pos = 0
		elif pos >= 99:
			print("Reached end! Aborting seek...")
			return False
		self.PLAYER.set_position(pos)
		print("Playback position set:", pos)
	def seek_fwd(self):
		return self.set_position(direction='fwd')
	def seek_rev(self):
		return self.set_position(direction='rev')
	def edit_active_series(self):
		def add_item():
			active = self.ACTIVE_SERIES
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
			self._set_attr('ACTIVE_SERIES', active, True)
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
			self.set_active_series(active)
			return active
		def update_active(active_items=None):
			if active_items is None:
				active_items = listbox_active_series.get(0, tk.END)
				if len(active_items) != len(self.ACTIVE_SERIES):
					print("Length is different! Updating player option ('ACTIVE_SERIES')...")
					#self.set_active_series(series_names=active_items)
					self._set_attr('ACTIVE_SERIES', active_items)
			root.destroy()
			return active_items
		def update_list(lb, items):
			lb.delete(0, tk.END)
			for item in items:
				lb.insert(tk.END, item)
		active = self.ACTIVE_SERIES
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
		active = self.ACTIVE_SERIES
		update_list(listbox_active_series, active)
		all_series = self.PLAYLIST.ACTIVE_SERIES
		update_list(listbox_all_series, all_series)

if __name__ == "__main__":
	import sys
	try:
		media_type = sys.argv[1]
	except:
		media_type = None
	try:
		query = sys.argv[2]
	except:
		query = None
	if '.txt' in str(query) or media_type == 'playlist':
		p = Player(run_mainloop=True, playlistfile=query)
	else:
		if media_type is None:
			p = Player(run_mainloop=True)
		else:
			p = Player(run_mainloop=True, media_type=media_type)


