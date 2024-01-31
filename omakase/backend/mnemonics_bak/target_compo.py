from omakase.backend.mnemonics.base import (
    FullPromptParams,
    FullPromptParamsConf,
    PromptParam,
    PromptParamConf,
    PromptParamsRow,
    PromptParamsSection,
    PromptParamsSectionConf,
)

TC_PARAM_NAME = "target_concept"
COMPO_PARAM_NAME = "component"
COMPO_PARAM_NAME = "component"


tc_target_param_conf = PromptParamConf(
    ui_name="target concept", default_value="", ui_descr="Target concept to learn"
)
tc_component_param_conf = PromptParamConf(
    ui_name="Component concept",
    default_value="",
    ui_descr="component concept available at recall time",
)
tc_section_conf = PromptParamsSectionConf(ui_title="Target concept", ui_descr="")
tc_full_conf = FullPromptParamsConf(
    ui_title="Target & Component Concepts",
    ui_descr="Associate a target concept to component concepts",
)


def make_blank_tc_prompt_params() -> FullPromptParams:
    return FullPromptParams(
        conf=tc_full_conf,
        value=[
            PromptParamsSection(
                value=[
                    PromptParamsRow(
                        value=[PromptParam(value="", conf=tc_target_param_conf)],
                    ),
                    PromptParamsRow(
                        value=[PromptParam(value="", conf=tc_component_param_conf)] * 3,
                    ),
                ],
                conf=tc_section_conf,
            )
        ],
    )
