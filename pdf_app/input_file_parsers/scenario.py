import logging

from dataclasses import dataclass
from typing import List
from copy import deepcopy

logger = logging.getLogger(__name__)

# TODO change errors to more applicable type


@dataclass
class DialogueElement:
    id: int
    character_name: str
    dialogue_text: str


@dataclass
class Page:
    page_number: int
    dialogue_elements: List[DialogueElement]


@dataclass
class Scenario:
    pages: List[Page]


class ScenarioBuilder:
    def __init__(self):
        self.is_finished: bool = False
        self.scenario: Scenario = Scenario([])
        self.current_page: Page = Page(-1, [])
        self.current_dialogue_element: DialogueElement = None
        self.dialogue_elements_count = 0

    def _save_dialogue_element_on_page(self):
        if self.current_page is None:
            raise RuntimeError()  # TODO error

        if len(self.current_dialogue_element.character_name) == 0:
            raise RuntimeError()  # TODO error

        if len(self.current_dialogue_element.dialogue_text) == 0:
            raise RuntimeError(
                f"Dialogue text for character {self.current_dialogue_element.character_name} is empty"
            )  # TODO error - empty dialogue

        logging.debug(
            f"Saving dialogue element for character {self.current_dialogue_element.character_name} to page number {self.current_page.page_number}"
        )
        self.current_page.dialogue_elements.append(
            deepcopy(self.current_dialogue_element)
        )
        self.current_dialogue_element = None

    def _save_page_in_scenario(self):
        # special case - first page initiated
        if self.current_page.page_number == -1:
            return

        if self.current_page is None:
            raise RuntimeError()  # TODO error

        if len(self.current_page.dialogue_elements) == 0:
            raise RuntimeError()  # TODO error

        logging.debug(
            f"Saving page number {self.current_page.page_number} in scenario."
        )
        self.scenario.pages.append(deepcopy(self.current_page))
        self.current_page = None

    def next_character(self, character_name: str, page_number: int):
        if self.is_finished:
            raise RuntimeError()  # TODO error

        if len(character_name) == 0:
            raise RuntimeError("Character name cannot be empty")

        if page_number <= 0:
            raise RuntimeError(
                f"Page number must be strictly positive number. Got {page_number}"
            )  # TODO error

        if self.current_dialogue_element is not None:
            self._save_dialogue_element_on_page()

        if page_number < self.current_page.page_number:
            raise RuntimeError(
                f"Page number sequence must be non-decreasing. Last page number was {self.current_page.page_number} and current is {page_number}"
            )

        if page_number > self.current_page.page_number:
            self._save_page_in_scenario()
            self.current_page = Page(page_number, [])

        logging.debug(f"Adding character with name {character_name}.")
        self.current_dialogue_element = DialogueElement(
            character_name=character_name,
            dialogue_text="",
            id=self.dialogue_elements_count,
        )
        self.dialogue_elements_count += 1

    def next_dialogue_line(self, dialogue_line: str):
        if self.is_finished:
            raise RuntimeError("Cannot modify builder after calling `build()`")

        if len(dialogue_line) == 0:
            raise RuntimeError("Dialogue line cannot be empty")

        if self.current_dialogue_element is None:
            raise RuntimeError("Character must be added before adding dialogue line")

        logging.debug(
            f"Adding new dialogue line to character with name {self.current_dialogue_element.character_name}"
        )
        if len(self.current_dialogue_element.dialogue_text) > 0:
            self.current_dialogue_element.dialogue_text += "\n"
        self.current_dialogue_element.dialogue_text += dialogue_line

    def build(self):
        try:
            self._save_dialogue_element_on_page()
        except RuntimeError as e:
            logger.warning(f"Don't add last dialogue element due to error `{e}`")
        self._save_page_in_scenario()
        self.is_finished = True

        return self.scenario
