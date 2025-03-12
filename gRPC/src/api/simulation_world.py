import os, sys
from api.map import Map
from api.obstacle import Obstacle
from api.pedestrian import Pedestrian
from api.vehicle import Vehicle
from proto.morai.actor.actor_get_pb2 import GetAllActorsFilter
from proto.morai.common.object_identifier_pb2 import ObjectIdentifier
from proto.morai.common.type_pb2 import Int32Value, StringValue
from proto.morai.environment.time_pb2 import SimulationTime

from proto.morai.environment.weather_pb2 import Weather
from proto.morai.infrastructure.intersection_pb2 import IntersectionPhase, IntersectionSchedule
from proto.morai.infrastructure.traffic_light_pb2 import GetTrafficLightInfoParam, TrafficLightStateParam
from proto.morai.map.get_neighbor_link_param_pb2 import GetNeighborLinkParam
from proto.morai.map.link_info_pb2 import LinkInfo
from proto.morai.scenario.spawn_point_pb2 import EnableSpawnPointParam
from proto.morai.sensor.sensor_data_save_config_pb2 import SensorDataSaveConfig
from proto.morai.simulation.simulation_enum_pb2 import SYNC_MODE_TYPE_UNSPECIFIED
from proto.morai.simulation.sync_mode_pb2 import SyncMode

current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '..')))
sys.path.append(os.path.normpath(os.path.join(current_path, '../proto')))

# from defines import *
from actor import *
from proto.sim_adapter import *
from proto.morai.common.enum_pb2 import *
from proto.morai.actor.actor_spawn_pb2 import ObstacleSpawnParam, PedestrianSpawnParam, VehicleSpawnParam, ActorSpawnInfo

class SimulationWorld:
    def __init__(self, sim_adapter, client_key, map_name=None, sync_mode=SYNC_MODE_TYPE_UNSPECIFIED, ego_id='Ego', ego_label='Ego') -> None:
        self._sim_adapter: SimAdapter = sim_adapter
        self._client_key = client_key
        self._actors = dict()        
        self._map = Map(sim_adapter, map_name)
        self._current_sync_mode =  sync_mode

        self._ego_label = ego_label
        self._ego_id = ego_id

        self.destroy_all_actors()
        self._set_ego()


    def finalize(self):
        param = StringValue()
        param.value = self._client_key
        self.destroy_all_actors()
        self._sim_adapter.stop(param)
        
        self._actors.clear()


    def get_map(self):
        return self._map


    def pause(self):
        self._sim_adapter.pause()


    def resume(self):
        self._sim_adapter.resume()


    def spawn_vehicle(self, transform, model_name, label, request_id='', velocity=30, pause=False, multi_ego=False):
        vehicle = None
        param = VehicleSpawnParam()
        param.spawn_info.CopyFrom(self._get_spawn_info(OBJECT_TYPE_VEHICLE, transform, model_name, label, request_id))
        param.velocity = velocity
        param.pause = pause
        param.multi_ego = multi_ego

        response = self._sim_adapter.spawn_vehicle(param)
        if response.status == STATUS_CODE_SUCCESS:
            vehicle = Vehicle(self._sim_adapter, self._client_key, response.custom_message)
            self._actors[response.custom_message] = vehicle

        return vehicle
    

    def spawn_pedestrian(self, transform, model_name, label, request_id='', velocity=10, active_dist=10, move_dist=10, start_action=False):
        pedestrian = None
        param = PedestrianSpawnParam()
        param.spawn_info.CopyFrom(self._get_spawn_info(OBJECT_TYPE_PEDESTRIAN, transform, model_name, label, request_id))
        param.velocity = velocity
        param.active_dist = active_dist
        param.move_dist = move_dist
        param.start_action = start_action

        response = self._sim_adapter.spawn_pedestrian(param)
        if response.status == STATUS_CODE_SUCCESS:
            pedestrian = Pedestrian(self._sim_adapter, self._client_key, response.custom_message)
            self._actors[response.custom_message] = pedestrian

        return pedestrian


    def spawn_obstacle(self, transform, model_name, label, request_id='', scale=None):
        obstacle = None
        param = ObstacleSpawnParam()
        param.spawn_info.CopyFrom(self._get_spawn_info(OBJECT_TYPE_OBSTACLE, transform, model_name, label, request_id))
        if scale == None:
            param.scale.x = 1
            param.scale.y = 1
            param.scale.z = 1
        else:
            param.scale.CopyFrom(scale)

        response = self._sim_adapter.spawn_obstacle(param)
        if response.status == STATUS_CODE_SUCCESS:
            obstacle = Obstacle(self._sim_adapter,self._client_key, response.custom_message)
            self._actors[response.custom_message] = obstacle

        return obstacle


    def get_actor(self, actor_id):
        actor = None
        if actor_id in self._actors:
            actor = self._actors[actor_id]

        return actor


    def _get_spawn_info(self, object_type, transform, model_name, label, request_id=''):
        spawn_info = ActorSpawnInfo()
        spawn_info.actor_info.id.value = request_id
        spawn_info.actor_info.object_type = object_type
        spawn_info.actor_info.client_key = self._client_key
        spawn_info.transform.CopyFrom(transform)
        spawn_info.model_name = model_name
        spawn_info.label = label

        return spawn_info


    def set_weather(self, weather_type):
        weather = Weather()
        weather.type = weather_type

        self._sim_adapter.set_env_weather(weather)


    def get_weather(self):
        weather_type = None
        cur_weather = self._sim_adapter.get_env_weather()
        if cur_weather != None:
            weather_type = cur_weather.type

        return weather_type


    def set_time(self, hour, data_only=False):
        time = SimulationTime()
        time.hour = hour
        time.data_only = data_only

        self._sim_adapter.set_env_time(time)


    def get_time(self):
        time = -1
        cur_time = self._sim_adapter.get_env_time()
        if cur_time != None:
            time = cur_time.hour

        return time


    def destroy_all_actors(self, remove_all=False):
        param = StringValue()
        if remove_all == False:
            param.value = self._client_key
        self._sim_adapter.destroy_all_actors(param)


    def get_all_actors_state(self, vehicle=True, pedestrian=False, obstacle=False):
        filter = GetAllActorsFilter()
        filter.client_key = self._client_key
        filter.vehicle = vehicle
        filter.pedestrian = pedestrian
        filter.obstacle = obstacle
        return self._sim_adapter.get_all_actors_state(filter)


    def get_synchronous_mode(self):
        mode = self._sim_adapter.get_synchronous_mode()
        self._current_sync_mode = mode.type
        return self._current_sync_mode

    
    def set_synchronous_mode(self, sync_mode_type, tick_period=20):
        param = SyncMode()
        param.type = sync_mode_type
        param.tick_period = tick_period
        response = self._sim_adapter.set_synchronous_mode(param)

        result = False
        if response.status == STATUS_CODE_SUCCESS:
            self._current_sync_mode = sync_mode_type
            result = True
        
        return result


    def get_neighbor_link(self, type, link_id):
        param = GetNeighborLinkParam()
        param.type = type
        param.target_link_id.value = link_id
        response = self._sim_adapter.get_neighbor_link(param)

        return response.values


    def get_vehicles_on_link(self, link_id):
        param = LinkInfo()
        param.id.value = link_id
        param.waypoint_idx = 0
        response = self._sim_adapter.get_vehicles_on_link(param)

        return response.values


    def _set_ego(self):
        self._actors[self._ego_id] = Vehicle(self._sim_adapter, self._client_key, self._ego_id)


    def get_ego(self):
        if self._ego_id not in self._actors:
            self._set_ego()

        return self._actors[self._ego_id]


    def save_sensor_data(self, is_custom_filename=False, custom_filename='', file_dir=''):
        """ MORAI SIM의 센서 데이터 저장 기능을 이용한 센서 데이터 저장 """
        param = SensorDataSaveConfig()
        param.is_custom_file_name = is_custom_filename
        param.custom_file_name = custom_filename
        param.file_dir = file_dir

        result = self._sim_adapter.save_sensor_data(param)        
        return result.status == STATUS_CODE_SUCCESS


    def load_ego_sensor_setting_file(self, setting_filename):
        """ 센서 설정 파일을 로드하여 Ego 차량에 부착한다. """
        if len(setting_filename) <= 0:
            return False

        param = StringValue()
        param.value = setting_filename

        result = self._sim_adapter.load_sensor_file(param)
        return result.status == STATUS_CODE_SUCCESS
        

    def load_scenario_file(self, scenario_filename):
        """ MORAI SIM 시나리오 파일을 로드한다. """
        param = StringValue()
        param.value = scenario_filename

        result = self._sim_adapter.load_morai_scenario(param)
        return result.status == STATUS_CODE_SUCCESS


    def wait_for_tick(self):
        if self._current_sync_mode != SYNC_MODE_TYPE_UNSPECIFIED:
            return False

        timestamp = self._sim_adapter.wait_for_tick()
        return timestamp.value


    def tick(self, count):
        if self._current_sync_mode == SYNC_MODE_TYPE_UNSPECIFIED:
            return False
        param = Int32Value()
        param.value = count

        return self._sim_adapter.tick(param)


    def get_traffic_light_info(self, type, value):
        """ 신호등 정보를 가져옴
            type이 GET_TL_INFO_BY_LINK_ID일 때는 value에 link id를,
            type이 GET_TL_INFO_BY_TL_ID일 때는 value에 traffic light id를 넣어야 함
        """
        param = GetTrafficLightInfoParam()
        param.type = type
        param.value = value

        return self._sim_adapter.get_traffic_light_info(param)


    def set_traffic_light_info(self, tl_id, color, impulse=False, sibling=True):
        """ 신호등 정보를 설정함 
        Args:
            tl_id(string): 신호등 아이디
            color(TrafficLightColor): 신호등 색상
            impulse(bool): True 일시적, False 영구적
            sibling(bool): True 동일한 진입로 신호등 함께 변경, False 해당 신호등만 변경
        """
        param = TrafficLightStateParam()
        param.info.id.value = tl_id
        param.info.color = color
        param.is_impulse = impulse
        param.set_sibling = sibling

        result = self._sim_adapter.set_traffic_light_state(param)
        return result.status == STATUS_CODE_SUCCESS


    def get_intersection_tl_info(self, intersection_id):
        intersection_info = ObjectIdentifier()
        intersection_info.value = intersection_id

        return self._sim_adapter.get_intersection_tl_info(intersection_info)


    def set_intersection_phase(self, intersection_id, phase):
        param = IntersectionPhase()
        param.id.value = intersection_id
        param.phase = phase

        result = self._sim_adapter.set_intersection_phase(param)
        return result.status == STATUS_CODE_SUCCESS


    def set_intersection_schedule(self, intersection_id, vehicle_schedules, yellow_schedules, ped_schedules):
        param = IntersectionSchedule()
        param.id.value = intersection_id
        for tl in vehicle_schedules:
            param.vehicle.append(tl)
        for tl in yellow_schedules:
            param.yellow.append(tl)
        for tl in ped_schedules:
            param.pedestrian.append(tl)

        result = self._sim_adapter.set_intersection_schedule(param)
        return result.status == STATUS_CODE_SUCCESS


    def create_vehicle_spawn_point(self, vehicle_spawn_point_param):
        result = self._sim_adapter.create_vehicle_spawn_point(vehicle_spawn_point_param)
        return result.custom_message


    def create_pedestrian_spawn_point(self, ped_spawn_point_param):
        result = self._sim_adapter.create_pedestrian_spawn_point(ped_spawn_point_param)
        return result.custom_message


    def enable_spawn_point(self, spawn_point_id, enable):
        param = EnableSpawnPointParam()
        param.object_info.id.value = spawn_point_id
        param.object_info.object_type = OBJECT_TYPE_SPAWN_POINT
        param.object_info.client_key = self._client_key
        param.is_active = enable

        result = self._sim_adapter.enable_spawn_point(param)
        return result.status == STATUS_CODE_SUCCESS


    def create_friction_control_area(self, friction_param):
        result = self._sim_adapter.create_friction_control_area(friction_param)
        return result.custom_message
    
    def add_sensor(self, sensor_setting):
        result = self._sim_adapter.add_sensor(sensor_setting)
        return result.status == STATUS_CODE_SUCCESS
    
    #def get_vehicle_control_mode(self):
        #result = self._sim_adapter.get_vehicle_control_mode()
        #return result
        