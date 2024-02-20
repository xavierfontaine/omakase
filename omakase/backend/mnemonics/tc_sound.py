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
class ComponentConcept(PromptField):
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


class ComponentConceptDetails(PromptField):
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


class Sound(PromptField):
    @property
    def prompt_name(self) -> str:
        return "sound"

    @property
    def ui_name(self) -> str:
        return "sound"

    @property
    def ui_explanation(self) -> str:
        return "The sound associated to the component concept ('りょ')"

    @property
    def ui_placeholder(self) -> str:
        return "Sound ('りょ')"


class TargetConcept(PromptField):
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


class TargetMeaningMnemonic(PromptField):
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
class Component(PromptRow):
    @property
    def field_classes(
        self,
    ) -> list[Type[PromptField]]:
        """Classes of fields in the row"""
        return [Sound, ComponentConcept, ComponentConceptDetails]


class TargetConceptRow(PromptRow):
    @property
    def field_classes(
        self,
    ) -> list[Type[PromptField]]:
        """Classes of fields in the row"""
        return [TargetConcept]


class TargetMeaningMnemonicRow(PromptRow):
    @property
    def field_classes(
        self,
    ) -> list[Type[PromptField]]:
        """Classes of fields in the row"""
        return [TargetMeaningMnemonic]


# =============
# PromptSection
# =============
class ComponentSounds(PromptSection):
    @property
    def field_row_class(self) -> Type[PromptRow]:
        """Classes of the field row composing the section."""
        return Component

    @property
    def n_repeat(self) -> int:
        return 4

    @property
    def ui_name(self) -> int:
        return "component"

    @property
    def prompt_name(self) -> int:
        return "component"

    @property
    def _section_explanation_header(self) -> str:
        return (
            "The overall reading of the concept is composed into components ('voyage'"
            " → []りょ,こ]). Each of them becomes an association of a concept, details"
            " about that concept, and a sound."
        )


class TargetSection(PromptSection):
    @property
    def field_row_class(self) -> Type[PromptRow]:
        """Classes of the field row composing the section."""
        return TargetConceptRow

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


class TargetMeaningMnemonicSection(PromptSection):
    @property
    def field_row_class(self) -> Type[PromptRow]:
        """Classes of the field row composing the section."""
        return TargetMeaningMnemonicRow

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


# ================
# PromptFieldsData
# ================
class SoundTargetComponents(PromptFieldsData):
    @property
    def field_section_classes(self) -> list[Type[PromptSection]]:
        return [TargetSection, TargetMeaningMnemonicSection, ComponentSounds]

    @property
    def ui_name(self) -> str:
        """UI name for the prompt type"""
        return "Sound Target Components"

    @property
    def _mnem_explanation_header(self):
        return "TO ADD (overall explanation header)"


if __name__ == "__main__":
    stc = SoundTargetComponents()
    print(stc.full_mnem_explanation)
