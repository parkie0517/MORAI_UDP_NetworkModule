import os, sys
from proto.morai.actor.actor_enum_pb2 import EGO_CRUISE_TYPE_LINK
from proto.morai.common.type_pb2 import StringValue

from proto.sim_adapter import *

current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '..')))
sys.path.append(os.path.normpath(os.path.join(current_path, '../proto')))


class Scenario() :
    #! @class Scenario
    #! @brief world 또는 map 에 있어야 할 것같은 기능을 일단 Scenario part로 구분지어 놓기 위해 일단 클래스로 만들어놓음.
    def __init__(self, sim_adapter) :
        self._sim_adapter: SimAdapter = sim_adapter

    def create_vehicle_spawn_point(self, vehicle_spawn_param) :
        self._sim_adapter.create_vehicle_spawn_point(vehicle_spawn_param)

    def create_pedestrian_spawn_point(self, pedestrian_spawn_param) :
        self._sim_adapter.create_pedestrian_spawn_point(pedestrian_spawn_param)

    def enable_spawn_point(self, enable_spawn_point_param) :
        self._sim_adapter.enable_spawn_point(enable_spawn_point_param)

    def load_scenario(self, scenario_filename) :        
        param = StringValue()
        param.value = scenario_filename
        self._sim_adapter.load_morai_scenario(param)

    def create_friction_control_area(self, friction_param) :
        self._sim_adapter.create_friction_control_area(friction_param)