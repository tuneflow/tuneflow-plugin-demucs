from demucs.pretrained import get_model
from demucs.separate import load_track
from demucs.apply import apply_model
from pathlib import Path
from io import BytesIO
import tempfile
import torch as th
import torchaudio as ta
import os


class SourceSeparator:
    def __init__(self, audio_bytes, output_dir_path=None, model_name="htdemucs"):
        self.audio_bytes = audio_bytes
        self.output_dir_path = output_dir_path
        self.model_name = model_name
        self.ext = "wav"

    def run(self):
        model_dir_path = Path(__file__).parent.joinpath("models")
        model = get_model(self.model_name, model_dir_path)
        model.cpu()
        model.eval()

        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp_file.write(self.audio_bytes)
        tmp_file.close()

        wav = load_track(tmp_file.name,
                         model.audio_channels, model.samplerate)

        os.unlink(tmp_file.name)

        ref = wav.mean(0)
        wav = (wav - ref.mean()) / ref.std()
        generated_tracks = apply_model(model, wav[None], device="cpu", shifts=1,
                                       split=True, overlap=0.25, progress=True,
                                       num_workers=os.cpu_count())[0]
        generated_tracks = generated_tracks * ref.std() + ref.mean()

        output_file_bytes_list = []
        for generated_track, track_type in zip(generated_tracks, model.sources):
            generated_file_bytes = SourceSeparator._wav2bytes(
                generated_track, model.samplerate, format=self.ext)
            output_file_bytes_list.append(generated_file_bytes)

        print("Completed separating music source.")
        return output_file_bytes_list

    @staticmethod
    def _wav2bytes(waveform: th.Tensor, samplerate, format):
        file_bytes = BytesIO()
        ta.save(file_bytes, waveform,
                samplerate, format=format)
        return file_bytes
