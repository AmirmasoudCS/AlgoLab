import pytest

from algolab.topics.linked_list.model import LinkedListModel


def _list(*values):
    model = LinkedListModel()

    for value in values:
        model.insert_at_end(value)

    return model


def test_round_trip_preserves_order_and_links():
    restored = LinkedListModel.from_dict(_list(10, 20, 30).to_dict())

    assert restored.to_list() == [10, 20, 30]
    assert restored.size == 3
    assert restored.head.data == 10
    assert restored.head.next.next.next is None
    assert restored.search(30) == 2


def test_empty_list_round_trips():
    restored = LinkedListModel.from_dict(LinkedListModel().to_dict())

    assert restored.is_empty and restored.size == 0 and restored.head is None


def test_a_loaded_list_keeps_working():
    restored = LinkedListModel.from_dict(_list(1, 2, 3).to_dict())

    restored.insert_at_beginning(0)
    restored.insert_at_end(4)
    restored.delete_at(2)

    assert restored.to_list() == [0, 1, 3, 4] and restored.size == 4


def test_mixed_scalars_round_trip():
    original = _list(1, "two", 3.5, None)

    assert LinkedListModel.from_dict(original.to_dict()).to_list() == [1, "two", 3.5, None]


@pytest.mark.parametrize(
    "bad",
    [None, [], {}, {"items": "abc"}, {"items": [[1]]}, {"items": [float("inf")]}],
)
def test_from_dict_rejects_malformed_data(bad):
    with pytest.raises(ValueError):
        LinkedListModel.from_dict(bad)


def test_from_dict_rejects_oversized_lists():
    with pytest.raises(ValueError, match="at most"):
        LinkedListModel.from_dict(
            {"items": list(range(LinkedListModel.MAX_LOADED_ITEMS + 1))}
        )


def test_replace_with_takes_over_the_other_list():
    target = _list(1)
    source = LinkedListModel.from_dict({"items": [7, 8, 9]})

    target.replace_with(source)

    assert target.to_list() == [7, 8, 9] and target.size == 3