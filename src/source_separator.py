from demucs.pretrained import get_model
from demucs.separate import load_track
from demucs.apply import apply_model
from pathlib import Path
from io import BytesIO
import tempfile
import torch as th
import torchaudio as ta
import os

model_name = "htdemucs"
model_dir_path = Path(__file__).parent.joinpath("models")
model = get_model(model_name, model_dir_path)
finetuned_model_name = "htdemucs_ft"
finetuned_model = get_model(finetuned_model_name, model_dir_path)
device = "cuda" if th.cuda.is_available() else "cpu"
model = model.to(th.device(device))
model.eval()
finetuned_model = finetuned_model.to(th.device(device))
finetuned_model.eval()


class SourceSeparator:
    def __init__(self, audio_bytes, output_dir_path=None):
        global device, model_name
        self.audio_bytes = audio_bytes
        self.output_dir_path = output_dir_path
        self.model_name = model_name
        self.exportExt = "mp3"
        self.device = device
        self.num_workers = 4
        self.model_inference_progress = False

    def run(self, mode: str):
        global model, finetuned_model
        using_finetuned_model = mode == '2_stems_vocal_finetune' or mode == '4_stems_finetune'
        print("Using finetuned model: {}".format(using_finetuned_model))
        chosen_model = finetuned_model if using_finetuned_model else model

        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='wav')
        tmp_file.write(self.audio_bytes)
        tmp_file.close()

        wav = load_track(tmp_file.name,
                         chosen_model.audio_channels, chosen_model.samplerate)

        os.unlink(tmp_file.name)

        ref = wav.mean(0)
        wav = (wav - ref.mean()) / ref.std()
        generated_tracks = apply_model(chosen_model, wav[None], device=self.device, split=True,
                                       progress=self.model_inference_progress, num_workers=self.num_workers)[0] #type:ignore
        generated_tracks = generated_tracks * ref.std() + ref.mean()

        # Combine tracks if needed, based on the selected mode
        stem = 'vocals' if mode == '2_stems_vocal' or mode == '2_stems_vocal_finetune' else None
        if stem is not None:
            sources = list(generated_tracks)
            stem_source = sources.pop(chosen_model.sources.index(stem))
            other_stem_source = th.zeros_like(sources[0])
            for i in sources:
                other_stem_source += i
            generated_tracks = [other_stem_source, stem_source]

        # Write tracks as audio.
        output_file_bytes_list = []
        for generated_track, track_type in zip(generated_tracks, chosen_model.sources):
            generated_file_bytes = SourceSeparator._wav2bytes(
                generated_track, chosen_model.samplerate, format=self.exportExt)
            output_file_bytes_list.append(generated_file_bytes)
        return output_file_bytes_list

    @staticmethod
    def _wav2bytes(waveform: th.Tensor, samplerate, format):
        file_bytes = BytesIO()
        ta.save(file_bytes, waveform,
                samplerate, format=format)
        return file_bytes
