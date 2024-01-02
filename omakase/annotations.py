"""
Custom annotated types
"""
from typing import Annotated

FieldName = Annotated[str, "Field of a note"]
FieldValue = Annotated[str, "Value of a note"]
