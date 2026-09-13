from algolab.topics.heap.model import Heap, HeapType
from algolab.topics.heap.operations import (
    BuildHeapOperation,
    ClearOperation,
    ExtractOperation,
    InsertOperation,
    PeekOperation,
)


class TestInsertOperation:
    def test_commit_inserts_value(self):
        heap = Heap[int](HeapType.MIN)
        operation = InsertOperation(10)

        result = operation.commit(heap)

        assert result is None
        assert heap.values == [10]

    def test_commit_respects_min_heap_order(self):
        heap = Heap[int](HeapType.MIN)
        operation = InsertOperation(10)

        heap.insert(20)

        operation.commit(heap)

        assert heap.values == [10, 20]

    def test_commit_respects_max_heap_order(self):
        heap = Heap[int](HeapType.MAX)
        operation = InsertOperation(20)

        heap.insert(10)

        operation.commit(heap)

        assert heap.values == [20, 10]

    def test_insert_allows_duplicate_values(self):
        heap = Heap[int](HeapType.MIN)
        operation = InsertOperation(10)

        operation.commit(heap)
        operation.commit(heap)

        assert heap.values == [10, 10]


class TestPeekOperation:
    def test_commit_returns_root(self):
        heap = Heap[int](HeapType.MIN)

        heap.build_heap([30, 10, 20])

        operation = PeekOperation()

        result = operation.commit(heap)

        assert result == 10
        assert heap.values == [10, 30, 20]

    def test_commit_returns_maximum_for_max_heap(self):
        heap = Heap[int](HeapType.MAX)

        heap.build_heap([30, 10, 20])

        operation = PeekOperation()

        result = operation.commit(heap)

        assert result == 30

    def test_commit_on_empty_heap_raises_error(self):
        heap = Heap[int](HeapType.MIN)
        operation = PeekOperation()

        try:
            operation.commit(heap)
            assert False
        except IndexError as error:
            assert str(error) == (
                "Cannot peek at an empty heap."
            )


class TestExtractOperation:
    def test_commit_extracts_root(self):
        heap = Heap[int](HeapType.MIN)

        heap.build_heap([30, 10, 20])

        operation = ExtractOperation()

        result = operation.commit(heap)

        assert result == 10
        assert heap.values == [20, 30]

    def test_commit_extracts_maximum_from_max_heap(self):
        heap = Heap[int](HeapType.MAX)

        heap.build_heap([30, 10, 20])

        operation = ExtractOperation()

        result = operation.commit(heap)

        assert result == 30
        assert heap.values == [20, 10]

    def test_commit_on_empty_heap_raises_error(self):
        heap = Heap[int](HeapType.MIN)
        operation = ExtractOperation()

        try:
            operation.commit(heap)
            assert False
        except IndexError as error:
            assert str(error) == (
                "Cannot extract from an empty heap."
            )


class TestBuildHeapOperation:
    def test_commit_builds_min_heap(self):
        heap = Heap[int](HeapType.MIN)

        operation = BuildHeapOperation(
            [40, 10, 30, 20, 50, 5]
        )

        result = operation.commit(heap)

        assert result is None
        assert heap.peek() == 5
        assert heap.size == 6

    def test_commit_builds_max_heap(self):
        heap = Heap[int](HeapType.MAX)

        operation = BuildHeapOperation(
            [40, 10, 30, 20, 50, 5]
        )

        result = operation.commit(heap)

        assert result is None
        assert heap.peek() == 50
        assert heap.size == 6

    def test_commit_replaces_existing_values(self):
        heap = Heap[int](HeapType.MIN)

        heap.insert(100)

        operation = BuildHeapOperation(
            [30, 10, 20]
        )

        operation.commit(heap)

        assert heap.values == [10, 30, 20]

    def test_operation_copies_input_values(self):
        values = [30, 10, 20]
        operation = BuildHeapOperation(values)

        values.append(100)

        heap = Heap[int](HeapType.MIN)
        operation.commit(heap)

        assert heap.size == 3
        assert heap.values == [10, 30, 20]


class TestClearOperation:
    def test_commit_clears_heap(self):
        heap = Heap[int](HeapType.MIN)

        heap.build_heap(
            [10, 20, 30, 40]
        )

        operation = ClearOperation()

        result = operation.commit(heap)

        assert result is None
        assert heap.is_empty
        assert heap.values == []

    def test_commit_on_empty_heap(self):
        heap = Heap[int](HeapType.MIN)
        operation = ClearOperation()

        result = operation.commit(heap)

        assert result is None
        assert heap.is_empty