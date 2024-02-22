"""
Utils for target-concepts-sound type of prompt
"""

from typing import Type

from omakase.backend.mnemonics.base import (
    PromptField,
    PromptFieldsData,
    PromptRow,
    PromptSection,
)


# ===========
# PromptField
# ===========
class _ComponentConcept(PromptField):
    @property
    def prompt_name(self) -> str:
        return "component_concept"

    @property
    def ui_name(self) -> str:
        return "component concept"

    @property
    def ui_explanation(self) -> str:
        return "Concept related to the component (bath robe')"

    @property
    def ui_placeholder(self) -> str:
        return "concept ('bath robe'...)"


class _ComponentConceptDetails(PromptField):
    @property
    def prompt_name(self) -> str:
        return "component_concept_details"

    @property
    def ui_name(self) -> str:
        return "component concept details"

    @property
    def ui_explanation(self) -> str:
        return (
            "Description of the component concept ('A fancy bath robe, blue"
            " as the sea')"
        )

    @property
    def ui_placeholder(self) -> str:
        return "details ('A fancy bath robe [..]')"


class _Sound(PromptField):
    @property
    def prompt_name(self) -> str:
        return "component_sound"

    @property
    def ui_name(self) -> str:
        return "component sound"

    @property
    def ui_explanation(self) -> str:
        return "The sound associated to the component concept ('りょ')"

    @property
    def ui_placeholder(self) -> str:
        return "Sound ('りょ')"


class _TargetConcept(PromptField):
    @property
    def prompt_name(self) -> str:
        return "target_concept"

    @property
    def ui_name(self) -> str:
        return "target concept"

    @property
    def ui_explanation(self) -> str:
        return "Target concept (e.g., 'voyage', if learning the word 旅行)"

    @property
    def ui_placeholder(self) -> str:
        return "Target concept ('voyage')"


class _TargetMeaningMnemonic(PromptField):
    @property
    def prompt_name(self) -> str:
        return "target_meaning_mnemonic"

    @property
    def ui_name(self) -> str:
        return "target meaning mnemonic"

    @property
    def ui_explanation(self) -> str:
        return (
            "Mnemonic for the target concept (e.g. for 旅行, 'When your family goes, it"
            " is on a voyage.')"
        )

    @property
    def ui_placeholder(self) -> str:
        return "Target leaning mnemonic ('When your family goes, it is on a voyage')"


# =========
# PromptRow
# =========
class _Component(PromptRow):
    @property
    def field_classes(
        self,
    ) -> list[Type[PromptField]]:
        """Classes of fields in the row"""
        return [_Sound, _ComponentConcept, _ComponentConceptDetails]


class _TargetConceptRow(PromptRow):
    @property
    def field_classes(
        self,
    ) -> list[Type[PromptField]]:
        """Classes of fields in the row"""
        return [_TargetConcept]


class _TargetMeaningMnemonicRow(PromptRow):
    @property
    def field_classes(
        self,
    ) -> list[Type[PromptField]]:
        """Classes of fields in the row"""
        return [_TargetMeaningMnemonic]


# =============
# PromptSection
# =============
class _TargetSection(PromptSection):
    @property
    def field_row_class(self) -> Type[PromptRow]:
        """Classes of the field row composing the section."""
        return _TargetConceptRow

    @property
    def n_repeat(self) -> int:
        return 1

    @property
    def ui_name(self) -> int:
        return "target concept"

    @property
    def prompt_name(self) -> int:
        return "target_concept"

    @property
    def _section_explanation_header(self) -> str:
        return (
            "The concept behind the word under study. For instance," " 'voyage' for 旅行."
        )


class _TargetMeaningMnemonicSection(PromptSection):
    @property
    def field_row_class(self) -> Type[PromptRow]:
        """Classes of the field row composing the section."""
        return _TargetMeaningMnemonicRow

    @property
    def n_repeat(self) -> int:
        return 1

    @property
    def ui_name(self) -> int:
        return "target meaning mnemonic"

    @property
    def prompt_name(self) -> int:
        return "target_meaning_mnemonic"

    @property
    def _section_explanation_header(self) -> str:
        return ""


class _ComponentSounds(PromptSection):
    @property
    def field_row_class(self) -> Type[PromptRow]:
        """Classes of the field row composing the section."""
        return _Component

    @property
    def n_repeat(self) -> int:
        return 4

    @property
    def ui_name(self) -> int:
        return "component sounds"

    @property
    def prompt_name(self) -> int:
        return "components"

    @property
    def _section_explanation_header(self) -> str:
        return (
            "The overall reading of the concept is composed into components ('voyage'"
            " → []りょ,こ]). Each of them becomes an association of a concept, details"
            " about that concept, and a sound."
        )


# ================
# PromptFieldsData
# ================
class SoundTargetComponents(PromptFieldsData):
    @property
    def field_section_classes(self) -> list[Type[PromptSection]]:
        return [_TargetSection, _TargetMeaningMnemonicSection, _ComponentSounds]

    @property
    def ui_name(self) -> str:
        """UI name for the prompt type"""
        return "Sound Target Components"

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


# TODO: remove
# =====
# Tests
# =====
if __name__ == "__main__":
    # Sound component explanation
    stc = SoundTargetComponents()
    print(stc.full_mnem_explanation)
    # Sound component to dict
    __import__("pprint").pp(
        stc.to_dict(drop_empty_rows=False, raise_when_empty_value_remains=False)
    )
    print(stc.value)
    # Filling in the TargetSection
    stc.value["target_concept"].value[0].value["target_concept"].value = "a"
    stc.value["target_meaning_mnemonic"].value[0].value[
        "target_meaning_mnemonic"
    ].value = "b"
    stc.value["components"].value[0].value["component_concept"].value = "c1"
    stc.value["components"].value[0].value["component_concept_details"].value = "c2"
    stc.value["components"].value[0].value["component_sound"].value = "c3"
    stc.value["components"].value[2].value["component_concept"].value = "d1"
    stc.value["components"].value[2].value["component_concept_details"].value = "d2"
    stc.value["components"].value[2].value["component_sound"].value = "d3"
    __import__("pprint").pp(
        stc.to_dict(drop_empty_rows=True, raise_when_empty_value_remains=True)
    )
    # Sound component to dict
    __import__("pprint").pp(stc.to_dict())
    # Render
    print(stc.get_1d_prompt_section_names())
    print(stc.get_prompt())
