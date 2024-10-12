from .scenario import Page, DialogueElement, Scenario, ScenarioBuilder
from typing import BinaryIO
import pymupdf
from html.parser import HTMLParser
from dataclasses import dataclass
from typing import List


class MyHTMLParser(HTMLParser):
    # listener - function accepting two values
    #   - left position of the text
    #   - text
    def __init__(self, listener, page_number, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.last_visited_left_pos = None
        self.is_in_span = False
        self.listener = listener
        self.page_number = page_number

    def handle_starttag(self, tag, attrs):
        if tag == "p":
            for attr in attrs:
                if attr[0] == "style":
                    # assume that attr[1] is in following format
                    # top:698.4pt;left:91.0pt;line-height:12.0pt
                    for attr_element in attr[1].split(";"):
                        # assume that attr_element is in following format
                        # top:698.4pt
                        attr_split = attr_element.split(":")
                        if attr_split[0] == "left":
                            # assume that attr_split[1] is in format 111.1pt
                            if self.last_visited_left_pos is not None:
                                raise RuntimeError()  # TODO some error
                            self.last_visited_left_pos = float(attr_split[1][:-2])
        elif tag == "span":
            if self.is_in_span:
                raise RuntimeError()  # TODO error
            self.is_in_span = True

    def handle_endtag(self, tag):
        if tag == "p":
            if self.last_visited_left_pos is None:
                raise RuntimeError()  # TODO some error
            self.last_visited_left_pos = None
        if tag == "span":
            if not self.is_in_span:
                raise RuntimeError()  # TODO error
            self.is_in_span = False

    def handle_data(self, data):
        if self.is_in_span:
            self.listener(self.last_visited_left_pos, data, self.page_number)


# algorithm
# 1) read text (html?) to get info about positions
# 2) guessing by distance from left
#   - the most often appearing position means text
#   - other are
#       - character names
#       - <didaskalia>
#       - other things we're not interested ine
#   The exact order might differ - the other heuristic is length of each
#   part. Character names will be short (probably most often just 1 word, very
#   often written in UPPER CASE), and the stage directions should contain more
#   diverse words.


class _ScenarioFromPdf:
    MAX_DIST_IN_GROUP_PT = 20

    @dataclass
    class PageElement:
        position: float
        text: str
        page_number: int

    @dataclass
    class Group:
        left_position: float
        number_of_elements: int

        def is_position_in_group(self, position):
            return (
                abs(position - self.left_position)
                <= _ScenarioFromPdf.MAX_DIST_IN_GROUP_PT
            )

    def __init__(self) -> None:
        # array of PageElements
        self.finalized = False
        self.page_content: List[_ScenarioFromPdf.PageElement] = []

    def listener(self, position, text, page_number):
        if self.finalized:
            raise RuntimeError()  # TODO error
        self.page_content.append(
            _ScenarioFromPdf.PageElement(position, text, page_number)
        )

    def _get_biggest_group(self, groups: List[Group]):
        biggest_group = groups[0]
        for group in groups:
            if group.number_of_elements > biggest_group.number_of_elements:
                biggest_group = group
        return biggest_group

    def _get_group_with_most_uppercase_words(self, groups: List[Group]):
        most_uppercase_words = 0
        group_with_most_uppercase_words = None
        for group in groups:
            num_uppercase_words_in_group = 0
            for page_element in self.page_content:
                if (
                    group.is_position_in_group(page_element.position)
                    and page_element.text.isupper()
                ):
                    num_uppercase_words_in_group += 1

            if num_uppercase_words_in_group > most_uppercase_words:
                most_uppercase_words = num_uppercase_words_in_group
                group_with_most_uppercase_words = group

        return group_with_most_uppercase_words

    def finalize(self):
        if self.finalized:
            raise RuntimeError()  # TODO error

        sorted_positions = sorted([element.position for element in self.page_content])

        groups: List[_ScenarioFromPdf.Group] = [
            _ScenarioFromPdf.Group(sorted_positions[0], 1)
        ]
        for position in sorted_positions:
            if not groups[-1].is_position_in_group(position):
                groups.append(_ScenarioFromPdf.Group(position, 1))
            else:
                groups[-1].number_of_elements += 1

        # biggest group refers to text
        text_group = self._get_biggest_group(groups)

        # group with most uppercase elements refers to character names
        character_name_group = self._get_group_with_most_uppercase_words(groups)

        scenario_builder = ScenarioBuilder()
        for element in self.page_content:
            if character_name_group.is_position_in_group(element.position):
                scenario_builder.next_character(element.text, element.page_number)
            elif text_group.is_position_in_group(element.position):
                scenario_builder.next_dialogue_line(element.text)

        return scenario_builder.build()


def scenario_from_pdf(file_path: str) -> Scenario:
    doc = pymupdf.open(file_path)
    scenario_from_pdf = _ScenarioFromPdf()
    for page_number, page in enumerate(doc):
        text = page.get_text("html")
        parser = MyHTMLParser(scenario_from_pdf.listener, page_number + 1)
        parser.feed(text)

    return scenario_from_pdf.finalize()
