
import os

import yaml

from sophie.utils.logging import log

LANGUAGES = []


def load_all_languages():
    from sophie.modules import LOADED_MODULES

    for module in LOADED_MODULES.values():
        log.debug(f"Loading localizations from {module['name']} module")

        path = f"{module['path']}/translations"
        if not os.path.exists(path):
            log.debug(f"No translations directory found for module {module['name']}")
            continue

        for file_name in os.listdir(path):
            lang_name = file_name.split('.')[0]
            with open(f"{path}/{file_name}") as f:
                lang = yaml.load(f, Loader=yaml.SafeLoader)

                if 'translations' not in LOADED_MODULES[module['name']]:
                    LOADED_MODULES[module['name']]['translations'] = {}

                if lang_name not in LANGUAGES:
                    LANGUAGES.append(lang_name)

                LOADED_MODULES[module['name']]['translations'][lang_name] = lang
