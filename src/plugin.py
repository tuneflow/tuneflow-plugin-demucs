from src.source_separator import SourceSeparator

from tuneflow_py import TuneflowPlugin, Song, ParamDescriptor, WidgetType, TrackType, InjectSource, Clip
from typing import Any, Dict
import traceback
from pydub import AudioSegment
from io import BytesIO


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
                    }
                }
            },
            "mode": {
                "displayName": {
                    "zh": '模式',
                    "en": 'Mode',
                },
                "defaultValue": '2_stems_vocal',
                "description": {
                    "zh": "精修版可能达到更好地效果，但是需要长得多的时间。",
                    "en": "Fine-tuned versions may have better quality but take much longer time."
                },
                "widget": {
                    "type": WidgetType.Select.value,
                    "config": {
                        "options": [
                            {
                                "label": {
                                    "zh": "人声 + 伴奏",
                                    "en": "Vocal + Accompaniment"
                                },
                                "value": "2_stems_vocal"
                            },
                            {
                                "label": {
                                    "zh": "人声 + 旋律 + 鼓 + 贝斯",
                                    "en": "Vocal + Melody + Drums + Bass"
                                },
                                "value": "4_stems"
                            },
                            {
                                "label": {
                                    "zh": "人声 + 伴奏 (精修版)",
                                    "en": "Vocal + Accompaniment (fine-tuned)"
                                },
                                "value": "2_stems_vocal_finetune"
                            },
                            {
                                "label": {
                                    "zh": "人声 + 旋律 + 鼓 + 贝斯 (精修版)",
                                    "en": "Vocal + Melody + Drums + Bass (fine-tuned)"
                                },
                                "value": "4_stems_finetune"
                            }
                        ],
                    },
                },
            }
        }

    @staticmethod
    def run(song: Song, params: Dict[str, Any]):
        print("=============================")
        print(
            "Separating drums, bass, and vocals from the music.")
        mode = params["mode"]
        selected_clip_infos = params["selectedClipInfos"]
        selected_clip_info = selected_clip_infos[0]
        track = song.get_track_by_id(selected_clip_info["trackId"])
        if track is None:
            raise Exception("Cannot find track")
        audio_clip = track.get_clip_by_id(selected_clip_info["clipId"])
        if audio_clip is None:
            raise Exception("Cannot find clip")
        clip_audio_data_list = params["clipAudioData"]
        audio_bytes = MusicSourceSeparatePlugin._trim_audio(
            clip_audio_data_list[0]["audioData"]["data"], song, audio_clip)
        track_index = song.get_track_index(track_id=track.get_id())
        MusicSourceSeparatePlugin._separate_music_sources(
            song=song, audio_bytes=audio_bytes, mode=mode, track_index=track_index, audio_clip=audio_clip)

    @staticmethod
    def _separate_music_sources(song: Song, audio_bytes, mode: str, track_index: int, audio_clip: Clip):
        source_separator = SourceSeparator(audio_bytes)
        output_file_bytes_list = source_separator.run(mode)
        print("Completed separating music source.")
        print("Rendering generated tracks...")
        for file_bytes in output_file_bytes_list:
            try:
                file_bytes.seek(0)
                new_track = song.create_track(
                    type=TrackType.AUDIO_TRACK, index=track_index+1)  # type:ignore
                new_track.create_audio_clip(
                    clip_start_tick=audio_clip.get_clip_start_tick(),
                    clip_end_tick=audio_clip.get_clip_end_tick(),
                    audio_clip_data={"audio_data": {"format": "mp3", "data": file_bytes.read()},
                                     "duration": audio_clip.get_duration(),
                                     "start_tick": audio_clip.get_clip_start_tick()})
            except:
                print(traceback.format_exc())
        print("All generated tracks have been rendered.")

    @staticmethod
    def _trim_audio(audio_bytes: bytes, song: Song, clip: Clip):
        clip_start_time = song.tick_to_seconds(clip.get_clip_start_tick())
        clip_end_time = song.tick_to_seconds(clip.get_clip_end_tick())
        audio_start_time = song.tick_to_seconds(clip.get_audio_start_tick()) #type:ignore
        in_bytes_io = BytesIO(audio_bytes)
        dub = AudioSegment.from_file(in_bytes_io)
        trimmed_dub = dub[(clip_start_time - audio_start_time)
                          * 1000:(clip_end_time - audio_start_time)*1000]
        output = BytesIO()
        trimmed_dub.export(output, format="wav")
        output.seek(0)
        return output.read()
