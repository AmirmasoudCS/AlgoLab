import copy
import math

import pytest

from algolab.topics.graph.model import GraphModel


def _graph(directed=False, weighted=False):
    graph = GraphModel(directed, weighted)
    ids = [graph.add_node(label) for label in "ABCDE"]
    graph.recompute_layout(640, 500, 200)

    graph.add_edge(ids[0], ids[1], 4)
    graph.add_edge(ids[1], ids[2], 2.5)
    graph.add_edge(ids[2], ids[3], 7)
    graph.add_edge(ids[3], ids[0], 1)
    graph.move_node(ids[4], 333.0, 444.0)             # pinned by "dragging"
    graph.remove_node(ids[1])                         # leaves an id gap

    return graph


def _same(a: GraphModel, b: GraphModel) -> None:
    assert a.to_dict() == b.to_dict()
    assert a.adjacency() == b.adjacency()


@pytest.mark.parametrize("directed", [False, True])
@pytest.mark.parametrize("weighted", [False, True])
def test_round_trip_preserves_everything(directed, weighted):
    original = _graph(directed, weighted)
    restored = GraphModel.from_dict(original.to_dict())

    assert restored.directed is directed and restored.weighted is weighted
    _same(original, restored)
    assert [(n.node_id, n.label, n.x, n.y, n.pinned) for n in restored.nodes] == \
           [(n.node_id, n.label, n.x, n.y, n.pinned) for n in original.nodes]
    assert [(e.source, e.target, e.weight) for e in restored.edges] == \
           [(e.source, e.target, e.weight) for e in original.edges]


def test_ids_are_never_reused_after_loading():
    original = _graph()
    assert max(n.node_id for n in original.nodes) == 4 and original.to_dict()["next_node_id"] == 5

    restored = GraphModel.from_dict(original.to_dict())

    assert restored.add_node("Z") == 5


def test_pinned_flags_and_positions_survive():
    restored = GraphModel.from_dict(_graph().to_dict())
    pinned = [n for n in restored.nodes if n.pinned]

    assert [(n.x, n.y) for n in pinned] == [(333.0, 444.0)]


def test_weights_are_kept_even_while_unweighted():
    graph = _graph(weighted=True)
    graph.set_weighted(False)

    restored = GraphModel.from_dict(graph.to_dict())
    restored.set_weighted(True)

    assert sorted(e.weight for e in restored.edges) == sorted(e.weight for e in graph.edges)


def test_empty_graph_round_trips_with_its_settings():
    restored = GraphModel.from_dict(GraphModel(True, True).to_dict())

    assert restored.is_empty and restored.directed and restored.weighted


def test_a_directed_graph_may_have_edges_in_both_directions():
    graph = GraphModel(directed=True)
    a, b = graph.add_node("A"), graph.add_node("B")
    graph.add_edge(a, b)
    graph.add_edge(b, a)

    assert len(GraphModel.from_dict(graph.to_dict()).edges) == 2


def test_a_loaded_graph_keeps_behaving_correctly():
    restored = GraphModel.from_dict(_graph().to_dict())
    new_id = restored.add_node("N")
    restored.add_edge(new_id, restored.nodes[0].node_id, 3)
    restored.remove_node(restored.nodes[0].node_id)

    assert restored.get_node(new_id) is not None


# ---------------------------------------------------------------- invalid data

def _data():
    return _graph(weighted=True).to_dict()


def _with(**changes):
    return {**_data(), **changes}


def _edit_node(**changes):
    data = _data()
    data["nodes"][0].update(changes)
    return data


def _edit_edge(**changes):
    data = _data()
    data["edges"][0].update(changes)
    return data


@pytest.mark.parametrize("bad", [
    None, [], "graph", {},
    _with(directed="yes"), _with(weighted=1), _with(directed=None),
    _with(nodes="abc"), _with(edges="abc"), _with(nodes=[1]), _with(edges=[1]),
    _with(next_node_id=0), _with(next_node_id=-1), _with(next_node_id=True), _with(next_node_id=10**10),
    _edit_node(id=-1), _edit_node(id="a"), _edit_node(id=True),
    _edit_node(label=""), _edit_node(label=5), _edit_node(label="x" * 13), _edit_node(label="a\nb"),
    _edit_node(x=math.nan), _edit_node(y=math.inf), _edit_node(x="1"), _edit_node(x=10**7),
    _edit_node(pinned="no"),
    _edit_edge(source=999), _edit_edge(target=999),
    _edit_edge(weight="heavy"), _edit_edge(weight=True), _edit_edge(weight=math.nan),
])
def test_from_dict_rejects_malformed_data(bad):
    with pytest.raises(ValueError):
        GraphModel.from_dict(bad)


def test_from_dict_rejects_missing_fields():
    for field in ("directed", "weighted", "next_node_id", "nodes", "edges"):
        data = _data()
        del data[field]

        with pytest.raises(ValueError):
            GraphModel.from_dict(data)


def test_from_dict_rejects_duplicate_node_ids():
    data = _data()
    data["nodes"].append(copy.deepcopy(data["nodes"][0]))

    with pytest.raises(ValueError, match="twice"):
        GraphModel.from_dict(data)


def test_from_dict_rejects_self_loops():
    data = _data()
    node = data["nodes"][0]["id"]
    data["edges"].append({"source": node, "target": node, "weight": 1})

    with pytest.raises(ValueError, match="self-loop"):
        GraphModel.from_dict(data)


def test_from_dict_rejects_duplicate_edges():
    data = _data()
    data["edges"].append(copy.deepcopy(data["edges"][0]))

    with pytest.raises(ValueError, match="duplicates"):
        GraphModel.from_dict(data)


def test_a_reversed_edge_is_a_duplicate_only_when_undirected():
    undirected = _data()
    undirected["edges"].append({
        "source": undirected["edges"][0]["target"],
        "target": undirected["edges"][0]["source"], "weight": 1,
    })

    with pytest.raises(ValueError, match="duplicates"):
        GraphModel.from_dict(undirected)

    directed = copy.deepcopy(undirected)
    directed["directed"] = True

    assert len(GraphModel.from_dict(directed).edges) == len(undirected["edges"])


def test_from_dict_rejects_oversized_graphs():
    many = GraphModel()
    for _ in range(GraphModel.MAX_LOADED_NODES):
        many.add_node("N")

    assert len(GraphModel.from_dict(many.to_dict()).nodes) == GraphModel.MAX_LOADED_NODES

    data = many.to_dict()
    data["nodes"].append({"id": 10**6, "label": "X", "x": 0, "y": 0, "pinned": False})

    with pytest.raises(ValueError, match="at most"):
        GraphModel.from_dict(data)

    data = _data()
    data["edges"] = [{"source": 0, "target": 2, "weight": 1}] * (GraphModel.MAX_LOADED_EDGES + 1)

    with pytest.raises(ValueError, match="at most"):
        GraphModel.from_dict(data)


def test_replace_with_takes_over_everything():
    target = GraphModel()
    target.add_node("Q")
    source = _graph(True, True)
    expected = source.to_dict()

    target.replace_with(source)

    assert target.to_dict() == expected and target.directed and target.weighted