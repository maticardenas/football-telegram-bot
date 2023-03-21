from src.utils.message_utils import ignore_parts_of_string


def test_ignore_parts_of_string():
    # given
    text = "This should not be ignored <not_translate>but it should!</not_translate>"

    # when
    not_translate_matches, not_translate_split_list = ignore_parts_of_string(text)

    # then
    assert not_translate_matches == ["but it should!"]
    assert not_translate_split_list == [
        "This should not be ignored ",
        "but it should!",
        "",
    ]


def test_ignore_parts_all_translatable():
    # given
    text = "This should not be ignored and this neither!"

    # when
    not_translate_matches, not_translate_split_list = ignore_parts_of_string(text)

    # then
    assert not_translate_matches == []
    assert not_translate_split_list == ["This should not be ignored and this neither!"]


def test_ignore_parts_all_ignored():
    # given
    text = "<not_translate>All this should be ignored!</not_translate>"

    # when
    not_translate_matches, not_translate_split_list = ignore_parts_of_string(text)

    # then
    assert not_translate_matches == ["All this should be ignored!"]
    assert not_translate_split_list == ["", "All this should be ignored!", ""]
