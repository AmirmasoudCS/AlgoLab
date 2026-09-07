from algolab.visualization.graph.coordinate_system import (
    GraphCoordinateSystem,
)


graph = GraphCoordinateSystem(
    x=100,
    y=100,
    width=800,
    height=500,
    x_min=0,
    x_max=10,
    y_min=0,
    y_max=100,
)

print(graph.to_screen(0, 0))
print(graph.to_screen(10, 100))
print(graph.to_screen(5, 50))