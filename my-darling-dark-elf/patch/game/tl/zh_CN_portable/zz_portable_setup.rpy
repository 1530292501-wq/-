

init 1100 python:
    _zh_font = "tl/zh_CN_portable/NotoSansSC-VF.ttf"
    _zh_fonts = (
        "DejaVuSans.ttf",
        "gui/fonts/default.ttf",
        "gui/fonts/NeverMindHand-Bold.ttf",
        "gui/fonts/NeverMindHand-DemiBold.ttf",
        "gui/fonts/NeverMindHand-Medium.ttf",
        "gui/fonts/NeverMindHand-Regular.ttf",
        "gui/fonts/Nunito-Black.ttf",
        "gui/fonts/Nunito-Bold.ttf",
        "gui/fonts/Nunito-Regular.ttf",
    )
    for _source_font in _zh_fonts:
        config.font_replacement_map[(_source_font, False, False)] = (_zh_font, False, False)
        config.font_replacement_map[(_source_font, True, False)] = (_zh_font, True, False)
        config.font_replacement_map[(_source_font, False, True)] = (_zh_font, False, True)
        config.font_replacement_map[(_source_font, True, True)] = (_zh_font, True, True)


    # Choose the ID set used by the loaded script, not by a machine-specific path.
    if "start_9ab6e64b" in renpy.game.script.translator.default_translates:
        config.language = "zh_CN_portable"
    elif "start_9ab6e64b_1" in renpy.game.script.translator.default_translates:
        config.language = "zh_CN_portable_compat"
    else:
        raise Exception("This Chinese patch does not support the installed game script version.")
