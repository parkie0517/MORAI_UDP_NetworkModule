import os, sys

current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '..')))
sys.path.append(os.path.normpath(os.path.join(current_path, '../proto')))

from proto.sim_adapter import *
from proto.morai.common.result_pb2 import Result
from proto.morai.common.object_info_pb2 import ObjectInfo
from proto.morai.common.enum_pb2 import OBJECT_TYPE_UNSPECIFIED, STATUS_CODE_SUCCESS
from proto.morai.actor.actor_set_pb2 import ActorScale, EnableActor, SetTransformParam, SetVelocityParam

class Actor:
    def __init__(self, sim_adapter, client_key, actor_id) -> None:
        self._sim_adapter: SimAdapter = sim_adapter
        self._client_key = client_key
        self._actor_id = actor_id
        self._object_type = OBJECT_TYPE_UNSPECIFIED
        self._actor_state = None
        self._simulate_physics = True
        self._destroyed_callback = None
        self._ai_enabled = True


    def get_id(self):
        return self._actor_id        


    def get_actor_state(self):
        return self._sim_adapter.get_actor_state(self.get_object_info())


    def set_scale(self, scale):
        param = ActorScale()
        param.actor_info.CopyFrom(self.get_object_info())
        param.scale.CopyFrom(scale)        
        result = self._sim_adapter.set_scale(param)
        return result.status == STATUS_CODE_SUCCESS


    def set_transform(self, transform):
        param = SetTransformParam()
        param.actor_info.CopyFrom(self.get_object_info())
        param.transform.CopyFrom(transform)
        result = self._sim_adapter.set_transform(param)
        return result.status == STATUS_CODE_SUCCESS
    

    def get_object_info(self):
        object_info = ObjectInfo()
        object_info.id.value = self._actor_id
        object_info.object_type = self._object_type
        object_info.client_key = self._client_key

        return object_info


    def get_option_name(self):
        option_name = ''
        param = self.get_object_info()
        result = self._sim_adapter.get_option_name(param)
        if result is not None:
            option_name = result.value

        return option_name



    def destroy(self):
        #TODO: world에서 관리하는 목록에서 지울 수 있도록 callback 등록 및 호출해야 함
        self._sim_adapter.destroy_actor(self.get_object_info())
            

    def set_pause(self, enabled):
        param = EnableActor()
        param.actor_info.CopyFrom(self.get_object_info())
        param.enable = enabled
        result = self._sim_adapter.set_pause(param)
        return result.status == STATUS_CODE_SUCCESS


    def set_physics(self, enabled):
        param = EnableActor()
        param.actor_info.CopyFrom(self.get_object_info())
        param.enable = enabled
        result = self._sim_adapter.set_physics(param)
        return result.status == STATUS_CODE_SUCCESS


    def set_velocity(self, velocity):
        velocity_param = SetVelocityParam()
        velocity_param.actor_info.CopyFrom(self.get_object_info())
        velocity_param.velocity = velocity
        result = self._sim_adapter.set_velocity(velocity_param)
        return result.status == STATUS_CODE_SUCCESS       
