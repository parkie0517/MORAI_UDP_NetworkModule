from actor import *
from proto.morai.common.enum_pb2 import OBJECT_TYPE_VEHICLE
from proto.morai.actor.actor_enum_pb2 import EGO_CRUISE_TYPE_LINK, NETWORK_COMM_TYPE_ROS, NETWORK_CONNECT_TYPE_EGO, NETWORK_CONNECT_TYPE_PUBSUB, NETWORK_ITEM_TYPE_BRIDGE_IP, NETWORK_ITEM_TYPE_BRIDGE_PORT, VEHICLE_FAULT_TYPE_CONTROL, VEHICLE_FAULT_TYPE_SENSOR, VEHICLE_FAULT_TYPE_TIRE
from proto.morai.actor.actor_network_pb2 import NetworkIpSetting, NetworkItem
from proto.morai.actor.actor_set_pb2 import EgoCruiseControl, NetworkConfig, VehicleControlModeParam, VehicleDestination, VehicleDisturbance, VehicleDynamicsMass, VehicleDynamicsSpeedLimit, VehicleDynamicsSteer, VehicleFaultInjection, VehicleGear, VehicleLimiter, VehiclePathOffset, VehicleRoute, VehicleSteer, VehicleTailLight
from proto.morai.actor.actor_control_pb2 import VehicleCtrlCmd
from proto.morai.map.link_info_pb2 import LinkInfo
from proto.morai.sensor.add_sensor_param_pb2 import AddSensorParam
from proto.morai.sensor.sensor_enum_pb2 import SENSOR_TYPE_GROUNDTRUTH
from proto.morai.sensor.sensor_info_pb2 import SensorInfo
from proto.morai.sensor.sensor_settings_pb2 import SensorSetting, SensorFault, WeatherEffect

class Vehicle(Actor):
    def __init__(self, sim_adapter, client_key, actor_id) -> None:
        super().__init__(sim_adapter, client_key, actor_id)
        self._object_type = OBJECT_TYPE_VEHICLE
        self.vehicle_spec = None
        self.attached_sensors = {}


    def control(self, long_cmd_type, throttle, brake, steer, velocity, acceleration, frame):
        control_param = VehicleCtrlCmd()
        control_param.actor_info.CopyFrom(self.get_object_info())
        control_param.long_cmd_type = long_cmd_type
        control_param.throttle = throttle
        control_param.brake = brake
        control_param.steer = steer
        control_param.velocity = velocity
        control_param.acceleration = acceleration
        control_param.frame = frame

        result = self._sim_adapter.control_vehicle(control_param)        
        return result.status == STATUS_CODE_SUCCESS


    def get_vehicle_spec(self):
        if self.vehicle_spec == None:
            self.vehicle_spec = self._sim_adapter.get_vehicle_spec(self.get_object_info())
        return self.vehicle_spec


    def get_vehicle_network_setting(self):
        return self._sim_adapter.get_vehicle_network_setting(self.get_object_info())


    def get_control_mode(self):
        control_mode = self._sim_adapter.get_vehicle_control_mode(self.get_object_info())
        return control_mode.mode


    def set_ai(self, enabled):
        param = EnableActor()
        param.actor_info.CopyFrom(self.get_object_info())
        param.enable = enabled

        result = self._sim_adapter.set_ai(param)
        return result.status == STATUS_CODE_SUCCESS


    def set_control_mode(self, mode):
        param = VehicleControlModeParam()
        param.actor_info.CopyFrom(self.get_object_info())
        param.mode = mode

        result = self._sim_adapter.set_vehicle_control_mode(param)
        return result.status == STATUS_CODE_SUCCESS


    def set_vehicle_limiter(self, limiter_type, min_saturation, max_saturation, failling_rate, rising_rate, reset=False):
        param = VehicleLimiter()
        param.actor_info.CopyFrom(self.get_object_info())
        param.limiter_type = limiter_type
        param.min_saturation = min_saturation
        param.max_saturation = max_saturation
        param.falling_rate = failling_rate
        param.rising_rate = rising_rate
        param.reset = reset

        result = self._sim_adapter.set_vehicle_limiter(param)        
        return result.status == STATUS_CODE_SUCCESS

    
    def set_vehicle_dynamics_steer(self, max_steer_angle, reset=False):
        param = VehicleDynamicsSteer()
        param.actor_info.CopyFrom(self.get_object_info())
        param.max_steer_angle = max_steer_angle
        param.reset = reset

        result = self._sim_adapter.set_vehicle_dynamics_steer(param)        
        return result.status == STATUS_CODE_SUCCESS

    
    def set_vehicle_dynamics_speed_limit(self, speed_limiter, speed_limit, reset=False):
        param = VehicleDynamicsSpeedLimit()
        param.actor_info.CopyFrom(self.get_object_info())
        param.speed_limiter = speed_limiter
        param.speed_limit = speed_limit
        param.reset = reset

        result = self._sim_adapter.set_vehicle_dynamics_speed_limit(param)        
        return result.status == STATUS_CODE_SUCCESS

    
    def set_vehicle_dynamics_mass(self, mass, reset=False):
        param = VehicleDynamicsMass()
        param.actor_info.CopyFrom(self.get_object_info())
        param.mass = mass
        param.reset = reset

        result = self._sim_adapter.set_vehicle_dynamics_mass(param)        
        return result.status == STATUS_CODE_SUCCESS


    def set_vehicle_path_offset(self, value, type):
        param = VehiclePathOffset()
        param.actor_info.CopyFrom(self.get_object_info())
        param.value = value
        param.lat_bias_mode = type

        result = self._sim_adapter.set_vehicle_path_offset(param)        
        return result.status == STATUS_CODE_SUCCESS


    def set_vehicle_disturbance(self, situation, behavior, duration, magnitude):
        param = VehicleDisturbance()
        param.actor_info.CopyFrom(self.get_object_info())
        param.situation = situation
        param.behavior = behavior
        param.duration = duration
        param.magnitude = magnitude

        result = self._sim_adapter.set_vehicle_disturbance(param)        
        return result.status == STATUS_CODE_SUCCESS


    def set_vehicle_fault_injection(self, fault_type, control:list=None, tire:list=None, sensor:list=None):
        param = VehicleFaultInjection()
        param.actor_info.CopyFrom(self.get_object_info())
        param.type = fault_type

        valid = True
        if (fault_type == VEHICLE_FAULT_TYPE_CONTROL) and (control != None):
            param.control.extend(control)
        elif (fault_type == VEHICLE_FAULT_TYPE_TIRE) and (tire != None):
            param.tire.extend(tire)
        elif fault_type == VEHICLE_FAULT_TYPE_SENSOR and sensor == None:
            param.sensor.extend(sensor)
        else:
            valid = False
        
        if valid:
            result = self._sim_adapter.set_vehicle_fault_injection(param)        
            return result.status == STATUS_CODE_SUCCESS
        else:
            return False


    def set_vehicle_route(self, decision_range, links):
        param = VehicleRoute()
        param.actor_info.CopyFrom(self.get_object_info())
        param.decision_range = decision_range
        for link in links:            
            link_info = LinkInfo()
            link_info.id.value = link
            link_info.waypoint_idx = 0
            param.links.append(link_info)
        
        result = self._sim_adapter.set_vehicle_route(param)        
        return result.status == STATUS_CODE_SUCCESS


    def set_vehicle_destination(self, decision_range, position):
        param = VehicleDestination()
        param.actor_info.CopyFrom(self.get_object_info())
        param.decision_range = decision_range
        param.position.CopyFrom(position)
        
        result = self._sim_adapter.set_vehicle_destination(param)        
        return result.status == STATUS_CODE_SUCCESS


    def set_cruise_mode(self, enable, cruise_type=EGO_CRUISE_TYPE_LINK, link_speed_ratio=80, constant_velocity=30):
        param = EgoCruiseControl()
        param.actor_info.CopyFrom(self.get_object_info())
        param.cruise_on = enable
        param.cruise_type = cruise_type
        param.link_speed_ratio = link_speed_ratio
        param.constant_velocity = constant_velocity

        result = self._sim_adapter.set_vehicle_ego_cruise(param)        
        return result.status == STATUS_CODE_SUCCESS


    def set_vehicle_network_setting(self, enabled, frame_rate, bridge_ip, bridge_port, protocol_setting):
        # bridge settings
        bridge_ip_item = NetworkItem()
        bridge_ip_item.type = NETWORK_ITEM_TYPE_BRIDGE_IP
        bridge_ip_item.value = bridge_ip
        
        bridge_port_item = NetworkItem()
        bridge_port_item.type = NETWORK_ITEM_TYPE_BRIDGE_PORT
        bridge_port_item.value = bridge_port

        ego_ip_setting = NetworkIpSetting()
        ego_ip_setting.connect_type = NETWORK_CONNECT_TYPE_EGO        
        ego_ip_setting.items.append(bridge_ip_item)
        ego_ip_setting.items.append(bridge_port_item)
        
        pubsub_ip_setting = NetworkIpSetting()
        pubsub_ip_setting.connect_type = NETWORK_CONNECT_TYPE_PUBSUB        
        pubsub_ip_setting.items.append(bridge_ip_item)
        pubsub_ip_setting.items.append(bridge_port_item)

        # network config
        network_config = NetworkConfig()
        network_config.actor_info.CopyFrom(self.get_object_info())
        network_config.enabled = enabled
        network_config.comm_type = NETWORK_COMM_TYPE_ROS    # Support ROS only
        network_config.frame_rate = frame_rate
        network_config.protocol_settings.CopyFrom(protocol_setting)
        network_config.ip_settings.append(ego_ip_setting)
        network_config.ip_settings.append(pubsub_ip_setting)

        result = self._sim_adapter.set_vehicle_network(network_config)
        return result.status == STATUS_CODE_SUCCESS


    def set_vehicle_steer(self, steer):
        param = VehicleSteer()
        param.actor_info.CopyFrom(self.get_object_info())
        param.steer = steer

        result = self._sim_adapter.set_vehicle_steer(param)        
        return result.status == STATUS_CODE_SUCCESS
        

    def set_vehicle_gear(self, gear):
        param = VehicleGear()
        param.actor_info.CopyFrom(self.get_object_info())
        param.gear = gear

        result = self._sim_adapter.set_vehicle_gear(param)        
        return result.status == STATUS_CODE_SUCCESS


    def set_vehicle_tail_light(self, turn_signal):
        param = VehicleTailLight()
        param.actor_info.CopyFrom(self.get_object_info())
        param.signal = turn_signal

        result = self._sim_adapter.set_vehicle_tail_light(param)        
        return result.status == STATUS_CODE_SUCCESS


    def add_sensor(self, sensor_type, transform):
        sensor_id = -1
        param = AddSensorParam()
        param.vehicle_id.CopyFrom(self.get_object_info())
        param.sensor_type = sensor_type
        param.transform.CopyFrom(transform)

        result = self._sim_adapter.add_sensor(param)
        if result.status == STATUS_CODE_SUCCESS:
            sensor_id = result.custom_message
            self.attached_sensors[sensor_id] = sensor_type
        return sensor_id


    def set_sensor(self, sensor_id, setting):
        if sensor_id not in self.attached_sensors:
            return False

        if self.attached_sensors[sensor_id] != SENSOR_TYPE_GROUNDTRUTH:
            return False 

        param = SensorSetting()
        param.sensor_info.vehicle_info.CopyFrom(self.get_object_info())
        param.sensor_info.sensor_id.value = sensor_id
        param.sensor_info.sensor_type = self.attached_sensors[sensor_id]
        param.gt_sensor.CopyFrom(setting)

        result = self._sim_adapter.set_sensor_setting(param)
        return result.status == STATUS_CODE_SUCCESS


    def remove_sensor(self, sensor_id):
        param = SensorInfo()
        param.vehicle_info.CopyFrom(self.get_object_info())
        param.sensor_id.value = sensor_id

        result = False
        response = self._sim_adapter.remove_sensor(param)
        if response.status == STATUS_CODE_SUCCESS:
            if sensor_id in self.attached_sensors:
                del self.attached_sensors[sensor_id]
            result = True

        return result


    def get_sensor_data(self, sensor_id):
        param = SensorInfo()
        param.vehicle_info.CopyFrom(self.get_object_info())
        param.sensor_id.value = sensor_id
        if sensor_id in self.attached_sensors:
            param.sensor_type = self.attached_sensors[sensor_id]

        response = self._sim_adapter.get_sensor_data(param)
        return response
    
    def set_vehicle_gear(self, gear):
        param = VehicleGear()
        param.actor_info.CopyFrom(self.get_object_info())
        param.gear = gear

        result = self._sim_adapter.set_vehicle_gear(param)        
        return result.status == STATUS_CODE_SUCCESS
    
    def set_sensor_fault(self, sensor_id, data_qualifier, type):
        print("set_sensor_fault")
        
        param = SensorFault()

        param.sensor_id.value = sensor_id
        param.data_qualifier = data_qualifier
        param.type = type
        
        result = self._sim_adapter.set_sensor_fault(param)   
        return result
    
    def set_sensor_weather_effect(self, sensor_id, is_true):
        print("set_weather_effect")
        
        param = WeatherEffect()
        
        param.sensor_id.value = sensor_id
        param.is_true = is_true
        
        result = self._sim_adapter.set_sensor_weather_effect(param)  
        return result