from demucs.pretrained import get_model
from demucs.separate import load_track
from demucs.apply import apply_model, BagOfModels
from demucs.audio import save_audio, AudioFile
import torch as th
import subprocess
import sys
from pathlib import Path


class SourceSeparator:
    def __init__(self, audio_file_path, output_dir_path, model_name="htdemucs"):
        self.audio_file_path = audio_file_path
        self.output_dir_path = output_dir_path
        self.model_name = model_name

    def run(self):
        model_dir_path = Path(__file__).parent.joinpath("models")
        model = get_model(self.model_name, model_dir_path)
        model.cpu()
        model.eval()

        print(
            f"Start separating music source for the audio path: {self.audio_file_path}")

        wav = load_track(self.audio_file_path,
                         model.audio_channels, model.samplerate)

        ref = wav.mean(0)
        wav = (wav - ref.mean()) / ref.std()
        sources = apply_model(model, wav[None], device="cpu", shifts=1,
                              split=True, overlap=0.25, progress=True,
                              num_workers=1)[0]
        sources = sources * ref.std() + ref.mean()
        ext = "wav"

        kwargs = {
            'samplerate': model.samplerate,
            'bitrate': 320,
            'clip': "rescale",
            'as_float': False,
            'bits_per_sample': 16,
        }

        out = Path(self.output_dir_path) / self.model_name
        stem = str(Path(self.audio_file_path).stem)
        filename = "{track}/{stem}.{ext}"
        output_audio_file_paths = []
        for source, name in zip(sources, model.sources):
            # /Users/frank/Documents/Track_5.wav
            output_audio_file_path = out / filename.format(track=stem.rsplit(".", 1)[0],
                                                           stem=name, ext=ext)
            print("Generating audio file: {output_audio_file_path}")
            output_audio_file_path.parent.mkdir(parents=True, exist_ok=True)
            save_audio(source, str(output_audio_file_path), **kwargs)
            output_audio_file_paths.append(output_audio_file_path)

        print("Completed separating music source.")
        return output_audio_file_paths
