import os
import uuid
import pickle
import logging
import tempfile

from django.db import models
from django.conf import settings
from django.core.files import File
from django.utils import timezone
from django.core.files.temp import NamedTemporaryFile

from pdf_app.input_file_parsers.pdf_parser import scenario_from_pdf

MAX_NAME_LENGTH = 200

FILES_DIR = "internal/pickled_scenarios/%Y%m%d/"

logger = logging.getLogger(__name__)


class ScenarioModelHandler:
    def __init__(self) -> None:
        self._temporary_pdf_file = tempfile.NamedTemporaryFile()

    def _save_pdf_in_temporary_location(self, pdf_file):
        self._temporary_pdf_file.write(pdf_file.read())

        return self._temporary_pdf_file

    def upload_scenario(self, scenario_id, pdf_file):
        if ScenarioModel.objects.filter(scenario_id=scenario_id).exists():
            raise RuntimeError(f"Scenario with ID {scenario_id} already exists")

        logger.debug(
            f"Saving scenario pdf with ID {scenario_id} to {self._temporary_pdf_file.name}"
        )
        self._temporary_pdf_file.write(pdf_file.read())

        scenario = scenario_from_pdf(self._temporary_pdf_file.name)

        pickled_scenario_temp_file = NamedTemporaryFile(delete=True)
        pickle.dump(scenario, pickled_scenario_temp_file)
        django_file = File(pickled_scenario_temp_file, name="name.bin")

        upload_date = timezone.now()
        new_scenario = ScenarioModel(
            scenario_id=scenario_id,
            upload_date=upload_date,
            serialized_scenario=django_file,
        )

        new_scenario.save()


class ScenarioModel(models.Model):
    scenario_id = models.CharField(max_length=MAX_NAME_LENGTH, primary_key=True)
    upload_date = models.DateTimeField()
    serialized_scenario = models.FileField(
        upload_to=FILES_DIR, max_length=MAX_NAME_LENGTH
    )
