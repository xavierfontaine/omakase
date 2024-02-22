"""
Utils for building prompts for mnemonics
- the `base` module refers to general utils
- each of the the other modules is specific to a prompt type
- The current module imports all the PromptData from the specific prompt
"""

from omakase.backend.mnemonics.tc_sound import SoundTargetComponents
