import grpc
import morai.common.type_pb2 as morai_common

import morai.simulator.simulator_pb2_grpc as simulator_grpc
import morai.simulation.simulation_pb2_grpc as simulation_grpc
import morai.environment.environment_pb2_grpc as env_grpc
import morai.map.map_pb2_grpc as map_grpc
import morai.actor.actor_pb2_grpc as actor_grpc
import morai.util.util_pb2_grpc as util_grpc
import morai.scenario.scenario_pb2_grpc as scenario_grpc
import morai.sensor.sensor_pb2_grpc as sensor_grpc
import morai.infrastructure.infrastructure_pb2_grpc as infrastructure_grpc

MAX_MESSAGE_LENGTH = 33554432 # 32mb

class SimAdapter:
    def __init__(self):
        self._address = '127.0.0.1'
        self._port = 7789

        self._channel = None
        self._simulator_stub = None
        self._simulation_stub = None
        self._environment_stub = None
        self._map_stub = None
        self._actor_stub = None
        self._util_stub = None
        self._scenario_stub = None
        self._sensor_stub = None
        self._infrastructure_stub = None

    
    def is_connected(self):
        return False if (self._channel == None) else True


    def connect(self, address, port):
        if self.is_connected():
            self.disconnect()

        self._address = address
        self._port = port

        self._channel = grpc.insecure_channel(
            f'{self._address}:{self._port}',
            options=[
                ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
            ]
        )

        self._simulator_stub = simulator_grpc.SimulatorStub(self._channel)
        self._simulation_stub = simulation_grpc.SimulationStub(self._channel)
        self._environment_stub = env_grpc.EnvironmentStub(self._channel)
        self._map_stub = map_grpc.MapStub(self._channel)
        self._actor_stub = actor_grpc.ActorStub(self._channel)
        self._util_stub = util_grpc.UtilStub(self._channel)
        self._scenario_stub = scenario_grpc.ScenarioStub(self._channel)
        self._sensor_stub = sensor_grpc.SensorStub(self._channel)
        self._infrastructure_stub = infrastructure_grpc.InfrastructureStub(self._channel)


    def disconnect(self):
        if not self.is_connected():
            return

        self._channel.close()
        self._channel = None
        
        self._simulator_stub = None
        self._simulation_stub = None
        self._environment_stub = None
        self._map_stub = None
        self._actor_stub = None
        self._util_stub = None
        self._scenario_stub = None
        self._sensor_stub = None
        self._infrastructure_stub = None


#region Simulator rpc

    def get_simulator_version(self):
        response = None
        try:
            response = self._simulator_stub.GetSimulatorVersion(morai_common.Empty())
        except BaseException as e:
            print(f'get_simulator_version failed : {e}')

        return response


    def get_timestamp(self):
        response = None
        try:
            response = self._simulator_stub.GetTimestamp(morai_common.Empty())
        except BaseException as e:
            print(f'get_timestamp failed : {e}')

        return response

        
    def get_available_maps(self):
        response = None
        try:
            response = self._simulator_stub.GetAvailableMaps(morai_common.Empty())
        except BaseException as e:
            print(f'get_available_maps failed : {e}')

        return response

        
    def get_available_objects(self):        
        response = None
        try:
            response = self._simulator_stub.GetAvailableObject(morai_common.Empty())
        except BaseException as e:
            print(f'get_available_maps failed : {e}')

        return response

        
    def get_simulator_data_path(self):
        response = None
        try:
            response = self._simulator_stub.GetDataPath(morai_common.Empty())
        except BaseException as e:
            print(f'get_simulator_data_path failed : {e}')

        return response


    def set_rendering_mode(self, rendering_mode):
        response = None
        try:
            response = self._simulator_stub.SetRenderingMode(rendering_mode)
        except BaseException as e:
            print(f'set_rendering_mode failed : {e}')

        return response


    def check_latency(self):
        try:
            self._simulator_stub.CheckLatency(morai_common.Empty())
        except BaseException as e:
            print(f'check_latency failed : {e}')

#endregion Simulator rpc


#region Simulation rpc

    def start(self, start_param):
        response = None
        try:
            response = self._simulation_stub.Start(start_param)
        except BaseException as e:
            print(f'start failed : {e}')

        return response


    def stop(self, client_key):
        response = None
        try:
            response = self._simulation_stub.Stop(client_key)
        except BaseException as e:
            print(f'stop failed : {e}')

        return response


    def pause(self):
        response = None
        try:
            response = self._simulation_stub.Pause(morai_common.Empty())
        except BaseException as e:
            print(f'pause failed : {e}')

        return response


    def resume(self):
        response = None
        try:
            response = self._simulation_stub.Resume(morai_common.Empty())
        except BaseException as e:
            print(f'resume failed : {e}')

        return response


    def get_synchronous_mode(self):
        response = None
        try:
            response = self._simulation_stub.GetSynchronousMode(morai_common.Empty())
        except BaseException as e:
            print(f'get_synchronous_mode failed : {e}')

        return response


    def set_synchronous_mode(self, sync_mode):
        response = None
        try:
            response = self._simulation_stub.SetSynchronousMode(sync_mode)
        except BaseException as e:
            print(f'set_synchronous_mode failed : {e}')

        return response


    def tick(self, msec):
        response = None
        try:
            response = self._simulation_stub.Tick(msec)
        except BaseException as e:
            print(f'tick failed : {e}')

        return response


    def wait_for_tick(self):
        response = None
        try:
            response = self._simulation_stub.WaitForTick(morai_common.Empty())
        except BaseException as e:
            print(f'wait_for_tick failed : {e}')

        return response
    
    def send_string_list_message(self, strParam):
        response = None
        try:
            response = self._simulation_stub.SendStringListMessage(strParam)
        except BaseException as e:
            print(f'send_string_list_message failed : {e}')

        return response

#endregion Simulation rpc


#region Environment rpc

    def get_env_time(self):
        response = None
        try:
            response = self._environment_stub.GetTime(morai_common.Empty())
        except BaseException as e:
            print(f'get_env_time failed : {e}')

        return response


    def set_env_time(self, simulation_time):
        response = None
        try:
            response = self._environment_stub.SetTime(simulation_time)
        except BaseException as e:
            print(f'set_env_time failed : {e}')

        return response


    def get_env_weather(self):
        response = None
        try:
            response = self._environment_stub.GetWeather(morai_common.Empty())
        except BaseException as e:
            print(f'get_env_weather failed : {e}')

        return response


    def set_env_weather(self, simulation_weather):
        response = None
        try:
            response = self._environment_stub.SetWeather(simulation_weather)
        except BaseException as e:
            print(f'set_env_time failed : {e}')

        return response

#endregion Environment rpc


#region Map rpc

    def get_mgeo(self, map_name):
        response = None
        try:
            response = self._map_stub.GetMGeo(map_name)
        except BaseException as e:
            print(f'get_mgeo failed : {e}')

        return response


    def get_neighbor_link(self, get_neighbor_link_param):
        response = None
        try:
            response = self._map_stub.GetNeighborLink(get_neighbor_link_param)
        except BaseException as e:
            print(f'get_neighbor_link failed : {e}')

        return response


    def get_vehicles_on_link(self, link_info):
        response = None
        try:
            response = self._map_stub.GetVehiclesOnLink(link_info)
        except BaseException as e:
            print(f'get_vehicles_on_link failed : {e}')

        return response

#endregion Map rpc


#region Actor rpc

    def spawn_vehicle(self, vehicle_spawn_param):
        response = None
        try:
            response = self._actor_stub.SpawnVehicle(vehicle_spawn_param)
        except BaseException as e:
            print(f'spawn_vehicle failed : {e}')

        return response


    def spawn_pedestrian(self, pedestrian_spawn_param):
        response = None
        try:
            response = self._actor_stub.SpawnPedestrian(pedestrian_spawn_param)
        except BaseException as e:
            print(f'spawn_pedestrian failed : {e}')

        return response


    def spawn_obstacle(self, obstacle_spawn_param):
        response = None
        try:
            response = self._actor_stub.SpawnObstacle(obstacle_spawn_param)
        except BaseException as e:
            print(f'spawn_obstacle failed : {e}')

        return response


    def destroy_actor(self, object_info):
        response = None
        try:
            response = self._actor_stub.DestroyActor(object_info)
        except BaseException as e:
            print(f'destroy_actor failed : {e}')

        return response


    def destroy_all_actors(self, client_key):
        response = None
        try:
            response = self._actor_stub.DestroyAllActors(client_key)
        except BaseException as e:
            print(f'destroy_all_actors failed : {e}')

        return response


    def control_vehicle(self, vehicle_control_command):
        response = None
        try:
            response = self._actor_stub.ControlVehicle(vehicle_control_command)
        except BaseException as e:
            print(f'control_vehicle failed : {e}')

        return response


    def control_pedestrian(self, pedestrian_control_command):
        response = None
        try:
            response = self._actor_stub.ControlPedestrian(pedestrian_control_command)
        except BaseException as e:
            print(f'control_pedestrian failed : {e}')

        return response
    

    def control_obstacle(self, obstacle_control_command):
        response = None
        try:
            response = self._actor_stub.ControlObstacle(obstacle_control_command)
        except BaseException as e:
            print(f'control_obstacle failed : {e}')

        return response


    def get_actor_state(self, object_info):
        response = None
        try:
            response = self._actor_stub.GetActorState(object_info)
        except BaseException as e:
            print(f'get_actor_state failed : {e}')

        return response


    def get_all_actors_state(self, filter):
        response = None
        try:
            response = self._actor_stub.GetAllActorsState(filter)
        except BaseException as e:
            print(f'get_all_actors_state failed : {e}')

        return response


    def get_vehicle_spec(self, object_info):
        response = None
        try:
            response = self._actor_stub.GetVehicleSpec(object_info)
        except BaseException as e:
            print(f'get_vehicle_spec failed : {e}')

        return response


    def get_vehicle_network_setting(self, object_info):
        response = None
        try:
            response = self._actor_stub.GetVehicleNetworkSetting(object_info)
        except BaseException as e:
            print(f'get_vehicle_network_setting failed : {e}')

        return response


    def get_vehicle_control_mode(self, object_info):
        response = None
        try:
            response = self._actor_stub.GetVehicleControlMode(object_info)
        except BaseException as e:
            print(f'get_vehicle_control_mode failed : {e}')

        return response


    def get_option_name(self, object_info):
        response = None
        try:
            response = self._actor_stub.GetOptionName(object_info)
        except BaseException as e:
            print(f'get_option_name failed : {e}')

        return response


    def set_scale(self, scale):
        response = None
        try:
            response = self._actor_stub.SetScale(scale)
        except BaseException as e:
            print(f'set_scale failed : {e}')

        return response


    def set_transform(self, set_transform_param):
        response = None
        try:
            response = self._actor_stub.SetTransform(set_transform_param)
        except BaseException as e:
            print(f'set_transform failed : {e}')

        return response


    def set_obstacle_animation(self, enable_actor):
        response = None
        try:
            response = self._actor_stub.SetObstacleAnimation(enable_actor)
        except BaseException as e:
            print(f'set_obstacle_animation failed : {e}')

        return response

    
    def set_train_signal_light(self, traffic_light_info):
        response = None
        try:
            response = self._actor_stub.SetTrainSignalLight(traffic_light_info)
        except BaseException as e:
            print(f'set_train_signal_light failed : {e}')

        return response


    def set_pause(self, enable_actor):
        response = None
        try:
            response = self._actor_stub.SetPause(enable_actor)
        except BaseException as e:
            print(f'set_pause failed : {e}')

        return response


    def set_ai(self, enable_actor):
        response = None
        try:
            response = self._actor_stub.SetAI(enable_actor)
        except BaseException as e:
            print(f'set_ai failed : {e}')

        return response


    def set_physics(self, enable_actor):
        response = None
        try:
            response = self._actor_stub.SetPhysics(enable_actor)
        except BaseException as e:
            print(f'set_physics failed : {e}')

        return response


    def set_velocity(self, velocity):
        response = None
        try:
            response = self._actor_stub.SetVelocity(velocity)
        except BaseException as e:
            print(f'set_physics failed : {e}')

        return response


    def set_vehicle_limiter(self, vehicle_limiter):
        response = None
        try:
            response = self._actor_stub.SetVehicleLimiter(vehicle_limiter)
        except BaseException as e:
            print(f'set_vehicle_limiter failed : {e}')

        return response


    def set_vehicle_dynamics_steer(self, dynamics_steer):
        response = None
        try:
            response = self._actor_stub.SetVehicleDynamicsSteer(dynamics_steer)
        except BaseException as e:
            print(f'set_vehicle_dynamics_steer failed : {e}')

        return response


    def set_vehicle_dynamics_speed_limit(self, dynamics_speed_limit):
        response = None
        try:
            response = self._actor_stub.SetVehicleDynamicsSpeedLimit(dynamics_speed_limit)
        except BaseException as e:
            print(f'set_vehicle_dynamics_speed_limit failed : {e}')

        return response


    def set_vehicle_dynamics_mass(self, dynamics_mass):
        response = None
        try:
            response = self._actor_stub.SetVehicleDynamicsMass(dynamics_mass)
        except BaseException as e:
            print(f'set_vehicle_dynamics_steer failed : {e}')

        return response


    def set_vehicle_path_offset(self, dynamics_mass):
        response = None
        try:
            response = self._actor_stub.SetVehiclePathOffset(dynamics_mass)
        except BaseException as e:
            print(f'set_vehicle_path_offset failed : {e}')

        return response


    def set_vehicle_disturbance(self, disturbance):
        response = None
        try:
            response = self._actor_stub.SetVehicleDisturbance(disturbance)
        except BaseException as e:
            print(f'set_vehicle_disturbance failed : {e}')

        return response


    def set_vehicle_fault_injection(self, fault_injection):
        response = None
        try:
            response = self._actor_stub.SetVehicleFaultInjection(fault_injection)
        except BaseException as e:
            print(f'set_vehicle_fault_injection failed : {e}')

        return response


    def set_vehicle_route(self, route):
        response = None
        try:
            response = self._actor_stub.SetVehicleRoute(route)
        except BaseException as e:
            print(f'set_vehicle_route failed : {e}')

        return response


    def set_vehicle_destination(self, destination):
        response = None
        try:
            response = self._actor_stub.SetVehicleDestination(destination)
        except BaseException as e:
            print(f'set_vehicle_destination failed : {e}')

        return response


    def set_vehicle_ego_cruise(self, ego_cruise_control):
        response = None
        try:
            response = self._actor_stub.SetVehicleEgoCruise(ego_cruise_control)
        except BaseException as e:
            print(f'set_vehicle_ego_cruise failed : {e}')

        return response


    def set_vehicle_network(self, network_setting):
        response = None
        try:
            response = self._actor_stub.SetVehicleNetwork(network_setting)
        except BaseException as e:
            print(f'set_vehicle_network failed : {e}')

        return response


    def set_vehicle_steer(self, steer):
        response = None
        try:
            response = self._actor_stub.SetVehicleSteer(steer)
        except BaseException as e:
            print(f'set_vehicle_steer failed : {e}')

        return response


    def set_vehicle_gear(self, gear):
        response = None
        try:
            response = self._actor_stub.SetVehicleGear(gear)
        except BaseException as e:
            print(f'set_vehicle_gear failed : {e}')

        return response


    def set_vehicle_tail_light(self, tail_light):
        response = None
        try:
            response = self._actor_stub.SetVehicleTailLight(tail_light)
        except BaseException as e:
            print(f'set_vehicle_tail_light failed : {e}')

        return response        


    def set_vehicle_control_mode(self, control_mode):
        response = None
        try:
            response = self._actor_stub.SetVehicleControlMode(control_mode)
        except BaseException as e:
            print(f'set_vehicle_control_mode failed : {e}')

        return response
    
    def set_sensor_fault(self, sensor_fault):
        response = None
        try:
            response = self._sensor_stub.SetSensorFault(sensor_fault)
        except BaseException as e:
            print(f'set_sensor_fault failed : {e}')

        return response
    
    def set_sensor_weather_effect(self, weather_effect):
        response = None
        try:
            response = self._sensor_stub.SetWeatherEffect(weather_effect)
        except BaseException as e:
            print(f'set_sensor_weather_effect failed : {e}')

        return response
        

#endregion Actor rpc        


#region Util rpc

    def raycast(self, raycast_param):
        response = None
        try:
            response = self._util_stub.RayCast(raycast_param)
        except BaseException as e:
            print(f'raycast failed : {e}')

        return response

#endregion Util rpc


#refion Scenario rpc

    def load_morai_scenario(self, scenario_file_name):
        response = None
        try :
            response = self._scenario_stub.LoadMoraiScenario(scenario_file_name)
        except BaseException as e :
            print(f'load_morai_scenario : {e}')
            
        return response

    def create_vehicle_spawn_point(self, vehicle_spawn_param):
        response = None
        try :
            response = self._scenario_stub.CreateVehicleSpawnPoint(vehicle_spawn_param)
        except BaseException as e :
            print(f'create_vehicle_spawn_point : {e}')

        return response

    def create_pedestrian_spawn_point(self, vehicle_spawn_param):
        response = None
        try :
            response = self._scenario_stub.CreatePedestrianSpawnPoint(vehicle_spawn_param)
        except BaseException as e :
            print(f'create_pedestrian_spawn_point : {e}')

        return response

    def enable_spawn_point(self, enable_spawn_point_param):
        response = None
        try :
            response = self._scenario_stub.EnableSpawnPoint(enable_spawn_point_param)
        except BaseException as e :
            print(f'enable_spawn_point : {e}')

        return response
    
    def create_friction_control_area(self, create_friction_control_area_param):
        response = None
        try :
            response = self._scenario_stub.CreateFrictionControlArea(create_friction_control_area_param)
        except BaseException as e :
            print(f'enable_spawn_point : {e}')

        return response

#endregion Scenario rpc


#region Sensor rpc

    def add_sensor(self, add_sensor_param):
        response = None
        try :
            response = self._sensor_stub.AddSensor(add_sensor_param)
        except BaseException as e :
            print(f'add_sensor : {e}')

        return response

    def remove_sensor(self, sensor_info):
        response = None
        try :
            response = self._sensor_stub.RemoveSensor(sensor_info)
        except BaseException as e:
            print(f'remove_sensor : {e}')
            
        return response
    
    def set_sensor_setting(self, sensor_setting):
        response = None
        try :
            response = self._sensor_stub.SetSensorSetting(sensor_setting)
        except BaseException as e:
            print(f'set_sensor_setting : {e}')
            
        return response


    def get_sensor_data(self, sensor_info):
        response = None
        try :
            response = self._sensor_stub.GetSensorData(sensor_info)
        except BaseException as e :
            print(f'get_sensor_data : {e}')
        
        return response


    def save_sensor_data(self, sensor_data_save_config):
        response = None
        try :
            response = self._sensor_stub.SaveSensorData(sensor_data_save_config)
        except BaseException as e :
            print(f'save_sensor_data : {e}')
        
        return response
    
    def load_sensor_file(self, sensor_file_name):
        response = None
        try :
            response = self._sensor_stub.LoadSensorFile(sensor_file_name)
        except BaseException as e :
            print(f'load_sensor_file : {e}')

        return response

#endregion Sensor rpc

#region Infrastructure rpc

    def get_traffic_light_info(self, get_traffic_light_info_param):
        response = None
        try :
            response = self._infrastructure_stub.GetTrafficLightInfo(get_traffic_light_info_param)
        except BaseException as e :
            print(f'get_traffic_light_info : {e}')
        finally :
            return response
    
    def get_intersection_tl_info(self, get_intersection_tl_info_param):
        response = None
        try :
            response = self._infrastructure_stub.GetIntersectionTLInfo(get_intersection_tl_info_param)
        except BaseException as e :
            print(f'get_intersection_tl_info_param : {e}')
        finally :
            return response
    
    def set_traffic_light_state(self, set_traffic_light_state_param):
        response = None
        try :
            response = self._infrastructure_stub.SetTrafficLightState(set_traffic_light_state_param)
        except BaseException as e :
            print(f'set_traffic_light_state_param : {e}')
        finally :
            return response
        
    def set_intersection_phase(self, set_intersection_state_param):
        response = None
        try :
            response = self._infrastructure_stub.SetIntersectionPhase(set_intersection_state_param)
        except BaseException as e :
            print(f'set_intersection_state_param : {e}')
        finally :
            return response
        
    def set_intersection_schedule(self, set_intersection_schedule_param):
        response = None
        try :
            response = self._infrastructure_stub.SetIntersectionSchedule(set_intersection_schedule_param)
        except BaseException as e :
            print(f'set_intersection_schedule_param : {e}')
        finally :
            return response
        
    def set_external_force(self, external_force_param):
        response = None
        try :
            response = self._environment_stub.SetExternalForce(external_force_param)
        except BaseException as e :
            print(f'set_external_force : {e}')
        finally :
            return response
        
    def set_sensor_mute_by_type(self, sensor_mute_param):
        response = None
        try :
            response = self._sensor_stub.SetSensorMuteByType(sensor_mute_param)
        except BaseException as e :
            print(f'set_sensor_mute : {e}')
        finally :
            return response
        
#endregion Infrastructure rpc
