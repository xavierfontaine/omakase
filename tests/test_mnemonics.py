from dataclasses import dataclass

import pytest

from omakase.backend.mnemonics import PromptFieldTypeError, PromptParams


@dataclass
class SimplePromptParams(PromptParams):
    field1: str
    field2: list[str]


def test_non_filled_out_fields():
    # Everything is fine
    instance = SimplePromptParams(field1="bla", field2={"k1": "a", "k2": "b"})
    assert instance.non_filled_out_fields() == []
    # Everything is fine (missing 1 str in list)
    instance = SimplePromptParams(field1="bla", field2={"k1": "", "k2": "b"})
    assert instance.non_filled_out_fields() == []
    # Missing str in list
    instance = SimplePromptParams(field1="", field2={"k1": "a", "k2": "b"})
    assert instance.non_filled_out_fields() == ["field1"]
    # Missing all str in list
    instance = SimplePromptParams(field1="bla", field2={"k1": "", "k2": ""})
    assert instance.non_filled_out_fields() == ["field2"]
    # Everything is missing
    instance = SimplePromptParams(field1="", field2={"k1": "", "k2": ""})
    assert instance.non_filled_out_fields() == ["field1", "field2"]
    # Type error in str
    instance = SimplePromptParams(field1=2, field2={"k1": "a", "k2": "b"})
    with pytest.raises(PromptFieldTypeError):
        instance.non_filled_out_fields()
    # Type error in list
    instance = SimplePromptParams(field1="", field2={"k1": None, "k2": "b"})
    with pytest.raises(PromptFieldTypeError):
        instance.non_filled_out_fields()
