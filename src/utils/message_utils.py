import re

from deep_translator import GoogleTranslator

from src.notifier_logger import get_logger

logger = get_logger(__name__)


def ignore_parts_of_string(input_string: str) -> tuple:
    not_translate_pattern = r"<not_translate>(.*?)<\/not_translate>"
    pattern = re.compile(not_translate_pattern, re.S)
    not_translate_matches = re.findall(pattern, input_string)
    not_translate_split_list = re.split(pattern, input_string)

    return not_translate_matches, not_translate_split_list


def translate_text(text: str, target_lang: str = "en") -> str:
    translator = GoogleTranslator(source="en", target=target_lang)
    not_translate_matches, not_translate_split_list = ignore_parts_of_string(text)

    logger.info(f"NOT TRANSLATE MATCHES -> {not_translate_matches}")
    logger.info(f"not_translate_split_list -> {not_translate_split_list}")

    final_translated_list = []
    for phrase in not_translate_split_list:
        if phrase not in not_translate_matches:
            final_translated_list.append(translator.translate(phrase))
        else:
            final_translated_list.append(phrase)

    logger.info(f"Final translated list -> {not_translate_split_list}")

    return "".join(
        list(
            filter(
                lambda item: item is not None
                and item not in ["<not_translate>", "</not_translate>"],
                final_translated_list,
            )
        )
    )
