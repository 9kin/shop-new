import tabels.all as tabels
import re

class Ladder:
    id = "6.2"
    tabel_cls = tabels.ladder_cls
    tabel = tabels.ladder
    text = """- Надежная металлическая конструкция.
- Удобные широкие ступени.
- Страховочная лента (в моделях СМ5, СМ6, СМ7, СМ8).
- Высокая эргономичная дуга безопасности со встроенным лотком для инвентаря и отделением для инструментов.
- Рифленая поверхность рабочей площадки, для предотвращения скольжения.
- Ступени шириной 65 мм обеспечивают удобство и безопасность подъема и спуска.

Cтремянка предназначена для бытового испо- льзования.


Материалы: сталь (ступени), сталь (профиль), пластмасса (PELD)."""


class ConnectionMixer:
    id = "1.2.*"
    tabel_cls = tabels.connection_cls
    tabel = tabels.connection
    text = ''


class Route:
    cl = [Ladder, ConnectionMixer]
    route_map = {}
    for i in cl:
        route_map[i.id] = i

    def routing(self, key):
        for pattern in self.route_map:
            if re.fullmatch(pattern, key):
                 return self.route_map[pattern]
        return None

