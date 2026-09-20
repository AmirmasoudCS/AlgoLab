from __future__ import annotations

from dataclasses import dataclass

from algolab.simulation.events import SimulationEvent
from algolab.simulation.state import SimulationState
from algolab.topics.sorting.model import SortArray
from algolab.topics.sorting.operations import ApplySortOperation, SortOperation


@dataclass(frozen=True)
class CompareEvent(SimulationEvent):
    """Indicates two elements are being compared."""

    first_index: int
    second_index: int


@dataclass(frozen=True)
class SwapEvent(SimulationEvent):
    """Indicates two elements are being swapped or one is overwriting another."""

    first_index: int
    second_index: int


@dataclass(frozen=True)
class MarkSortedEvent(SimulationEvent):
    """Indicates an element has reached its final sorted position."""

    index: int


@dataclass(frozen=True)
class CompleteSortEvent(SimulationEvent):
    """Indicates the sort has finished."""

    algorithm: str


@dataclass(frozen=True)
class SortState:
    """
    Represents the visual state of a sorting algorithm at one step.

    Shared across all six algorithms for the same reason
    GraphAlgorithmState is shared across graph algorithms: the screen
    only needs "what does the array look like right now, what's being
    compared, what's being swapped, what's already sorted" regardless
    of which algorithm produced it. Fields that don't apply to a given
    algorithm (pivot_index for anything but quicksort, active_range
    for anything but merge/quick sort) are simply left at their
    default.
    """

    description: str

    values: tuple[int, ...]
    comparing: tuple[int, ...] = ()
    swapping: tuple[int, ...] = ()
    sorted_indices: frozenset[int] = frozenset()
    pivot_index: int | None = None
    active_range: tuple[int, int] | None = None


@dataclass(frozen=True)
class SortSimulation:
    """Represents a complete sorting run."""

    states: tuple[SimulationState, ...]
    operation: SortOperation

    def commit(self, array: SortArray) -> None:
        """Commit the simulated sort to the real array."""
        self.operation.commit(array)


class BubbleSortSimulator:
    """Creates a step-by-step simulation of bubble sort."""

    def run(self, values: list[int]) -> SortSimulation:
        arr = list(values)
        states: list[SimulationState] = []
        n = len(arr)
        sorted_indices: set[int] = set()

        def add_state(events, description, comparing=(), swapping=(), pivot_index=None):
            states.append(
                SimulationState(
                    data=SortState(
                        description=description,
                        values=tuple(arr),
                        comparing=tuple(comparing),
                        swapping=tuple(swapping),
                        sorted_indices=frozenset(sorted_indices),
                        pivot_index=pivot_index,
                    ),
                    events=events,
                    step=len(states),
                )
            )

        add_state([], "Initial array.")

        if n == 0:
            add_state([CompleteSortEvent("bubble")], "The array is empty. Nothing to sort.")
            return SortSimulation(tuple(states), ApplySortOperation(arr))

        for i in range(n):
            swapped_any = False

            for j in range(0, n - i - 1):
                add_state(
                    [CompareEvent(j, j + 1)],
                    f"Compare {arr[j]} and {arr[j + 1]}.",
                    comparing=(j, j + 1),
                )

                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped_any = True

                    add_state(
                        [SwapEvent(j, j + 1)],
                        f"{arr[j + 1]} and {arr[j]} were out of order. Swap them.",
                        swapping=(j, j + 1),
                    )

            sorted_indices.add(n - i - 1)

            add_state(
                [MarkSortedEvent(n - i - 1)],
                f"{arr[n - i - 1]} is now in its final position.",
            )

            if not swapped_any:
                sorted_indices.update(range(n))
                add_state(
                    [],
                    "No swaps happened in that pass, so the array is already sorted.",
                )
                break

        sorted_indices.update(range(n))

        add_state([CompleteSortEvent("bubble")], "Bubble sort is complete.")

        return SortSimulation(tuple(states), ApplySortOperation(arr))


class SelectionSortSimulator:
    """Creates a step-by-step simulation of selection sort."""

    def run(self, values: list[int]) -> SortSimulation:
        arr = list(values)
        states: list[SimulationState] = []
        n = len(arr)
        sorted_indices: set[int] = set()

        def add_state(events, description, comparing=(), swapping=()):
            states.append(
                SimulationState(
                    data=SortState(
                        description=description,
                        values=tuple(arr),
                        comparing=tuple(comparing),
                        swapping=tuple(swapping),
                        sorted_indices=frozenset(sorted_indices),
                    ),
                    events=events,
                    step=len(states),
                )
            )

        add_state([], "Initial array.")

        if n == 0:
            add_state([CompleteSortEvent("selection")], "The array is empty. Nothing to sort.")
            return SortSimulation(tuple(states), ApplySortOperation(arr))

        for i in range(n):
            min_index = i

            add_state(
                [],
                f"Find the smallest value in the unsorted portion starting at index {i}.",
                comparing=(i,),
            )

            for j in range(i + 1, n):
                add_state(
                    [CompareEvent(min_index, j)],
                    f"Compare the current minimum {arr[min_index]} with {arr[j]}.",
                    comparing=(min_index, j),
                )

                if arr[j] < arr[min_index]:
                    min_index = j

                    add_state(
                        [],
                        f"New minimum found: {arr[min_index]} at index {min_index}.",
                        comparing=(min_index,),
                    )

            if min_index != i:
                arr[i], arr[min_index] = arr[min_index], arr[i]

                add_state(
                    [SwapEvent(i, min_index)],
                    f"Swap {arr[min_index]} and {arr[i]} to place the minimum at index {i}.",
                    swapping=(i, min_index),
                )

            sorted_indices.add(i)

            add_state(
                [MarkSortedEvent(i)],
                f"{arr[i]} is now in its final position.",
            )

        add_state([CompleteSortEvent("selection")], "Selection sort is complete.")

        return SortSimulation(tuple(states), ApplySortOperation(arr))


class InsertionSortSimulator:
    """Creates a step-by-step simulation of insertion sort."""

    def run(self, values: list[int]) -> SortSimulation:
        arr = list(values)
        states: list[SimulationState] = []
        n = len(arr)

        def add_state(events, description, comparing=(), swapping=(), sorted_upto=0):
            states.append(
                SimulationState(
                    data=SortState(
                        description=description,
                        values=tuple(arr),
                        comparing=tuple(comparing),
                        swapping=tuple(swapping),
                        sorted_indices=frozenset(range(sorted_upto)),
                    ),
                    events=events,
                    step=len(states),
                )
            )

        add_state([], "Initial array.")

        if n == 0:
            add_state([CompleteSortEvent("insertion")], "The array is empty. Nothing to sort.")
            return SortSimulation(tuple(states), ApplySortOperation(arr))

        add_state([], "The first element is trivially sorted on its own.", sorted_upto=1)

        for i in range(1, n):
            key = arr[i]
            j = i - 1

            add_state(
                [],
                f"Take {key} and find where it belongs in the sorted portion.",
                comparing=(i,),
                sorted_upto=i,
            )

            while j >= 0 and arr[j] > key:
                add_state(
                    [CompareEvent(j, j + 1)],
                    f"{arr[j]} is greater than {key}, shift it one position right.",
                    comparing=(j, j + 1),
                    sorted_upto=i,
                )

                arr[j + 1] = arr[j]
                j -= 1

                add_state(
                    [SwapEvent(j + 1, j + 2)],
                    "Shift complete.",
                    swapping=(j + 1, j + 2),
                    sorted_upto=i,
                )

            arr[j + 1] = key

            add_state(
                [],
                f"Place {key} at index {j + 1}.",
                swapping=(j + 1,),
                sorted_upto=i + 1,
            )

        add_state(
            [CompleteSortEvent("insertion")],
            "Insertion sort is complete.",
            sorted_upto=n,
        )

        return SortSimulation(tuple(states), ApplySortOperation(arr))


class MergeSortSimulator:
    """Creates a step-by-step simulation of merge sort."""

    def run(self, values: list[int]) -> SortSimulation:
        arr = list(values)
        states: list[SimulationState] = []
        n = len(arr)

        def add_state(events, description, comparing=(), swapping=(), active_range=None):
            states.append(
                SimulationState(
                    data=SortState(
                        description=description,
                        values=tuple(arr),
                        comparing=tuple(comparing),
                        swapping=tuple(swapping),
                        active_range=active_range,
                    ),
                    events=events,
                    step=len(states),
                )
            )

        add_state([], "Initial array.")

        if n == 0:
            add_state([CompleteSortEvent("merge")], "The array is empty. Nothing to sort.")
            return SortSimulation(tuple(states), ApplySortOperation(arr))

        def merge(low: int, mid: int, high: int) -> None:
            left = arr[low:mid]
            right = arr[mid:high]

            add_state(
                [],
                f"Merge the sorted halves [{low}, {mid}) and [{mid}, {high}).",
                active_range=(low, high),
            )

            i = j = 0
            k = low

            while i < len(left) and j < len(right):
                add_state(
                    [CompareEvent(low + i, mid + j)],
                    f"Compare {left[i]} and {right[j]}.",
                    comparing=(low + i, mid + j),
                    active_range=(low, high),
                )

                if left[i] <= right[j]:
                    arr[k] = left[i]
                    i += 1
                else:
                    arr[k] = right[j]
                    j += 1

                add_state(
                    [SwapEvent(k, k)],
                    f"Place {arr[k]} at index {k}.",
                    swapping=(k,),
                    active_range=(low, high),
                )

                k += 1

            while i < len(left):
                arr[k] = left[i]

                add_state(
                    [SwapEvent(k, k)],
                    f"Copy the remaining {arr[k]} from the left half.",
                    swapping=(k,),
                    active_range=(low, high),
                )

                i += 1
                k += 1

            while j < len(right):
                arr[k] = right[j]

                add_state(
                    [SwapEvent(k, k)],
                    f"Copy the remaining {arr[k]} from the right half.",
                    swapping=(k,),
                    active_range=(low, high),
                )

                j += 1
                k += 1

        def merge_sort(low: int, high: int) -> None:
            if high - low <= 1:
                return

            mid = (low + high) // 2

            add_state(
                [],
                f"Split [{low}, {high}) into [{low}, {mid}) and [{mid}, {high}).",
                active_range=(low, high),
            )

            merge_sort(low, mid)
            merge_sort(mid, high)
            merge(low, mid, high)

        merge_sort(0, n)

        add_state(
            [CompleteSortEvent("merge")],
            "Merge sort is complete.",
        )

        # Override the final state's sorted_indices, since merge sort
        # doesn't build up a sorted region incrementally the way the
        # comparison sorts do; everything is only fully sorted at the
        # very end, once the top-level merge finishes.
        final_state = states[-1]
        states[-1] = SimulationState(
            data=SortState(
                description=final_state.data.description,
                values=final_state.data.values,
                sorted_indices=frozenset(range(n)),
            ),
            events=final_state.events,
            step=final_state.step,
        )

        return SortSimulation(tuple(states), ApplySortOperation(arr))


class QuickSortSimulator:
    """Creates a step-by-step simulation of quicksort (Lomuto partition)."""

    def run(self, values: list[int]) -> SortSimulation:
        arr = list(values)
        states: list[SimulationState] = []
        n = len(arr)
        sorted_indices: set[int] = set()

        def add_state(events, description, comparing=(), swapping=(), pivot_index=None, active_range=None):
            states.append(
                SimulationState(
                    data=SortState(
                        description=description,
                        values=tuple(arr),
                        comparing=tuple(comparing),
                        swapping=tuple(swapping),
                        sorted_indices=frozenset(sorted_indices),
                        pivot_index=pivot_index,
                        active_range=active_range,
                    ),
                    events=events,
                    step=len(states),
                )
            )

        add_state([], "Initial array.")

        if n == 0:
            add_state([CompleteSortEvent("quick")], "The array is empty. Nothing to sort.")
            return SortSimulation(tuple(states), ApplySortOperation(arr))

        def partition(low: int, high: int) -> int:
            pivot = arr[high]

            add_state(
                [],
                f"Choose {pivot} (the last element) as the pivot.",
                pivot_index=high,
                active_range=(low, high + 1),
            )

            i = low - 1

            for j in range(low, high):
                add_state(
                    [CompareEvent(j, high)],
                    f"Compare {arr[j]} with the pivot {pivot}.",
                    comparing=(j, high),
                    pivot_index=high,
                    active_range=(low, high + 1),
                )

                if arr[j] < pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]

                    add_state(
                        [SwapEvent(i, j)],
                        f"{arr[j]} is less than the pivot. Swap {arr[i]} and {arr[j]}.",
                        swapping=(i, j),
                        pivot_index=high,
                        active_range=(low, high + 1),
                    )

            arr[i + 1], arr[high] = arr[high], arr[i + 1]

            add_state(
                [SwapEvent(i + 1, high)],
                f"Place the pivot {arr[i + 1]} at index {i + 1}.",
                swapping=(i + 1, high),
                active_range=(low, high + 1),
            )

            return i + 1

        def quicksort(low: int, high: int) -> None:
            if low < high:
                pivot_index = partition(low, high)

                sorted_indices.add(pivot_index)

                add_state(
                    [MarkSortedEvent(pivot_index)],
                    f"{arr[pivot_index]} is now in its final position.",
                )

                quicksort(low, pivot_index - 1)
                quicksort(pivot_index + 1, high)
            elif low == high:
                sorted_indices.add(low)

        quicksort(0, n - 1)

        sorted_indices.update(range(n))

        add_state([CompleteSortEvent("quick")], "Quick sort is complete.")

        return SortSimulation(tuple(states), ApplySortOperation(arr))


class HeapSortSimulator:
    """Creates a step-by-step simulation of heap sort."""

    def run(self, values: list[int]) -> SortSimulation:
        arr = list(values)
        states: list[SimulationState] = []
        n = len(arr)
        sorted_indices: set[int] = set()

        def add_state(events, description, comparing=(), swapping=()):
            states.append(
                SimulationState(
                    data=SortState(
                        description=description,
                        values=tuple(arr),
                        comparing=tuple(comparing),
                        swapping=tuple(swapping),
                        sorted_indices=frozenset(sorted_indices),
                    ),
                    events=events,
                    step=len(states),
                )
            )

        add_state([], "Initial array.")

        if n == 0:
            add_state([CompleteSortEvent("heap")], "The array is empty. Nothing to sort.")
            return SortSimulation(tuple(states), ApplySortOperation(arr))

        def heapify(size: int, root: int) -> None:
            largest = root
            left = 2 * root + 1
            right = 2 * root + 2

            if left < size:
                add_state(
                    [CompareEvent(largest, left)],
                    f"Compare {arr[largest]} with its left child {arr[left]}.",
                    comparing=(largest, left),
                )

                if arr[left] > arr[largest]:
                    largest = left

            if right < size:
                add_state(
                    [CompareEvent(largest, right)],
                    f"Compare {arr[largest]} with its right child {arr[right]}.",
                    comparing=(largest, right),
                )

                if arr[right] > arr[largest]:
                    largest = right

            if largest != root:
                arr[root], arr[largest] = arr[largest], arr[root]

                add_state(
                    [SwapEvent(root, largest)],
                    f"Swap {arr[largest]} and {arr[root]} to restore the heap property.",
                    swapping=(root, largest),
                )

                heapify(size, largest)

        add_state([], "Build a max heap from the array.")

        for i in range(n // 2 - 1, -1, -1):
            heapify(n, i)

        add_state([], "Max heap built. The largest value is now at the root.")

        for end in range(n - 1, 0, -1):
            arr[0], arr[end] = arr[end], arr[0]
            sorted_indices.add(end)

            add_state(
                [SwapEvent(0, end)],
                f"Move the largest remaining value {arr[end]} to its final position.",
                swapping=(0, end),
            )

            heapify(end, 0)

        sorted_indices.add(0)

        add_state([CompleteSortEvent("heap")], "Heap sort is complete.")

        return SortSimulation(tuple(states), ApplySortOperation(arr))