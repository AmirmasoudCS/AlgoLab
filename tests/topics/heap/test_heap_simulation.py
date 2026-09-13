import pytest

from algolab.topics.heap.model import Heap, HeapType


class TestHeapProperties:
    def test_new_heap_is_empty(self):
        heap = Heap[int]()

        assert heap.is_empty
        assert heap.size == 0
        assert heap.values == []
        assert heap.heap_type is HeapType.MIN

    def test_max_heap_has_max_type(self):
        heap = Heap[int](HeapType.MAX)

        assert heap.heap_type is HeapType.MAX


class TestHeapInsert:
    def test_insert_into_empty_min_heap(self):
        heap = Heap[int](HeapType.MIN)

        heap.insert(10)

        assert heap.values == [10]
        assert heap.size == 1
        assert heap.peek() == 10

    def test_insert_bubbles_up_in_min_heap(self):
        heap = Heap[int](HeapType.MIN)

        heap.insert(30)
        heap.insert(20)
        heap.insert(10)

        assert heap.values == [10, 30, 20]

    def test_insert_bubbles_up_in_max_heap(self):
        heap = Heap[int](HeapType.MAX)

        heap.insert(10)
        heap.insert(20)
        heap.insert(30)

        assert heap.values == [30, 10, 20]

    def test_insert_allows_duplicates(self):
        heap = Heap[int](HeapType.MIN)

        heap.insert(10)
        heap.insert(10)
        heap.insert(5)

        assert heap.values == [5, 10, 10]
        assert heap.size == 3


class TestHeapPeek:
    def test_peek_returns_root_without_removing_it(self):
        heap = Heap[int](HeapType.MIN)

        heap.insert(20)
        heap.insert(10)
        heap.insert(30)

        assert heap.peek() == 10
        assert heap.values == [10, 20, 30]
        assert heap.size == 3

    def test_peek_returns_maximum_in_max_heap(self):
        heap = Heap[int](HeapType.MAX)

        heap.insert(20)
        heap.insert(10)
        heap.insert(30)

        assert heap.peek() == 30

    def test_peek_empty_heap_raises_error(self):
        heap = Heap[int]()

        with pytest.raises(
            IndexError,
            match="Cannot peek at an empty heap.",
        ):
            heap.peek()


class TestHeapExtract:
    def test_extract_returns_minimum_from_min_heap(self):
        heap = Heap[int](HeapType.MIN)

        heap.build_heap([40, 10, 30, 20, 50])

        assert heap.extract() == 10
        assert heap.peek() == 20
        assert heap.size == 4

    def test_extract_returns_maximum_from_max_heap(self):
        heap = Heap[int](HeapType.MAX)

        heap.build_heap([40, 10, 30, 20, 50])

        assert heap.extract() == 50
        assert heap.peek() == 40
        assert heap.size == 4

    def test_extract_from_single_element_heap(self):
        heap = Heap[int](HeapType.MIN)

        heap.insert(10)

        assert heap.extract() == 10
        assert heap.is_empty
        assert heap.values == []

    def test_extract_from_empty_heap_raises_error(self):
        heap = Heap[int]()

        with pytest.raises(
            IndexError,
            match="Cannot extract from an empty heap.",
        ):
            heap.extract()

    def test_extract_maintains_min_heap_property(self):
        heap = Heap[int](HeapType.MIN)

        heap.build_heap(
            [50, 20, 40, 10, 30, 5, 15]
        )

        extracted_values = []

        while not heap.is_empty:
            extracted_values.append(
                heap.extract()
            )

        assert extracted_values == [
            5,
            10,
            15,
            20,
            30,
            40,
            50,
        ]

    def test_extract_maintains_max_heap_property(self):
        heap = Heap[int](HeapType.MAX)

        heap.build_heap(
            [50, 20, 40, 10, 30, 5, 15]
        )

        extracted_values = []

        while not heap.is_empty:
            extracted_values.append(
                heap.extract()
            )

        assert extracted_values == [
            50,
            40,
            30,
            20,
            15,
            10,
            5,
        ]


class TestHeapBuild:
    def test_build_heap_creates_min_heap(self):
        heap = Heap[int](HeapType.MIN)

        heap.build_heap(
            [40, 10, 30, 20, 50, 5]
        )

        assert heap.values == [
            5,
            10,
            30,
            20,
            50,
            40,
        ]

    def test_build_heap_creates_max_heap(self):
        heap = Heap[int](HeapType.MAX)

        heap.build_heap(
            [40, 10, 30, 20, 50, 5]
        )

        assert heap.values == [
            50,
            20,
            30,
            10,
            40,
            5,
        ]

    def test_build_heap_replaces_existing_values(self):
        heap = Heap[int](HeapType.MIN)

        heap.insert(100)
        heap.insert(200)

        heap.build_heap([30, 10, 20])

        assert heap.values == [10, 30, 20]
        assert heap.size == 3

    def test_build_heap_with_empty_list(self):
        heap = Heap[int](HeapType.MIN)

        heap.build_heap([])

        assert heap.is_empty
        assert heap.values == []


class TestHeapClear:
    def test_clear_removes_all_values(self):
        heap = Heap[int](HeapType.MIN)

        heap.build_heap(
            [10, 20, 30, 40]
        )

        heap.clear()

        assert heap.is_empty
        assert heap.size == 0
        assert heap.values == []

    def test_clear_empty_heap(self):
        heap = Heap[int]()

        heap.clear()

        assert heap.is_empty
        assert heap.values == []


class TestHeapValues:
    def test_values_returns_copy(self):
        heap = Heap[int](HeapType.MIN)

        heap.build_heap(
            [30, 10, 20]
        )

        values = heap.values
        values.append(100)

        assert heap.values == [
            10,
            30,
            20,
        ]
        assert heap.size == 3