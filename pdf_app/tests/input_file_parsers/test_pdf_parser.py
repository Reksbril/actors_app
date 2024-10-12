from django.test import TestCase

from pdf_app.input_file_parsers.pdf_parser import _ScenarioFromPdf, scenario_from_pdf
from pdf_app.input_file_parsers.scenario import Scenario, Page, DialogueElement
from pdf_app.tests.constants import TEST_ARTIFACTS_PATH


class TestGroup(TestCase):
    def test_positions_in_group(self):
        group = _ScenarioFromPdf.Group(500, 0)

        positions_that_should_be_in_group = [480, 495, 500, 505, 520]

        for position in positions_that_should_be_in_group:
            self.assertTrue(group.is_position_in_group(position))

    def test_positions_not_in_group(self):
        group = _ScenarioFromPdf.Group(500, 0)

        positions_that_should_not_be_in_group = [-10, 0, 479.9, 520.1, 10000]

        for position in positions_that_should_not_be_in_group:
            self.assertFalse(group.is_position_in_group(position))


class TestHamlet(TestCase):
    def test_single_page_is_parsed_properly(self):
        result = scenario_from_pdf(str(TEST_ARTIFACTS_PATH / "hamlet-1-page.pdf"))

        expected_scenario = Scenario(
            [
                Page(
                    1,
                    [
                        DialogueElement(0, "MARCELLUS", "Bernardo!"),
                        DialogueElement(
                            1, "BERNARDO", "Welcome, Horatio. Welcome, good Marcellus."
                        ),
                        DialogueElement(
                            2, "Horatio", "What, has this thing appeared again tonight?"
                        ),
                        DialogueElement(3, "BARNARDO", "I have seen nothing."),
                        DialogueElement(
                            4,
                            "MARCELLUS",
                            "Horatio says ‘tis but our fantasy,\nAnd will not let belief take hold of him\nTouching this dreaded sight twice seen of us.\nTherefore I have entreated him along\nWith us to watch the minutes of this night,\nThat, if again this apparition come,\nHe may approve our eyes and speak to it.",
                        ),
                        DialogueElement(5, "HORATIO", "Tush, tush, ‘twill not appear."),
                        DialogueElement(
                            6, "MARCELLUS", "Peace. Look where it comes again."
                        ),
                        DialogueElement(
                            7,
                            "BARNARDO",
                            "In the same figure like the king that’s dead.",
                        ),
                        DialogueElement(
                            8, "MARCELLUS", "Thou art a scholar; speak to it, Horatio."
                        ),
                        DialogueElement(
                            9,
                            "BARNARDO",
                            "Looks a not like the king? Mark it, Horatio.",
                        ),
                        DialogueElement(
                            10,
                            "HORATIO",
                            "Most like. It harrows me with fear and wonder.",
                        ),
                        DialogueElement(11, "MARCELLUS", "Speak to it, Horatio."),
                        DialogueElement(
                            12,
                            "HORATIO",
                            "What art thou that usurp’st this time of night\nTogether with that fair and warlike form\nIn which the majesty of buried Denmark",
                        ),
                    ],
                )
            ]
        )

        self.assertEqual(result, expected_scenario)

    def test_dialogue_on_page_break_is_parsed_properly(self):
        result = scenario_from_pdf(str(TEST_ARTIFACTS_PATH / "hamlet-2-pages.pdf"))

        expected_first_dialogue_element_on_page_1 = DialogueElement(
            0, "MARCELLUS", "Bernardo!"
        )
        expected_last_dialogue_element_on_page_1 = DialogueElement(
            12,
            "HORATIO",
            "What art thou that usurp’st this time of night\nTogether with that fair and warlike form\nIn which the majesty of buried Denmark\nDid sometimes march? By heaven I charge thee, speak.",
        )
        expected_first_dialogue_element_on_page_2 = DialogueElement(
            13, "MARCELLUS", "It is offended."
        )
        expected_last_dialogue_element_on_page_2 = DialogueElement(
            21,
            "CLAUDIUS",
            "Though yet of Hamlet our dear brother’s death\nThe memory be green, and that it us befitted\nTo bear our hearts in grief, and our whole kingdom\nTo be contracted in one brow of woe,\nYet so far hath discretion fought with nature\nThat we with wisest sorrow think on him\nTogether with remembrance of ourselves.\nTherefore our sometime sister, now our queen,",
        )

        self.assertEqual(len(result.pages), 2)
        self.assertEqual(result.pages[0].page_number, 1)
        self.assertEqual(result.pages[1].page_number, 2)

        self.assertEqual(
            expected_first_dialogue_element_on_page_1,
            result.pages[0].dialogue_elements[0],
        )
        self.assertEqual(
            expected_last_dialogue_element_on_page_1,
            result.pages[0].dialogue_elements[-1],
        )
        self.assertEqual(
            expected_first_dialogue_element_on_page_2,
            result.pages[1].dialogue_elements[0],
        )
        self.assertEqual(
            expected_last_dialogue_element_on_page_2,
            result.pages[1].dialogue_elements[-1],
        )

    def test_whole_scenario_is_parsed_properly(self):
        result = scenario_from_pdf(str(TEST_ARTIFACTS_PATH / "hamlet.pdf"))

        self.assertEqual(len(result.pages), 20)
        for idx, page in enumerate(result.pages):
            assert idx + 1 == page.page_number

        # TODO extend this test
