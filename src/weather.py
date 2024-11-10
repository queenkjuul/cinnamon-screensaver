#!/usr/bin/python3
import json

from gi.repository import CinnamonDesktop, GLib, Gtk, Gio, Pango

from util import utils, trackers, settings
from baseWindow import BaseWindow
from floating import Floating
import requests

MAX_WIDTH = 320
MAX_WIDTH_LOW_RES = 200

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

class WeatherWidget(Floating, BaseWindow):
    """
    WeatherWidget displays current weather on screen

    It is a child of the Stage's GtkOverlay, and its placement is
    controlled by the overlay's child positioning function.

    When not Awake, it positions itself around all monitors
    using a timer which randomizes its halign and valign properties
    as well as its current monitor.
    """
    def __init__(self, away_message=None, initial_monitor=0, low_res=False):
        super(WeatherWidget, self).__init__(initial_monitor)
        self.get_style_context().add_class("weather")
        self.set_halign(Gtk.Align.START)

        self.set_property("margin", 6)

        self.low_res = low_res

        if not settings.get_show_weather():
            return

        self.away_message = away_message

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(box)
        box.show()

        self.label = Gtk.Label()
        self.label.show()
        self.label.set_line_wrap(True)
        self.label.set_alignment(0.5, 0.5)

        box.pack_start(self.label, True, False, 6)

        self.msg_label = Gtk.Label()
        self.msg_label.show()
        self.msg_label.set_line_wrap(True)
        self.msg_label.set_alignment(0.5, 0.5)

        if self.low_res:
            self.msg_label.set_max_width_chars(50)
        else:
            self.msg_label.set_max_width_chars(80)

        box.pack_start(self.msg_label, True, True, 6)

        self.update_weather()

    def update_weather(self):
        default_message = GLib.markup_escape_text (settings.get_default_away_message(), -1)
        font_message = Pango.FontDescription.from_string(settings.get_message_font())
        font_weather = Pango.FontDescription.from_string(settings.get_weather_font())

        response = requests.get(WEATHER_URL,
                                { "q": settings.get_weather_location(),
                                  "units": settings.get_weather_units(),
                                  "appid": settings.get_weather_api_key()})
        data = response.json()
        default_message = data["weather"][0]["main"] + " in " + data["name"]

        if self.low_res:
            msg_size = font_message.get_size() * .66
            font_message.set_size(int(msg_size))

        markup = '<b><span font_desc=\"%s\" foreground=\"#CCCCCC\">%s</span></b>\n ' %\
                     (font_message.to_string(), default_message)

        self.label.set_markup('<span font_desc=\"%s\">%s°</span>' % (font_weather.to_string(), data['main']['temp']))
        self.msg_label.set_markup(markup)

    def set_message(self, msg=""):
        self.away_message = msg
        self.update_weather()

    @staticmethod
    def on_destroy(data=None):
        # placeholder
        print("shut down weather widget: " + data)
