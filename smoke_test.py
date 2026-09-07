from algolab.topics.asymptotic.complexity import QUADRATIC
from algolab.topics.asymptotic.model import AsymptoticModel


model = AsymptoticModel()

print(model.selected_complexity.notation)
print(len(model.visible_complexities))

model.select_complexity(QUADRATIC)

print(model.selected_complexity.notation)

model.set_input_range(1, 100)

print(model.minimum_input)
print(model.maximum_input)

model.set_visible(QUADRATIC, False)

print(len(model.visible_complexities))