from tuneflow_py import TuneflowPlugin, Song, ParamDescriptor, WidgetType, TrackType, InjectSource
from tuneflow_py.models.protos import song_pb2
from typing import Any
from .source_separator import SourceSeparator
import traceback


class MusicSourceSeparatePlugin(TuneflowPlugin):

    @staticmethod
    def provider_id():
        return "qjq"

    @staticmethod
    def plugin_id():
        return "demucs"

    @staticmethod
    def params(song: Song) -> dict[str, ParamDescriptor]:
        return {
            "selectedClipInfos": {
                "displayName": {
                    "zh": '选中片段',
                    "en": 'Selected Clips',
                },
                "defaultValue": None,
                "widget": {
                    "type": WidgetType.NoWidget.value,
                },
                "hidden": True,
                "injectFrom": {
                    "type": InjectSource.SelectedClipInfos.value,
                    "options": {
                        "maxNumClips": 1
                    }
                }
            },
            "clipAudioData": {
                "displayName": {
                    "zh": '音频',
                    "en": 'Audio',
                },
                "defaultValue": None,
                "widget": {
                    "type": WidgetType.NoWidget.value,
                },
                "hidden": True,
                "injectFrom": {
                    "type": InjectSource.ClipAudioData.value,
                    "options": {
                        "clips": "selectedAudioClips"
                    }
                }
            },
        }

    @staticmethod
    def run(song: Song, params: dict[str, Any]):
        print("=============================")
        print(
            "Separating drums, bass, and vocals from the music.")
        audio_clip_data: song_pb2.AudioClipData = MusicSourceSeparatePlugin._get_selected_audio_clip_data(
            song, params)
        clip_audio_data_list = params["clipAudioData"]
        audio_bytes = clip_audio_data_list[0]["audioData"]["data"]

        MusicSourceSeparatePlugin._separate_music_sources(
            song, audio_bytes, audio_clip_data.duration)

    @staticmethod
    def _get_selected_audio_clip_data(song: Song, params: dict[str, Any]) -> song_pb2.AudioClipData:
        selected_clip_infos = params["selectedClipInfos"]
        selected_clip_info = selected_clip_infos[0]
        track = song.get_track_by_id(selected_clip_info["trackId"])
        if track is None:
            raise Exception("Cannot find track")
        clip = track.get_clip_by_id(selected_clip_info["clipId"])
        if clip is None:
            raise Exception("Cannot find clip")
        return clip.get_audio_clip_data()

    @staticmethod
    def _separate_music_sources(song: Song, audio_bytes, duration):
        source_separator = SourceSeparator(audio_bytes)
        output_file_bytes_list = source_separator.run()
        print("Completed separating music source.")
        print("Rendering generated tracks...")
        for file_bytes in output_file_bytes_list:
            try:
                file_bytes.seek(0)
                track = song.create_track(type=TrackType.AUDIO_TRACK)
                track.create_audio_clip(clip_start_tick=0, audio_clip_data={
                    "audio_data": {
                        "format": "wav",
                        "data": file_bytes.read()
                    },
                    "duration": duration,
                    "start_tick": 0
                })
            except:
                print(traceback.format_exc())
        print("All generated tracks have been rendered.")

    @staticmethod
    def _create_track(song: Song, audio_file_path, duration):
        new_track = song.create_track(TrackType.AUDIO_TRACK)
        new_track.create_audio_clip(clip_start_tick=0, audio_clip_data={
            "audio_file_path": audio_file_path,
            "start_tick": 0,
            "duration": duration
        })
