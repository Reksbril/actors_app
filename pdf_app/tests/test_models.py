from django.test import TestCase

from pdf_app.models import ScenarioModel, ScenarioModelHandler


class ModelsTest(TestCase):
    def test_upload_new_scenario(self):
        scenario_handler = ScenarioModelHandler()

        with open(
            "/home/mateusz/projects/actors_app/pdf_app/tests/test_artifacts/hamlet.pdf",
            "rb",
        ) as f:
            scenario_handler.upload_scenario("1", f)

    def test_upload_two_scenarios(self):
        scenario_handler = ScenarioModelHandler()

        with open(
            "/home/mateusz/projects/actors_app/pdf_app/tests/test_artifacts/hamlet.pdf",
            "rb",
        ) as f:
            scenario_handler.upload_scenario("1", f)
            scenario_handler.upload_scenario("2", f)

    def test_handler_throws_error_if_two_scenarios_with_the_same_id_are_added(self):
        scenario_handler = ScenarioModelHandler()

        with open(
            "/home/mateusz/projects/actors_app/pdf_app/tests/test_artifacts/hamlet.pdf",
            "rb",
        ) as f:
            scenario_handler.upload_scenario("1", f)

            with self.assertRaisesRegex(RuntimeError, "already exists"):
                scenario_handler.upload_scenario("1", f)
