from django.http import HttpResponse, Http404, HttpResponseServerError
from django.shortcuts import render, get_object_or_404

import pickle
import os
from subprocess import run, PIPE
from uuid import uuid4
from pathlib import Path

from django.conf import settings
from .models import ScenarioModelHandler, ScenarioModel
from .forms import PdfFileForm
from .input_file_parsers.scenario import Scenario


def delete_scenario_by_id(scenario_id):
    ScenarioModel.objects.filter(scenario_id=scenario_id).delete()


def get_characters_list(scenario: Scenario):
    characters_set = set()
    for page in scenario.pages:
        for dialogue_element in page.dialogue_elements:
            characters_set.add(dialogue_element.character_name.lower())

    return list(characters_set)


def index(request, scenario_id_to_delete=None):
    if scenario_id_to_delete is not None:
        delete_scenario_by_id(scenario_id=scenario_id_to_delete)

    if request.method == "POST":
        form = PdfFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["file"]
            scenario_id = form.cleaned_data["scenario_id"]
            try:
                ScenarioModelHandler().upload_scenario(
                    scenario_id=scenario_id, pdf_file=file
                )
                form = PdfFileForm()
            except RuntimeError as e:
                form.add_error("file", str(e))
    else:
        form = PdfFileForm()

    all_scenarios_list = ScenarioModel.objects.all()

    context = {
        "all_scenarios_list": all_scenarios_list,
        "pdf_file_form": form,
    }

    return render(request, "pdf_app/index.html", context)


def file_details(request, scenario_id):
    scenario = get_object_or_404(ScenarioModel, scenario_id=scenario_id)

    scenario_obj = pickle.load(scenario.serialized_scenario)

    context = {
        "all_characters": get_characters_list(scenario=scenario_obj),
        "scenario": scenario_obj,
        "scenario_id": scenario_id,
    }

    return render(request, "pdf_app/file_details.html", context)


# class AudioGenerator:
#     def __init__(self) -> None:
#         # self.tts = TTS(
#         #    model_path="/home/mateusz/projects/actors_app/models/vocoder_models--en--ljspeech--hifigan_v2/model_file.pth",
#         #    config_path="/home/mateusz/projects/actors_app/models/vocoder_models--en--ljspeech--hifigan_v2/config.json",
#         # )
#         # self.tts = TTS("tts_models/en/ljspeech/speedy-speech")
#         self.tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")

#     def generate(self, text):
#         file_path = self.tts.tts_to_file(text, file_path="/tmp/file.wav")
#         AudioSegment.from_wav(file_path).export("/tmp/file.mp3", format="mp3")
#         return "/tmp/file.mp3"


# audio_generator = AudioGenerator()


class PiperAudioGenerator:
    PIPER_BINARIES_PATH = settings.DEPS_BINARIES_PATH / "piper"

    def _download_file(self, file_src: str, file_dst: str):
        process = ["wget", "-O", file_dst, file_src]

        p = run(process, stdout=PIPE)

        if p.returncode != 0:
            print(p.returncode)
            print(p.stdout)
            print(p.stderr)
            print(" ".join(process))

            raise RuntimeError("File download not successful")  # TODO error handling

        # TODO check md5sum

    def __init__(self) -> None:
        self.models_dir = settings.TMP_WORKDIR / "models"
        self.onnx_model_path = self.models_dir / "model.onnx"
        self.model_config_path = self.models_dir / "config.json"

        if self.models_dir.exists():
            return

        self.models_dir.mkdir()

        dnn_model_src = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/high/en_US-lessac-high.onnx?download=true"
        dnn_config_src = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/high/en_US-lessac-high.onnx.json?download=true.json"
        self._download_file(dnn_model_src, self.onnx_model_path.resolve())
        self._download_file(dnn_config_src, self.model_config_path.resolve())

    def generate(self, text):
        out_dir = settings.TMP_WORKDIR
        out_file = out_dir / (str(uuid4()) + ".wav")

        process = [
            (PiperAudioGenerator.PIPER_BINARIES_PATH / "piper").resolve(),
            "-m",
            self.onnx_model_path.resolve(),
            "-c",
            self.model_config_path.resolve(),
            "-f",
            out_file.resolve(),
        ]

        p = run(
            process,
            stdout=PIPE,
            input=text,
            encoding="utf-8",
        )

        if p.returncode != 0:
            print(p.returncode)
            print(p.stdout)
            print(p.stderr)
            print(" ".join(process))

            raise RuntimeError("TTS not successful")  # TODO error handling

        return out_file


def get_dialogue_element_audio(request, scenario_id, dialogue_element_id):
    scenario = get_object_or_404(ScenarioModel, scenario_id=scenario_id)
    scenario_obj = pickle.load(scenario.serialized_scenario)

    text_to_generate = None
    for page in scenario_obj.pages:
        for dialogue_element in page.dialogue_elements:
            if dialogue_element.id == int(dialogue_element_id):
                text_to_generate = dialogue_element.dialogue_text

    if text_to_generate is None:
        raise RuntimeError(
            f"Dialogue element with ID {dialogue_element_id} does not exist in scenario {scenario_id}"
        )  # TODO generate 404

    audio_generator = PiperAudioGenerator()

    mp3_file_path = audio_generator.generate(text_to_generate)
    f = open(mp3_file_path, "rb")
    response = HttpResponse()
    response.write(f.read())
    response["Content-Type"] = "audio/mp3"
    response["Content-Length"] = os.path.getsize(mp3_file_path)
    return response
