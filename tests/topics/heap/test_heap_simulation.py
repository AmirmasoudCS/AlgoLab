from algolab.simulation.events import SimulationEvent
from algolab.topics.heap.model import Heap, HeapType
from algolab.topics.heap.operations import (
    BuildHeapOperation,
    ClearOperation,
    ExtractOperation,
    InsertOperation,
    PeekOperation,
)
from algolab.topics.heap.simulation import (
    CompareHeapElementsEvent,
    CompleteHeapOperationEvent,
    CreateHeapElementEvent,
    ExtractHeapElementEvent,
    HeapSimulation,
    HeapSimulationState,
    HeapSimulator,
    MoveLastElementEvent,
    SwapHeapElementsEvent,
)


class TestHeapSimulationState:
    def test_state_contains_expected_values(self):
        state = HeapSimulationState(
            values=(10, 20, 30),
            description="Test state.",
        )

        assert state.values == (10, 20, 30)
        assert state.description == "Test state."
        assert state.current_index is None
        assert state.compared_indices is None
        assert state.swapped_indices is None


class TestHeapSimulation:
    def test_commit_insert(self):
        heap = Heap[int](HeapType.MIN)
        simulation = HeapSimulator(heap).insert(10)

        result = simulation.commit(heap)

        assert result is None
        assert heap.values == [10]

    def test_commit_extract(self):
        heap = Heap[int](HeapType.MIN)
        heap.build_heap([30, 10, 20])

        simulation = HeapSimulator(heap).extract()

        result = simulation.commit(heap)

        assert result == 10
        assert heap.peek() == 20

    def test_commit_peek(self):
        heap = Heap[int](HeapType.MIN)
        heap.build_heap([30, 10, 20])

        simulation = HeapSimulator(heap).peek()

        result = simulation.commit(heap)

        assert result == 10
        assert heap.values == [10, 30, 20]

    def test_commit_build_heap(self):
        heap = Heap[int](HeapType.MIN)
        simulator = HeapSimulator(heap)

        simulation = simulator.build_heap(
            [30, 10, 20]
        )

        result = simulation.commit(heap)

        assert result is None
        assert heap.peek() == 10

    def test_commit_clear(self):
        heap = Heap[int](HeapType.MIN)
        heap.build_heap([10, 20, 30])

        simulation = HeapSimulator(heap).clear()

        result = simulation.commit(heap)

        assert result is None
        assert heap.is_empty


class TestHeapSimulatorInsert:
    def test_insert_creates_initial_state(self):
        heap = Heap[int](HeapType.MIN)
        heap.insert(10)

        simulation = HeapSimulator(heap).insert(5)

        state = simulation.states[0]

        assert state.step == 0
        assert state.data.values == (10,)
        assert state.data.description == (
            "Initial state of the heap."
        )
        assert state.events == []

    def test_insert_creates_new_element(self):
        heap = Heap[int](HeapType.MIN)
        heap.insert(10)

        simulation = HeapSimulator(heap).insert(5)

        state = simulation.states[1]

        assert state.data.values == (10,)
        assert state.data.current_index == 1
        assert state.data.created_value == 5

        assert state.events == [
            CreateHeapElementEvent(
                index=1,
                value=5,
            )
        ]

    def test_insert_adds_value_to_end_before_bubbling_up(self):
        heap = Heap[int](HeapType.MIN)
        heap.insert(10)

        simulation = HeapSimulator(heap).insert(5)

        state = simulation.states[2]

        assert state.data.values == (10, 5)
        assert state.data.current_index == 1

    def test_insert_compares_child_with_parent(self):
        heap = Heap[int](HeapType.MIN)
        heap.insert(10)

        simulation = HeapSimulator(heap).insert(5)

        comparison_states = [
            state
            for state in simulation.states
            if any(
                isinstance(
                    event,
                    CompareHeapElementsEvent,
                )
                for event in state.events
            )
        ]

        assert len(comparison_states) == 1

        state = comparison_states[0]

        assert state.data.compared_indices == (1, 0)
        assert state.events == [
            CompareHeapElementsEvent(
                first_index=1,
                second_index=0,
            )
        ]

    def test_insert_swaps_when_child_has_priority(self):
        heap = Heap[int](HeapType.MIN)
        heap.insert(10)

        simulation = HeapSimulator(heap).insert(5)

        swap_states = [
            state
            for state in simulation.states
            if any(
                isinstance(
                    event,
                    SwapHeapElementsEvent,
                )
                for event in state.events
            )
        ]

        assert len(swap_states) == 1

        state = swap_states[0]

        assert state.data.values == (10, 5)
        assert state.data.swapped_indices == (1, 0)

    def test_insert_does_not_modify_model(self):
        heap = Heap[int](HeapType.MIN)
        heap.build_heap([10, 20])

        simulator = HeapSimulator(heap)

        simulation = simulator.insert(5)

        assert heap.values == [10, 20]
        assert simulation.states[-1].data.values == (
            5,
            20,
            10,
        )

    def test_insert_completes(self):
        heap = Heap[int](HeapType.MIN)

        simulation = HeapSimulator(heap).insert(10)

        final_state = simulation.states[-1]

        assert final_state.events == [
            CompleteHeapOperationEvent(
                operation="insert",
            )
        ]
        assert final_state.data.values == (10,)


class TestHeapSimulatorPeek:
    def test_peek_empty_heap(self):
        heap = Heap[int](HeapType.MIN)

        simulation = HeapSimulator(heap).peek()

        assert len(simulation.states) == 2

        final_state = simulation.states[-1]

        assert final_state.data.values == ()
        assert final_state.events == [
            CompleteHeapOperationEvent(
                operation="peek_empty",
            )
        ]

    def test_peek_non_empty_heap(self):
        heap = Heap[int](HeapType.MIN)
        heap.build_heap([30, 10, 20])

        simulation = HeapSimulator(heap).peek()

        assert simulation.states[-1].data.values == (
            10,
            30,
            20,
        )

        assert simulation.states[-1].events == [
            CompleteHeapOperationEvent(
                operation="peek",
            )
        ]

    def test_peek_does_not_modify_model(self):
        heap = Heap[int](HeapType.MIN)
        heap.build_heap([30, 10, 20])

        original_values = heap.values

        simulation = HeapSimulator(heap).peek()

        assert heap.values == original_values
        assert simulation.states[-1].data.values == tuple(
            original_values
        )


class TestHeapSimulatorExtract:
    def test_extract_empty_heap(self):
        heap = Heap[int](HeapType.MIN)

        simulation = HeapSimulator(heap).extract()

        assert len(simulation.states) == 2

        final_state = simulation.states[-1]

        assert final_state.data.values == ()
        assert final_state.events == [
            CompleteHeapOperationEvent(
                operation="extract_empty",
            )
        ]

    def test_extract_identifies_root(self):
        heap = Heap[int](HeapType.MIN)
        heap.build_heap([30, 10, 20])

        simulation = HeapSimulator(heap).extract()

        extraction_states = [
            state
            for state in simulation.states
            if any(
                isinstance(
                    event,
                    ExtractHeapElementEvent,
                )
                for event in state.events
            )
        ]

        assert len(extraction_states) == 1

        state = extraction_states[0]

        assert state.data.extracted_value == 10
        assert state.events == [
            ExtractHeapElementEvent(
                index=0,
                value=10,
            )
        ]

    def test_extract_moves_last_element_to_root(self):
        heap = Heap[int](HeapType.MIN)
        heap.build_heap([30, 10, 20])

        simulation = HeapSimulator(heap).extract()

        move_states = [
            state
            for state in simulation.states
            if any(
                isinstance(
                    event,
                    MoveLastElementEvent,
                )
                for event in state.events
            )
        ]

        assert len(move_states) == 1

        state = move_states[0]

        assert state.events == [
            MoveLastElementEvent(
                from_index=2,
                to_index=0,
            )
        ]

    def test_extract_bubbles_down(self):
        heap = Heap[int](HeapType.MIN)
        heap.build_heap(
            [50, 20, 40, 10, 30, 5, 15]
        )

        simulation = HeapSimulator(heap).extract()

        comparison_states = [
            state
            for state in simulation.states
            if any(
                isinstance(
                    event,
                    CompareHeapElementsEvent,
                )
                for event in state.events
            )
        ]

        assert comparison_states

        swap_states = [
            state
            for state in simulation.states
            if any(
                isinstance(
                    event,
                    SwapHeapElementsEvent,
                )
                for event in state.events
            )
        ]

        assert swap_states

    def test_extract_single_element(self):
        heap = Heap[int](HeapType.MIN)
        heap.insert(10)

        simulation = HeapSimulator(heap).extract()

        assert simulation.states[-1].data.values == ()

        assert simulation.states[-1].events == [
            CompleteHeapOperationEvent(
                operation="extract",
            )
        ]

    def test_extract_does_not_modify_model(self):
        heap = Heap[int](HeapType.MIN)
        heap.build_heap(
            [30, 10, 20]
        )

        original_values = heap.values

        simulation = HeapSimulator(heap).extract()

        assert heap.values == original_values
        assert simulation.states[-1].data.values == (
            20,
            30,
        )

    def test_extract_completes(self):
        heap = Heap[int](HeapType.MIN)
        heap.build_heap([30, 10, 20])

        simulation = HeapSimulator(heap).extract()

        final_state = simulation.states[-1]

        assert final_state.events == [
            CompleteHeapOperationEvent(
                operation="extract",
            )
        ]


class TestHeapSimulatorBuildHeap:
    def test_build_heap_starts_with_empty_heap(self):
        heap = Heap[int](HeapType.MIN)

        simulation = HeapSimulator(heap).build_heap(
            [40, 10, 30]
        )

        assert simulation.states[0].data.values == ()

    def test_build_heap_places_input_values_in_array(self):
        heap = Heap[int](HeapType.MIN)

        simulation = HeapSimulator(heap).build_heap(
            [40, 10, 30]
        )

        assert simulation.states[1].data.values == (
            40,
            10,
            30,
        )

    def test_build_heap_generates_comparison_events(self):
        heap = Heap[int](HeapType.MIN)

        simulation = HeapSimulator(heap).build_heap(
            [40, 10, 30, 20, 50, 5]
        )

        comparison_states = [
            state
            for state in simulation.states
            if any(
                isinstance(
                    event,
                    CompareHeapElementsEvent,
                )
                for event in state.events
            )
        ]

        assert comparison_states

    def test_build_heap_generates_swap_events(self):
        heap = Heap[int](HeapType.MIN)

        simulation = HeapSimulator(heap).build_heap(
            [40, 10, 30, 20, 50, 5]
        )

        swap_states = [
            state
            for state in simulation.states
            if any(
                isinstance(
                    event,
                    SwapHeapElementsEvent,
                )
                for event in state.events
            )
        ]

        assert swap_states

    def test_build_heap_final_state_is_valid_min_heap(self):
        heap = Heap[int](HeapType.MIN)

        simulation = HeapSimulator(heap).build_heap(
            [40, 10, 30, 20, 50, 5]
        )

        values = simulation.states[-1].data.values

        for index, value in enumerate(values):
            left_index = 2 * index + 1
            right_index = 2 * index + 2

            if left_index < len(values):
                assert value <= values[left_index]

            if right_index < len(values):
                assert value <= values[right_index]

    def test_build_heap_final_state_is_valid_max_heap(self):
        heap = Heap[int](HeapType.MAX)

        simulation = HeapSimulator(heap).build_heap(
            [40, 10, 30, 20, 50, 5]
        )

        values = simulation.states[-1].data.values

        for index, value in enumerate(values):
            left_index = 2 * index + 1
            right_index = 2 * index + 2

            if left_index < len(values):
                assert value >= values[left_index]

            if right_index < len(values):
                assert value >= values[right_index]

    def test_build_heap_does_not_modify_model(self):
        heap = Heap[int](HeapType.MIN)

        original_values = heap.values

        simulation = HeapSimulator(heap).build_heap(
            [40, 10, 30]
        )

        assert heap.values == original_values
        assert simulation.states[-1].data.values != ()


class TestHeapSimulatorClear:
    def test_clear_creates_empty_final_state(self):
        heap = Heap[int](HeapType.MIN)
        heap.build_heap([10, 20, 30])

        simulation = HeapSimulator(heap).clear()

        assert simulation.states[-1].data.values == ()

    def test_clear_completes(self):
        heap = Heap[int](HeapType.MIN)
        heap.build_heap([10, 20, 30])

        simulation = HeapSimulator(heap).clear()

        assert simulation.states[-1].events == [
            CompleteHeapOperationEvent(
                operation="clear",
            )
        ]

    def test_clear_does_not_modify_model(self):
        heap = Heap[int](HeapType.MIN)
        heap.build_heap([10, 20, 30])

        simulation = HeapSimulator(heap).clear()

        assert heap.values == [10, 20, 30]
        assert simulation.states[-1].data.values == ()