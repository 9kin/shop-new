from tables import Base, Ladder
import re


class Ladder:
    id = "6.2"
    table = Ladder()
    text = """- Надежная металлическая конструкция.
- Удобные широкие ступени.
- Страховочная лента (в моделях СМ5, СМ6, СМ7, СМ8).
- Высокая эргономичная дуга безопасности со встроенным лотком для инвентаря и отделением для инструментов.
- Рифленая поверхность рабочей площадки, для предотвращения скольжения.
- Ступени шириной 65 мм обеспечивают удобство и безопасность подъема и спуска.

Cтремянка предназначена для бытового использования.


Материалы: сталь (ступени), сталь (профиль), пластмасса (PELD)."""


class ConnectionMixer:
    id = "1.2.*"
    table = Base()
    text = ""


class PPR:
    id = "1.3.1"
    table = Base()
    text = ""


class Route:
    cl = [Ladder, ConnectionMixer, PPR]
    route_map = {}
    for i in cl:
        route_map[i.id] = i

    def routing(self, key):
        for pattern in self.route_map:
            if re.fullmatch(pattern, key):
                return self.route_map[pattern]
        return None
