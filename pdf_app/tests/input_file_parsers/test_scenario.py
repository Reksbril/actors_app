from django.test import TestCase

from pdf_app.input_file_parsers.scenario import (
    Scenario,
    Page,
    DialogueElement,
    ScenarioBuilder,
)


class ScenarioTest(TestCase):
    def test_scenario_builder_builds_single_page(self):
        builder = ScenarioBuilder()

        builder.next_character("Character1", page_number=1)
        builder.next_dialogue_line("Line1")

        builder.next_character("Character2", page_number=1)
        builder.next_dialogue_line("Line2")
        builder.next_dialogue_line("Line3")

        result = builder.build()

        expected_scenario = Scenario(
            [
                Page(
                    page_number=1,
                    dialogue_elements=[
                        DialogueElement(0, "Character1", "Line1"),
                        DialogueElement(1, "Character2", "Line2\nLine3"),
                    ],
                )
            ]
        )

        assert result == expected_scenario

    def test_scenario_builder_builds_multiple_pages(self):
        builder = ScenarioBuilder()

        builder.next_character("Character1", page_number=1)
        builder.next_dialogue_line("Line1")

        builder.next_character("Character2", page_number=2)
        builder.next_dialogue_line("Line2")
        builder.next_dialogue_line("Line3")

        builder.next_character("Character3", page_number=3)
        builder.next_dialogue_line("Line4")
        builder.next_dialogue_line("Line5")

        result = builder.build()

        expected_scenario = Scenario(
            [
                Page(
                    page_number=1,
                    dialogue_elements=[DialogueElement(0, "Character1", "Line1")],
                ),
                Page(
                    page_number=2,
                    dialogue_elements=[
                        DialogueElement(1, "Character2", "Line2\nLine3")
                    ],
                ),
                Page(
                    page_number=3,
                    dialogue_elements=[
                        DialogueElement(2, "Character3", "Line4\nLine5")
                    ],
                ),
            ]
        )

        assert result == expected_scenario

    def test_scenario_allows_more_than_single_page_jump(self):
        builder = ScenarioBuilder()

        builder.next_character("Character1", page_number=1)
        builder.next_dialogue_line("Line1")

        builder.next_character("Character2", page_number=5)
        builder.next_dialogue_line("Line2")

        result = builder.build()

        expected_scenario = Scenario(
            [
                Page(
                    page_number=1,
                    dialogue_elements=[DialogueElement(0, "Character1", "Line1")],
                ),
                Page(
                    page_number=5,
                    dialogue_elements=[DialogueElement(1, "Character2", "Line2")],
                ),
            ]
        )
        self.assertEqual(result, expected_scenario)

    def test_build_fails_for_negative_page_number(self):
        builder = ScenarioBuilder()

        with self.assertRaisesRegex(RuntimeError, "Page number .* -1"):
            builder.next_character("Character1", page_number=-1)

    def test_build_fails_when_next_page_number_is_smaller_than_previous(self):
        builder = ScenarioBuilder()

        builder.next_character("Character1", page_number=5)
        builder.next_dialogue_line("Line1")

        with self.assertRaisesRegex(RuntimeError, "Page number .* 5 .* 1"):
            builder.next_character("Character2", page_number=1)

    def test_build_fails_when_character_didnt_have_text_added(self):
        builder = ScenarioBuilder()

        builder.next_character("Character1", page_number=1)

        with self.assertRaisesRegex(RuntimeError, ".* Character1 .* empty"):
            builder.next_character("Character2", page_number=1)

    def test_build_fails_when_text_is_added_before_character(self):
        builder = ScenarioBuilder()

        with self.assertRaisesRegex(
            RuntimeError, "Character must be added before adding dialogue line"
        ):
            builder.next_dialogue_line("Line1")

    def test_build_fails_when_empty_character_name_is_added(self):
        builder = ScenarioBuilder()

        with self.assertRaisesRegex(RuntimeError, "Character name cannot be empty"):
            builder.next_character("", page_number=1)

    def test_build_fails_when_empty_text_is_added(self):
        builder = ScenarioBuilder()

        builder.next_character("Character1", page_number=1)

        with self.assertRaisesRegex(RuntimeError, "Dialogue line cannot be empty"):
            builder.next_dialogue_line("")

    def test_next_character_fails_when_previous_build_was_finished(self):
        builder = ScenarioBuilder()

        builder.next_character("Character1", page_number=1)
        builder.next_dialogue_line("Line1")
        builder.build()

        with self.assertRaises(RuntimeError):
            builder.next_character("Character2", page_number=1)

    def test_next_dialogue_line_fails_when_previous_build_was_finished(self):
        builder = ScenarioBuilder()

        builder.next_character("Character1", page_number=1)
        builder.next_dialogue_line("Line1")
        builder.build()

        with self.assertRaises(RuntimeError):
            builder.next_dialogue_line("Line2")
