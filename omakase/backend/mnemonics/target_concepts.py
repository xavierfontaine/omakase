"""
Utils for target-concepts type of prompt
"""

from typing import Type

from omakase.backend.mnemonics.base import (
    PromptField,
    PromptFieldsData,
    PromptRow,
    PromptSection,
)


# MOCK - BEGIN
# ===========
# PromptField
# ===========
class _MockField1(PromptField):
    @property
    def prompt_name(self) -> str:
        return "mockfield1"

    @property
    def ui_name(self) -> str:
        return "mockfield1"

    @property
    def ui_explanation(self) -> str:
        return "mockfield1"

    @property
    def ui_placeholder(self) -> str:
        return "mockfield1"


class _MockField2(PromptField):
    @property
    def prompt_name(self) -> str:
        return "mockfield2"

    @property
    def ui_name(self) -> str:
        return "mockfield2"

    @property
    def ui_explanation(self) -> str:
        return "mockfield2"

    @property
    def ui_placeholder(self) -> str:
        return "mockfield2"


# =========
# PromptRow
# =========
class _Row1(PromptRow):
    @property
    def field_classes(
        self,
    ) -> list[Type[PromptField]]:
        """Classes of fields in the row"""
        return [_MockField1]


class _Row2(PromptRow):
    @property
    def field_classes(
        self,
    ) -> list[Type[PromptField]]:
        """Classes of fields in the row"""
        return [_MockField2]


# =============
# PromptSection
# =============
class _Section1(PromptSection):
    @property
    def field_row_class(self) -> Type[PromptRow]:
        """Classes of the field row composing the section."""
        return _Row1

    @property
    def n_repeat(self) -> int:
        return 1

    @property
    def ui_name(self) -> int:
        return "mocksection1"

    @property
    def prompt_name(self) -> int:
        return "mocksection1"

    @property
    def _section_explanation_header(self) -> str:
        return "mocksection1"


class _Section2(PromptSection):
    @property
    def field_row_class(self) -> Type[PromptRow]:
        """Classes of the field row composing the section."""
        return _Row2

    @property
    def n_repeat(self) -> int:
        return 2

    @property
    def ui_name(self) -> int:
        return "mocksection2"

    @property
    def prompt_name(self) -> int:
        return "mocksection2"

    @property
    def _section_explanation_header(self) -> str:
        return "mocksection2"


# ================
# PromptFieldsData
# ================
class MockPromptData(PromptFieldsData):
    @property
    def field_section_classes(self) -> list[Type[PromptSection]]:
        return [_Section1, _Section2]

    @property
    def ui_name(self) -> str:
        """UI name for the prompt type"""
        return "Mock"

    @property
    def template_name(self) -> str:
        """Name of the jinja template (= folder name in '/template')"""
        return "reading_mnem"

    @property
    def template_version(self) -> int:
        """Version of the jinja template (= number in '{number}.jinja')"""
        return 0

    @property
    def _mnem_explanation_header(self):
        return "TO ADD (overall explanation header)"


# MOCK - END
