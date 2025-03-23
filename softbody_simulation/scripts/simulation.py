import numpy as np
from softbody_simulation.entities import MassPoint, Spring, PolygonObstacle, GameObject


class SimulationScript:
    def __init__(self):
        self.mass_points, self.springs = generate_objects(
            pos=(50, 50),
            size=(3, 3),
            spacing=100,
            mass_point_kwargs={
                "mass": 1,
                "damping": 0.1,
                "velocity": np.array([200, -100]),
            },
            spring_kwargs={"stiffness": 200, "damping": 1},
        )

        self.obstacles = [
            PolygonObstacle(np.array([(0, 600), (0, 600), (800, 560), (800, 600)]))
        ]

    def update(self, delta_time: float) -> None:
        GameObject.set_delta_time(delta_time)

        for spring in self.springs:
            spring.update()
        for mass_point in self.mass_points:
            others = [m for m in self.mass_points if m != mass_point]
            mass_point.update(self.obstacles, others)


def generate_objects(pos, size, spacing, mass_point_kwargs, spring_kwargs):
    mass_points = []
    for j in range(0, size[1] * spacing, spacing):
        for i in range(0, size[0] * spacing, spacing):
            mass_points.append(
                MassPoint(np.array([pos[0] + i, pos[1] + j]), **mass_point_kwargs)
            )
    springs = []
    for y in range(size[1]):
        for x in range(size[0]):
            index = lambda x, y: x + y * size[0]
            if x + 1 < size[0]:
                springs.append(
                    Spring(
                        (mass_points[index(x, y)], mass_points[index(x + 1, y)]),
                        **spring_kwargs
                    )
                )
            if y + 1 < size[1]:
                springs.append(
                    Spring(
                        (mass_points[index(x, y)], mass_points[index(x, y + 1)]),
                        **spring_kwargs
                    )
                )
            if x + 1 < size[0] and y + 1 < size[1]:
                springs.append(
                    Spring(
                        (mass_points[index(x, y)], mass_points[index(x + 1, y + 1)]),
                        **spring_kwargs
                    )
                )
            if x + 1 < size[0] and y + 1 < size[1]:
                springs.append(
                    Spring(
                        (mass_points[index(x + 1, y)], mass_points[index(x, y + 1)]),
                        **spring_kwargs
                    )
                )
    return mass_points, springs
