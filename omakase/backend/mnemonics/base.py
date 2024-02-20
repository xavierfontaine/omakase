from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, fields
from typing import Annotated, Literal, Optional, Type, Union, get_args, get_origin

from beartype import beartype

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
    CachedUserDataPoint,
    point_to_om_user_subcache,
)
from omakase.observer_logic import Observable


class PromptFieldTypeError(Exception):
    """A prompt field has an unexpected type"""

    pass


# ===============
# General classes
# ===============
"""
Developer note:
* PromptField, PromptRow, PromptSection, PromptFieldData form a matryoshka.
* Instantiation a PromptFieldData will instantiate all the inner dolls. The
PromptFieldData `notify` is shared to the inner dolls.
"""

# TODO: further explanation of the method in the docstr ↓


class PromptField(ABC, Observable):
    """Field of a prompt"""

    _DEFAULT_VALUE = ""

    def __init__(self):
        self.value: str = self._DEFAULT_VALUE

    @property
    @abstractmethod
    def prompt_name(self) -> str:
        """Name as it should appear in the prompt"""
        pass

    @property
    @abstractmethod
    def ui_name(self) -> str:
        """Name as it should appear in the UI"""
        pass

    @property
    @abstractmethod
    def ui_explanation(self) -> str:
        """Explanation of the field, as should appear in the help page of the ui"""
        pass

    @property
    @abstractmethod
    def ui_placeholder(self) -> str:
        """Placeholder in the ui when no value is filled in"""
        pass


class PromptRow(ABC, Observable):
    """Row of fields for a prompt

    The notion of a 'row of fields' designates fields that might be:
    - Connected (when one is filled, the other can be pre-filled based on
      existing associations.)
    - Repeated (a section of prompt is defined as a row repeated 1+ times)
    """

    def __init__(self):
        # Init all fields
        self.value: list[PromptField] = [cl() for cl in self.field_classes]
        # Propagate the notify method
        for field in self.value:
            field.notify = self.notify

    @property
    @abstractmethod
    def field_classes(self) -> list[Type[PromptField]]:
        """Classes of fields in the row"""
        pass

    def update_from_store(
        self, field_pos: int, field_value: str, om_username: str
    ) -> None:
        """Get back existing associations of fields for this value of field
        `field_pos`"""
        assoc_store = FieldRowAssocs(
            om_username=om_username, row_class_name=self.__class__.__name__
        )
        assoc = assoc_store.retrieve(field_pos=field_pos, field_value=field_value)
        self.value = assoc

    def store_assoc(self, om_username: str):
        """Store the current field association"""
        assoc_store = FieldRowAssocs(
            om_username=om_username, row_class_name=self.__class__.__name__
        )
        assoc_store.store(field_values=self.value)


class PromptSection(ABC, Observable):
    """A section of fields of a prompt

    Concretely, a PromptRow repeated 1+ times"""

    def __init__(self) -> None:
        # Init the value
        self.value: list[PromptRow] = [
            self.field_row_class() for _ in range(self.n_repeat)
        ]
        # Propagate the notify method
        for row in self.value:
            row.notify = self.notify

    @property
    @abstractmethod
    def field_row_class(self) -> Type[PromptRow]:
        """Classes of the field row composing the section."""
        pass

    @property
    @abstractmethod
    def n_repeat(self) -> int:
        """Number of repetitions of the row."""
        pass

    @property
    @abstractmethod
    def ui_name(self) -> int:
        """Name as displayed in the UI"""
        pass

    @property
    @abstractmethod
    def prompt_name(self) -> int:
        """Name as it should appear in the prompt"""
        pass

    @property
    @abstractmethod
    def _section_explanation_header(self) -> str:
        """Explanation of the section, as should appear in the help page of the ui

        `self.full_ui_explanation` will automatically happen it before teh description
        of the individual fields"""
        pass

    @property
    def full_ui_explanation(self) -> str:
        """Full explanation of the section parameters"""
        full_expl = ""
        # Add name
        full_expl += f"#### {self.ui_name}"
        # Add the header of section expl
        full_expl += f"\n{self._section_explanation_header}"
        # Add field explanations
        full_expl += "\n"
        typical_row = self.value[0]
        for field in typical_row.value:
            field_expl = field.ui_explanation
            field_name = field.ui_name
            full_expl += f"\n* `{field_name}`: {field_expl}"
        return full_expl


class PromptFieldsData(ABC, Observable):
    """Encapsulate all the field data of a prompt

    Concretely, a sequence of PromptSection.
    """

    def __init__(self) -> None:
        # Init the value
        self.value: list[PromptSection] = [cl() for cl in self.field_section_classes]
        # Propagate the notify method
        for section in self.value:
            section.notify = self.notify

    @property
    @abstractmethod
    def field_section_classes(self) -> list[Type[PromptSection]]:
        """Classes of the field sections composing the prompt."""
        pass

    @property
    @abstractmethod
    def ui_name(self) -> str:
        """UI name for the prompt type"""
        pass

    @property
    @abstractmethod
    def _mnem_explanation_header(self):
        """General description of the prompt fields

        `self.generate_help` will automatically happen that to the description of the
        sections"""
        pass

    @property
    def full_mnem_explanation(self) -> str:
        """Full explanation of the prompt parameters"""
        full_expl = ""
        # Add name
        full_expl += f"### {self.ui_name}"
        # Add the header of section expl
        full_expl += f"\n{self._mnem_explanation_header}"
        # Add section expalantions
        for section in self.value:
            full_expl += f"\n{section.full_ui_explanation}"
        return full_expl


# ==============
# Database utils
# ==============
# TODO: put that in a separate module
class FieldRowAssocs:
    """Store and retrieve associations between fields of a prompt row"""

    def __init__(self, om_username: str, row_class_name: str) -> None:
        self._om_username = om_username
        self._row_class_name = row_class_name

    def retrieve(self, field_pos: int, field_value: str) -> list[str]:
        """For this `field_value` of field `field_pos`, return the row association of
        values."""
        # TODO: implement
        # BEGIN MOCK
        print(
            f"Pretending to retrieve for {self._om_username=}, {self._row_class_name},"
            f" {field_pos=} and {field_value=}"
        )
        inst: PromptRow = getattr(globals(), self._row_class_name)()
        row_len = len(inst.value)
        if field_pos == 0 & field_value == "a":
            field_values = ["a"] * row_len
        elif field_pos == 1 & field_value == "b":
            field_values = ["b"] * row_len
        # END MOCK
        return field_values

    def store(self, field_values: list[str]) -> None:
        """Store the current association"""
        # TODO: implement
        # BEGIN MOCK
        print(
            f"Pretending to store for {self._om_username=} and {self._row_class_name},"
            f" the association {field_values=}"
        )
        # END MOCK


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


def get_str_field_names(
    prompt_params_class: Type[PromptParams],
) -> list[PromptParamName]:
    """Return all str fields"""
    out_field_names = []
    for f in fields(prompt_params_class):
        if f.type == str:
            out_field_names.append(f.name)
        elif get_origin(f.type) is Annotated:
            if get_args(f.type)[0] == str:
                out_field_names.append(f.name)
    return out_field_names


@dataclass
class PromptParamFieldUiConf:
    ui_name: str
    ui_explanation: str


@dataclass
class MnemConf:
    prompt_param_class: Type[PromptParams]
    ui_label: str
    ui_descr: str
    template_name: str
    template_version: int
    prompt_param_field_ui_descr: dict[PromptParamName, PromptParamFieldUiConf]


class MnemonicNoteFieldMapData:
    def __init__(
        self,
        prompt_params_class: Type[PromptParams],
        note_type: NoteType,
        note_field_names: list[NoteFieldName],
        om_username: str,
    ):
        """OM user data mapping mnemonic fields (prompt, output) to the note fields

        At instanciation, retrieve the associations between the `note_type` and the
        `prompt_params` type from the om user data.
        1. If the data do not exist yet, initialize the storage.
        2. If the data are not empty, clean up the existing associations, so as to adapt
        to potential changes in prompt parameters or note field names.


        Attributes
            prompt_note_assocs (dict[PromptParamName, Optional[NoteFieldName]]):
            association between **string** prompt parameters and a note field (or None).
            self.genout_note_assocs (Optional[NoteFieldName]): note field associated to
            the generation output, default None

        Methods
            genout_is_associated_to_note_field()
        """
        # Assign params to self
        self._om_username = om_username
        self._note_field_names = note_field_names
        self._prompt_params_class = prompt_params_class
        # Pointer
        self._assocs_root_keys = [  # Root keys to all associations
            MNEM_NOTE_ASSOCS_KEY,
            note_type,
            prompt_params_class.__qualname__,
        ]
        self._prompt_note_assocs: dict[
            PromptParamName, Optional[NoteFieldName]
        ] = self._point_to_prompt_note_assocs()
        # Sanitize
        self._sanitize_prompt_note_assocs()

    def genout_is_associated_to_note_field(self) -> bool:
        """Is the generation output associated to an (existing) note field?"""
        return self.genout_note_assocs in self._note_field_names

    def point_to_genout_note_field_dp(self) -> CachedUserDataPoint:
        # TODO docstr
        dp = CachedUserDataPoint(
            om_username=self._om_username,
            root_keys=self._assocs_root_keys,
            subject_key=GENOUT_NOTE_ASSOCS_KEY,
            default_value=None,
        )
        return dp

    def point_to_prompt_note_assoc_dp(
        self, prompt_param_name: str
    ) -> CachedUserDataPoint:
        # TODO docstr
        dp = CachedUserDataPoint(
            om_username=self._om_username,
            root_keys=self._assocs_root_keys + [PROMPT_NOTE_ASSOCS_KEY],
            subject_key=prompt_param_name,
            default_value=None,
        )
        return dp

    def _point_to_prompt_note_assocs(
        self,
    ) -> dict[PromptParamName, Optional[NoteFieldName]]:
        return point_to_om_user_subcache(
            om_username=self._om_username,
            keys=self._assocs_root_keys + [PROMPT_NOTE_ASSOCS_KEY],
        )

    def _sanitize_prompt_note_assocs(self) -> None:
        """Ensure the names of the note fields stored in memory indeed exist for that
        note type. Check that all the prompt parameter names are accounted for --
        and only them."""
        # Get names of **string** prompt params
        str_prompt_param_names = get_str_field_names(
            prompt_params_class=self._prompt_params_class
        )
        # check for existing prompt param names that exist in user data but shouldn't
        for prompt_param in self._prompt_note_assocs.keys():
            if prompt_param not in str_prompt_param_names:
                del self._prompt_note_assocs[prompt_param]
        # check for existing prompt param associated to an imaginary NoteFieldName
        for prompt_param in self._prompt_note_assocs.keys():
            if self._prompt_note_assocs[prompt_param] not in (
                [None] + self._note_field_names
            ):
                self._prompt_note_assocs[prompt_param] = None


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
    prompt_param_field_ui_descr={
        "target_concept": PromptParamFieldUiConf(
            ui_name="target concept", ui_explanation="TODO"
        ),
        "component_concepts": PromptParamFieldUiConf(
            ui_name="Component concepts", ui_explanation="TODO"
        ),
    },
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
    prompt_param_class=TCRevisionParams,
    ui_label="improve target & components",
    ui_descr=("Improve on a 'target & components' mnemonic."),
    template_name="pure_concepts_revision",
    template_version=0,
    prompt_param_field_ui_descr={
        "mnemonic": PromptParamFieldUiConf(ui_name="mnemonic", ui_explanation="TODO"),
    },
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
