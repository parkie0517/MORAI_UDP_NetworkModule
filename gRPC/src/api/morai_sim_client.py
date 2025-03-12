import os, sys

from proto.morai.simulator.category_obstacles_pb2 import CategoryObstacles

current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '..')))
sys.path.append(os.path.normpath(os.path.join(current_path, '../proto')))

import time
from proto.sim_adapter import *
from simulation_world import *
from proto.morai.simulation.start_param_pb2 import StartParam

class MoraiSimClient:
    def __init__(self, client_key) -> None:
        self._sim_adapter = SimAdapter()
        self._client_key = client_key

        self._available_maps = []
        self._available_objects = []


    def connect(self, addr, port):
        self._sim_adapter.connect(addr, port)


    def is_connected(self):
        return self._sim_adapter.is_connected()


    def disconnect(self):
        self._sim_adapter.disconnect()


    def finalize(self):
        self._simulation_world.finalize()
        self._simulation_world = None
        self._available_maps.clear()
        self.disconnect()


    def get_simulator_version(self):
        version = self._sim_adapter.get_simulator_version()
        return version.value


    def get_timestamp(self):
        timestamp = self._sim_adapter.get_timestamp()
        return timestamp.value


    def get_available_maps(self):
        if len(self._available_maps) == 0:
            available_maps = self._sim_adapter.get_available_maps()
            for map_name in available_maps.values:
                self._available_maps.append(map_name)

        return self._available_maps


    def get_available_objects(self):        
        if len(self._available_objects) == 0:
            param = CategoryObstacles()
            param.vehicle = True
            param.pedestrian = True
            param.obstacle = True
            param.spawn_point = True
            param.map_object = True

            self._available_objects = self._sim_adapter.get_available_objects()

        return self._available_maps



    def get_simulator_data_path(self):
        data_path = self._sim_adapter.get_simulator_data_path()
        return data_path.value


    def get_simulation_world(self):
        return self._simulation_world


    def set_rendering_mode(self, rendering_mode):
        response = self._sim_adapter.set_rendering_mode(rendering_mode)
        return response.status == STATUS_CODE_SUCCESS

    
    def check_latency(self):
        bef = time.perf_counter()
        self._sim_adapter.check_latency()
        elapsed = time.perf_counter() - bef

        return elapsed / 2
    

    def start_simulation(self, map_and_vehicle=None, ego_transform=None, ego_cruise_setting=None,
                         sync_mode=None, simulation_settings=None, ego_setting=None):
        start_param = StartParam()
        map_name = None
        init_sync_mode = SYNC_MODE_TYPE_UNSPECIFIED
        ego_id = 'Ego'
        ego_label = 'Ego'
        start_param.client_key = self._client_key
        if map_and_vehicle != None:
            start_param.map_and_vehicle.CopyFrom(map_and_vehicle)
            map_name = map_and_vehicle.map_name
        if ego_transform != None:
            start_param.ego_transform.CopyFrom(ego_transform)
        if ego_cruise_setting != None:
            start_param.ego_cruise_setting.CopyFrom(ego_cruise_setting)
        if sync_mode != None:
            start_param.mode.CopyFrom(sync_mode)
            init_sync_mode = sync_mode.type
        if simulation_settings != None:
            start_param.simulation_settings.CopyFrom(simulation_settings)
        if ego_setting != None:
            start_param.ego_setting.CopyFrom(ego_setting)
            ego_id = ego_setting.ego_id
            ego_label = ego_setting.label

        response = self._sim_adapter.start(start_param)        
        if (response.status == STATUS_CODE_SUCCESS) or (response.description == 'same map'):
            self._simulation_world = SimulationWorld(self._sim_adapter, self._client_key, map_name, 
                                                     init_sync_mode, ego_id, ego_label)
        