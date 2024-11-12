#!/usr/bin/python3
from gi.repository import GLib, Gtk, Pango, Gio, GdkPixbuf

from util import settings
from util.openweathermap import OWMWeatherProvider
from util.location import LocationData
from baseWindow import BaseWindow
from floating import Floating

ICON_SIZE = 128  # probably works OK on most screens


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

        # overall container
        big_box = Gtk.Box(Gtk.Orientation.HORIZONTAL)
        self.add(big_box)
        big_box.show()
        self.icon_size = ICON_SIZE

        # icon
        self.condition_icon = Gtk.Image()
        self.condition_icon.set_size_request(self.icon_size, self.icon_size)
        big_box.pack_start(self.condition_icon, False, False, 6)
        self.condition_icon.show()

        # temp + condition
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        big_box.pack_start(box, True, False, 6)
        box.show()

        self.temp_label = Gtk.Label()
        self.temp_label.show()
        self.temp_label.set_line_wrap(True)
        self.temp_label.set_alignment(0.5, 0.5)

        box.pack_start(self.temp_label, True, False, 6)

        self.desc_label = Gtk.Label()
        self.desc_label.show()
        self.desc_label.set_line_wrap(True)
        self.desc_label.set_alignment(0.5, 0.5)

        if self.low_res:
            self.desc_label.set_max_width_chars(50)
        else:
            self.desc_label.set_max_width_chars(80)

        box.pack_start(self.desc_label, True, True, 6)

        self.location = self.get_location()
        # TODO: get from settings once other providers are available
        self.weather_provider = OWMWeatherProvider()

        self.update_weather()

    def get_location(self):
        # TODO: IP geolocation
        loc_string = settings.get_weather_location()
        lat = float(loc_string.split(",")[0])
        lon = float(loc_string.split(",")[1])
        return LocationData(lat, lon)

    def update_weather(self):
        default_message = GLib.markup_escape_text(
            settings.get_default_away_message(), -1)
        message_font = Pango.FontDescription.from_string(
            settings.get_message_font())
        weather_font = Pango.FontDescription.from_string(
            settings.get_weather_font())

        if self.low_res:
            msg_size = message_font.get_size() * .66
            message_font.set_size(int(msg_size))

        weather_data = self.weather_provider.GetWeather(self.location)

        # commented out proper code, but we're cheating by pulling imperial directly for now
        # temp_string = weather_data.temp_f(
        # ) if settings.get_weather_units == "imperial" else weather_data.temp_c()
        temp_string = str(round(weather_data.temperature))
        default_message = weather_data.condition.main + \
            " in " + weather_data.location.city

        markup = '<b><span font_desc=\"%s\" foreground=\"#CCCCCC\">%s</span></b>\n ' %\
            (message_font.to_string(), default_message)

        self.temp_label.set_markup('<span font_desc=\"%s\">%s°</span>' %
                                   (weather_font.to_string(), temp_string))
        self.desc_label.set_markup(markup)

        self.condition_icon.set_from_icon_name(
            weather_data.condition.icons[0], Gtk.IconSize.DIALOG)
        self.condition_icon.set_pixel_size(self.icon_size)

    def set_message(self, msg=""):
        self.away_message = msg
        self.update_weather()

    @staticmethod
    def on_destroy(data=None):
        pass
