from actor import *
from proto.morai.actor.actor_enum_pb2 import ANIMATION_OBJECT_TYPE_CROSSING_GATE
from proto.morai.actor.actor_set_pb2 import AnimationParam, TrainSignalLightInfo
from proto.morai.common.enum_pb2 import OBJECT_TYPE_OBSTACLE

class Obstacle(Actor):
    def __init__(self, sim_adapter, client_key, actor_id) -> None:
        super().__init__(sim_adapter, client_key, actor_id)
        self._object_type = OBJECT_TYPE_OBSTACLE   


    def set_obstacle_animation(self, enabled, key='Play'):
        param = AnimationParam()
        param.actor_info.CopyFrom(self.get_object_info())
        param.enabled = enabled
        param.object_type = ANIMATION_OBJECT_TYPE_CROSSING_GATE
        param.animation_key = key
        result = self._sim_adapter.set_obstacle_animation(param)

        return result.status == STATUS_CODE_SUCCESS


    def set_train_signal_light(self, tl_color):
        param = TrainSignalLightInfo()
        param.actor_info.CopyFrom(self.get_object_info())
        param.color = tl_color
        result = self._sim_adapter.set_train_signal_light(param)

        return result.status == STATUS_CODE_SUCCESS

