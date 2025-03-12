from actor import *
from proto.morai.actor.actor_control_pb2 import PedestrianCtrlCmd
from proto.morai.common.enum_pb2 import OBJECT_TYPE_PEDESTRIAN

class Pedestrian(Actor):
    def __init__(self, sim_adapter, client_key, actor_id) -> None:
        super().__init__(sim_adapter, client_key, actor_id)
        self._object_type = OBJECT_TYPE_PEDESTRIAN        


    def control(self, direction, speed):
        command = PedestrianCtrlCmd()
        command.actor_info.CopyFrom(self.get_object_info())
        command.direction.CopyFrom(direction)
        command.speed = speed

        result = self._sim_adapter.control_pedestrian(command)
        return result.status == STATUS_CODE_SUCCESS