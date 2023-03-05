from tuneflow_py import TuneflowPlugin, Song, ParamDescriptor, WidgetType, TrackType, InjectSource
from tuneflow_py.models.protos import song_pb2
from typing import Any
from source_separator import SourceSeparator
from pathlib import Path


class MusicSourceSeparatePlugin(TuneflowPlugin):

    @staticmethod
    def provider_id():
        return "qjq"

    @staticmethod
    def plugin_id():
        return "separate-track-plugin"

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
        }

    @staticmethod
    def run(song: Song, params: dict[str, Any]):
        print("=============================")
        print(
            "Separating drums, bass, and vocals from the music.")
        audio_clip_data: song_pb2.AudioClipData = MusicSourceSeparatePlugin._get_selected_audio_clip_data(
            song, params)
        MusicSourceSeparatePlugin._separate_music_sources(
            song, audio_clip_data.audio_file_path, audio_clip_data.duration)

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
    def _separate_music_sources(song: Song, audio_file_path, duration):
        file_path = Path(audio_file_path)
        if not file_path.exists():
            raise Exception("Cannot find audio under path: ", audio_file_path)

        # TODO: Switch to use tempfile.TemporaryDirectory().
        output_dir_path = file_path.parent.joinpath("tuneflow_output")

        source_separator = SourceSeparator(
            audio_file_path, output_dir_path)
        output_audio_file_paths = source_separator.run()

        # Rendering generated tracks.
        for output_audio_file_path in output_audio_file_paths:
            MusicSourceSeparatePlugin._create_track(
                song, str(output_audio_file_path.absolute()), duration)

    @staticmethod
    def _create_track(song: Song, audio_file_path, duration):
        new_track = song.create_track(TrackType.AUDIO_TRACK)
        new_track.create_audio_clip(clip_start_tick=0, audio_clip_data={
            "audio_file_path": audio_file_path,
            "start_tick": 0,
            "duration": duration
        })
