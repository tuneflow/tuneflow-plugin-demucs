from .source_separator import SourceSeparator

from tuneflow_py import TuneflowPlugin, Song, ParamDescriptor, WidgetType, TrackType, InjectSource, Clip
from typing import Any, Dict
import traceback
from io import BytesIO
import soundfile

class MusicSourceSeparatePlugin(TuneflowPlugin):

    @staticmethod
    def provider_id():
        return "qjq"

    @staticmethod
    def plugin_id():
        return "demucs"

    @staticmethod
    def params(song: Song) -> Dict[str, ParamDescriptor]:
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
                        "clips": "selectedAudioClips",
                        "convert": {
                            "toFormat": "wav"
                        }
                    }
                }
            },
        }

    @staticmethod
    def run(song: Song, params: Dict[str, Any]):
        print("=============================")
        print(
            "Separating drums, bass, and vocals from the music.")
        audio_clip = MusicSourceSeparatePlugin._get_selected_clip(
            song, params)
        clip_audio_data_list = params["clipAudioData"]
        audio_bytes = clip_audio_data_list[0]["audioData"]["data"]

        MusicSourceSeparatePlugin._separate_music_sources(
            song, audio_bytes, audio_clip)

    @staticmethod
    def _get_selected_clip(song: Song, params: Dict[str, Any]):
        selected_clip_infos = params["selectedClipInfos"]
        selected_clip_info = selected_clip_infos[0]
        track = song.get_track_by_id(selected_clip_info["trackId"])
        if track is None:
            raise Exception("Cannot find track")
        clip = track.get_clip_by_id(selected_clip_info["clipId"])
        if clip is None:
            raise Exception("Cannot find clip")
        return clip

    @staticmethod
    def _separate_music_sources(song: Song, audio_bytes, audio_clip: Clip):
        source_separator = SourceSeparator(audio_bytes)
        output_file_bytes_list = source_separator.run()
        print("Completed separating music source.")
        print("Rendering generated tracks...")
        for file_bytes in output_file_bytes_list:
            try:
                file_bytes.seek(0)
                input_file = BytesIO(file_bytes.read())
                output_file = BytesIO()
                input_data, input_samplerate = soundfile.read(input_file)
                soundfile.write(output_file, input_data, 44100,format='mp3')
                output_file.seek(0)
                track = song.create_track(type=TrackType.AUDIO_TRACK)
                track.create_audio_clip(
                    clip_start_tick=audio_clip.get_clip_start_tick(),
                    clip_end_tick=audio_clip.get_clip_end_tick(),
                    audio_clip_data={"audio_data": {"format": "mp3", "data": output_file.read()},
                                     "duration": audio_clip.get_duration(),
                                     "start_tick": audio_clip.get_clip_start_tick()})
            except:
                print(traceback.format_exc())
        print("All generated tracks have been rendered.")
