from tuneflow_py import TuneflowPlugin, Song, ReadAPIs, ParamDescriptor, WidgetType, TrackType, ClipType, Note, Track
from tuneflow_py.models.clip import Clip
from tuneflow_py.models.protos import song_pb2
from typing import Any
from subprocess import Popen, PIPE, STDOUT
import os

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
        return {
            "file": {
                "displayName": {
                    "zh": '文件',
                    "en": 'File',
                },
                "defaultValue": "/Users/frank/Documents/project/temp/test.mp3",
                "widget": {
                    "type": WidgetType.Input.value
                },
            },
            # "audio": {
            #     "displayName": {
            #         "zh": '音频',
            #         "en": 'Audio',
            #     },
            #     "defaultValue": None,
            #     "widget": {
            #         "type": WidgetType.MultiSourceAudioSelector.value,
            #         "config": {
            #             "allowedSources": ['audioTrack', 'file'],
            #         }
            #     },
            # },
            "doSeparation":{
                "displayName": {
                    "zh": '自动分离伴奏',
                    "en": 'Automatic accompaniment separation',
                },
                "defaultValue": False,
                "description": {
                    "zh": '先自动分离音频中的伴奏，再进行人声转录',
                    "en": 'Automatically separate the accompaniment from the audio first, then transcribe the vocals',
                },
                "widget": {
                    "type": WidgetType.Switch.value,
                },
            },
            "silenceThreshold":{
                "displayName": {
                    "zh": '音符结束阈值',
                    "en": 'Silence threshold',
                },
                "defaultValue": 0.5,
                "description": {
                    "zh": '该阈值越大，转录出的MIDI音符越长',
                    "en": 'The higher the threshold, the longer the MIDI note transcribed',
                },
                "widget": {
                    "type": WidgetType.Slider.value,
                    "config":{
                        "minValue": 0.1,
                        "maxValue": 0.9,
                        "step": 0.1
                    }
                },
            }
        }
    
    def init(self, song: Song, read_apis: ReadAPIs):
        pass

    def create_track(self, song: Song, audio_file_path):
        song.create_track(TrackType.AUDIO_TRACK, index=0)

        print("before create_audio_clip song.get_track_at(0).get_clip_count() = ", song.get_track_at(0).get_clip_count())

        # audio_clip_data = song_pb2.AudioClipData()
        # audio_clip_data.audio_file_path = audio_file_path
        # audio_clip_data.start_tick = 0
        # audio_clip_data.duration = 10

        clip = song.get_track_at(0).create_audio_clip(clip_start_tick = 0, audio_clip_data = {
            "audio_file_path": audio_file_path,
            "start_tick": 0,
            "start_tick": 0,
            "duration": 10
        })
        print("create_audio_clip clip = ", clip._proto)
        # print("after create_audio_clip song.get_track_at(0).get_clip_count() = ", song.get_track_at(0).get_clip_count())
        # print("song.get_track_at(0).get_clip_at(0)._proto = ", song.get_track_at(0).get_clip_at(0)._proto)

    def separate_music_sources(self, filename, song: Song):
        cmd = "python3 -m demucs -d cpu --out /Users/frank/Documents/project/temp/out/ " + filename
        print("executing cmd = ", cmd)
        # os.system(cmd)
        self.create_track(song, "/Users/frank/Documents/project/temp/out/htdemucs/test/bass.wav")
        self.create_track(song, "/Users/frank/Documents/project/temp/out/htdemucs/test/drums.wav")
        self.create_track(song, "/Users/frank/Documents/project/temp/out/htdemucs/test/other.wav")
        self.create_track(song, "/Users/frank/Documents/project/temp/out/htdemucs/test/vocals.wav")

    def run(self, song: Song, params: dict[str, Any], read_apis: ReadAPIs):
        print("=============================")
        print(
            "Separating drums, bass, and vocals from the music.")
        # song.create_track(TrackType.MIDI_TRACK, index=0)

        if("file" in params):
            filename = params["file"]
            print("filename = ", filename)
            self.separate_music_sources(filename, song)
            print("after create_audio_clip song.get_track_at(0).get_clip_count() = ", song.get_track_at(0).get_clip_count())
            print("song.get_track_at(0).get_clip_at(0)._proto = ", song.get_track_at(0).get_clip_at(0)._proto)


        if("audio" in params):
            audio = params["audio"]
            print("audio.keys() = ", audio.keys())
            print("audio[\"sourceType\"] = ", audio["sourceType"])

            if audio["sourceType"] == 'audioTrack':
                print(type(audio["audioInfo"]))
                track_id = audio["audioInfo"]
                print("track_id = ",  track_id)

            #     track = song.get_track_by_id(track_id=track_id)
            #     if track is None:
            #         raise Exception("Track not ready")
            #     if track.get_type() != TrackType.AUDIO_TRACK:
            #         raise Exception("Can only transcribe audio tracks")
                
            #     # track_index = song.get_track_index_by_id(track_id=track_id) # selected audio track
            #     # print(track_index)
            #     # new_midi_track = song.create_track(type=TrackType.MIDI_TRACK, index=track_index+1)
                
            #     for clip in track.get_clips():
            #         if clip.get_type() != ClipType.AUDIO_CLIP:
            #             raise Exception("Skip non-audio clip")
            #         print(clip.get_type())
            #         # audio_clip_data = clip.get_audio_clip_data()
            #         # if audio_clip_data is None or audio_clip_data.audio_file_path is None:
            #         #     continue
            #         # print("audio_clip_data.audio_file_path = " % audio_clip_data.audio_file_path)
                    
            #         # self._transcribe_clip(audio_clip_data.audio_file_path, params["doSeparation"], params["onsetThreshold"], params["silenceThreshold"])

            elif audio["sourceType"] == 'file':
                # print("audio = ", audio)
                print(type(audio["audioInfo"]))
