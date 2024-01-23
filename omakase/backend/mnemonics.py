from copy import deepcopy
from dataclasses import dataclass, fields
from typing import Literal, Optional, Type, Union

from omakase.annotations import (
    ComponentConcept,
    NoteFieldName,
    NoteType,
    PromptParamName,
    TargetConcept,
)
from omakase.backend.om_user import (
    GENOUT_NOTE_ASSOCS_KEY,
    MNEM_NOTE_ASSOCS_KEY,
    PROMPT_NOTE_ASSOCS_KEY,
)


class PromptFieldTypeError(Exception):
    """A prompt field has an unexpected type"""

    pass


# ===============
# General classes
# ===============
@dataclass
class PromptParams:
    """A generic dataclass for prompt parameters.

    Fields must be str, dict[str, str] or dict[str, dict[str, str]].
    """

    pass

    def non_filled_out_fields(self) -> list[PromptParamName]:
        """Return non-optional fields that haven't been filled out.

        For dict fields, we need at least one element to be non-null."""
        non_field_out = []
        fields_names = self._get_fields_names()
        for field_name in fields_names:
            field_value = self._get_field_attribute(field_name=field_name)
            if not self._field_is_filled_out(
                field_value=field_value, field_name=field_name
            ):
                non_field_out.append(field_name)
        return non_field_out

    def get_filled_out_fields_subfields(
        self,
    ) -> dict[PromptParamName, Union[str, dict[str, str], dict[str, dict[str, str]]]]:
        """Return the dict of parameters, leaving out empty fields/subfields"""
        # Drop the empty fields
        filled_field_names = [
            n for n in self._get_fields_names() if n not in self.non_filled_out_fields()
        ]
        output = {
            n: deepcopy(self._get_field_attribute(field_name=n))
            for n in filled_field_names
        }
        # Drop the empty subfields
        for field_name, field_value in output.items():
            if isinstance(field_value, dict):
                subfields_to_drop = []
                for subfield_name, subfield_value in field_value.items():
                    if not self._field_is_filled_out(
                        field_value=subfield_value, field_name=subfield_name
                    ):
                        subfields_to_drop.append(subfield_name)
                [field_value.pop(to_drop) for to_drop in subfields_to_drop]
        return output

    def _get_fields_names(self) -> list[PromptParamName]:
        """Return all fields (class attributes)"""
        return [f.name for f in fields(self)]

    def get_str_field_names(self) -> list[PromptParamName]:
        """Return all str fields"""
        return [f.name for f in fields(self) if f.type == str]

    def _get_field_attribute(
        self, field_name: str
    ) -> Union[str, dict[str, str], dict[str, dict[str, str]]]:
        """Return value associated to a field"""
        return self.__getattribute__(field_name)

    def _field_is_filled_out(self, field_value: str, field_name: str) -> bool:
        """Check if all fields are str or nested dict of str with at least one
        non-null value"""
        if isinstance(field_value, str):
            return field_value != ""
        elif isinstance(field_value, dict):
            return self._is_nested_dict_nonempty_str(
                d=field_value, field_name=field_value
            )
        else:
            raise PromptFieldTypeError(self._field_error_message(field_name=field_name))

    def _is_nested_dict_nonempty_str(self, d: dict, field_name: str) -> bool:
        """Is field a (nested or plain) dict of str, with some non-empty?"""
        if len(d) == 0:
            return False
        elif all(isinstance(v, str) for v in d.values()):
            if all(v == "" for v in d.values()):
                return False
        elif all(isinstance(v, dict) for v in d.values()):
            for v in d.values():
                self._is_nested_dict_nonempty_str(d=v, field_name=field_name)
        else:
            raise PromptFieldTypeError(self._field_error_message(field_name=field_name))
        return True

    @staticmethod
    def _field_error_message(field_name: str) -> str:
        """Return error msg for field type errors"""
        error_msg = (
            "Field {field_name} is not str, dict[str, str] or dict[str, dict[str, str]]"
        )
        return error_msg.format(field_name=field_name)


@dataclass
class MnemConf:
    prompt_param_class: Type[PromptParams]
    ui_label: str
    ui_descr: str
    template_name: str
    template_version: int


class MnemonicNoteFieldMapper:
    def __init__(
        self,
        prompt_params: PromptParams,
        note_type: NoteType,
        note_field_names: list[NoteFieldName],
        om_user_data: dict,
    ):
        """Map mnemonic fields (prompt, output) to note fields

        Attributes
            prompt_note_assocs (dict[PromptParamName, Optional[NoteFieldName]]):
            association between **string** prompt parameters and a note field (or None).
            self.genout_note_assocs (Optional[NoteFieldName]): note field associated to
            the generation output, default None
        """
        # Assign params to self
        self._om_user_data = om_user_data
        self._note_type = note_type
        self._note_field_names = note_field_names
        self._prompt_params = prompt_params
        self._prompt_params_type = type(prompt_params).__name__
        # init
        self._init_om_user_data_if_not()
        self.prompt_note_assocs: dict[
            PromptParamName, Optional[NoteFieldName]
        ] = self._point_to_prompt_note_assocs()
        self.genout_note_assocs: Optional[
            NoteFieldName
        ] = self._point_to_genout_note_assocs()
        # Sanitize
        self._sanitize_prompt_note_assocs()
        self._sanitize_genout_note_assocs()

    def _point_to_prompt_note_assocs(
        self,
    ) -> dict[PromptParamName, Optional[NoteFieldName]]:
        return self._om_user_data[MNEM_NOTE_ASSOCS_KEY][self._note_type][
            self._prompt_params_type
        ][PROMPT_NOTE_ASSOCS_KEY]

    def _point_to_genout_note_assocs(
        self,
    ) -> Optional[NoteFieldName]:
        return self._om_user_data[MNEM_NOTE_ASSOCS_KEY][self._note_type][
            self._prompt_params_type
        ][GENOUT_NOTE_ASSOCS_KEY]

    def _init_om_user_data_if_not(self) -> None:
        if MNEM_NOTE_ASSOCS_KEY not in self._om_user_data:
            self._om_user_data[MNEM_NOTE_ASSOCS_KEY] = dict()
        # Structure for this specific note type and prompt param type
        if PROMPT_NOTE_ASSOCS_KEY not in self._om_user_data[MNEM_NOTE_ASSOCS_KEY]:
            self._om_user_data[MNEM_NOTE_ASSOCS_KEY] = dict()
        if self._note_type not in self._om_user_data[MNEM_NOTE_ASSOCS_KEY]:
            self._om_user_data[MNEM_NOTE_ASSOCS_KEY][self._note_type] = dict()
        if (
            self._prompt_params_type
            not in self._om_user_data[MNEM_NOTE_ASSOCS_KEY][self._note_type]
        ):
            self._om_user_data[MNEM_NOTE_ASSOCS_KEY][self._note_type][
                self._prompt_params_type
            ] = dict()
        # Adding the PROMPT_NOTE_ASSOCS_KEY and GENOUT_NOTE_ASSOCS_KEY layers
        assocs = self._om_user_data[MNEM_NOTE_ASSOCS_KEY][self._note_type][
            self._prompt_params_type
        ]
        if PROMPT_NOTE_ASSOCS_KEY not in assocs:
            assocs[PROMPT_NOTE_ASSOCS_KEY] = dict()
        if GENOUT_NOTE_ASSOCS_KEY not in assocs:
            assocs[GENOUT_NOTE_ASSOCS_KEY] = None

    def _sanitize_prompt_note_assocs(self) -> None:
        str_prompt_param_names = self._prompt_params.get_str_field_names()
        # check for existing prompt param names that exist in user data but shouldn't
        for prompt_param in self.prompt_note_assocs:
            if prompt_param not in str_prompt_param_names:
                del self.prompt_note_assocs[prompt_param]
        # Check for prompt param names that should be in the user data but aren't
        for prompt_param in str_prompt_param_names:
            if prompt_param not in self.prompt_note_assocs:
                self.prompt_note_assocs[prompt_param] = None
        # check for existing prompt param associated to an imaginary NoteFieldName
        for prompt_param in self.prompt_note_assocs:
            if str_prompt_param_names not in [None] + self._note_field_names:
                self.prompt_note_assocs[prompt_param] = None

    def _sanitize_genout_note_assocs(self) -> None:
        if self.genout_note_assocs is not None:
            if self.genout_note_assocs not in self._note_field_names:
                self.genout_note_assocs = None


# ========================
# Target concept mnemonics
# ========================
@dataclass
class TCParams(PromptParams):
    """
    Associate a Target concept (to learn,) with Component concepts (available
    at the time of recall.)
    """

    target_concept: TargetConcept
    component_concepts: dict[str, ComponentConcept]


tc_mnem_conf = MnemConf(
    prompt_param_class=TCParams,
    ui_label="target & components",
    ui_descr=(
        "Associate a target to remember with component concepts available during recall"
    ),
    template_name="pure_concepts",
    template_version=0,
)


# ==============================
# Target concept mnemonic update
# ==============================
@dataclass
class TCRevisionParams(PromptParams):
    """
    Inherits from TCParams. Used for mnemonic revision.
    """

    mnemonic: str


tc_revision_mnem_conf = MnemConf(
    prompt_param_class=TCParams,
    ui_label="improve target & components",
    ui_descr=("Improve on a 'target & components' mnemonic."),
    template_name="pure_concepts_revision",
    template_version=0,
)


# ===============================
# Target concept reading mnemonic
# ===============================
@dataclass
class TCSoundParams(PromptParams):
    """
    Associate a Target concept (to learn,) with the *sound* of a Component concepts.
    """

    target_concept: TargetConcept
    component_concepts_sounds: dict[
        str, dict[Literal["concept", "details", "sound"], str]
    ]
    meaning_mnemonic: str
