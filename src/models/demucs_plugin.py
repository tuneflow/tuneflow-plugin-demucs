from tuneflow_py import TuneflowPlugin, Song, ReadAPIs, ParamDescriptor, TrackType
from typing import Any

class MusicSourceSeparatePlugin(TuneflowPlugin):

    @staticmethod
    def provider_id():
        return "qjq"

    @staticmethod
    def plugin_id():
        return "separate-track-plugin"

    @staticmethod
    def provider_display_name():
        return {
            "zh": "QJQ",
            "en": "QJQ"
        }

    @staticmethod
    def plugin_display_name():
        return {
            "zh": "音轨分离",
            "en": "Music Source Separation",
        }

    @staticmethod
    def plugin_description():
        return {
            "zh": "从音乐中分离鼓、贝斯和人声",
            "en": "Separating drums, bass, and vocals from the music.",
        }

    @staticmethod
    def allow_reset():
        return False

    def params(self) -> dict[str, ParamDescriptor]:
        return {}

    def run(self, song: Song, params: dict[str, Any], read_apis: ReadAPIs):
        print("=============================")
        print(
            "Separating drums, bass, and vocals from the music.")
        song.create_track(TrackType.MIDI_TRACK, index=0)