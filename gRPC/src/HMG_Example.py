import os, sys, time
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, 'proto')))
from proto.sim_adapter import *

MORAI_SIM_ADDRESS = '127.0.0.1'
MORAI_SIM_PORT = 7789

"""
MORAI gRPC API 사용예제
자세한 설명 아래 gRPC Manual Link를 참조한다.
https://help-morai-sim.scrollhelp.site/ko/sim-api-guide/Working-version/grpc-api-docs
https://morai-autonomous.github.io/grpc-docs/


MORAI SIM을 실행(로딩 완료)후 본 예제코드를 실행함.

본 예제는 아래와 같은 내용을 포함하고 있음.
- Simulator 관련
    - SetSimulationStart : Simulation Start(Map, Vehicle 선택)
    - SetSimPause : Simulation 일시정지
    - SetSimResume : Simulation 일시정지 해제

- 차량 관련
    - SetVehiclePosition : Ego 차량 위치 및 자세
    - SetVehicleControlMode : Ego 차량 제어 모드
    - SetVehicleVelocity: Ego 차량 속도
    - 경로설정 , ControlMode가 VEHICLE_CONTROL_CRUISE_MODE일 때 적용
        - SetVehicleRoute : Mgeo Link idx 기준으로 NPC Vehicle 경로 설정
        - SetVehicleDestination : NPC 차량 위치와 Destination 기준으로 최단경로 설정

- Object 관련
    - SetSpawnVehicle : NPC 차량 생성
    - SetSpawnPedestrian : NPC 보행자 새성
    - SetSpawnObstacle : Object 생성
    Spawn완료 후 SimPause, SimResume을 해줘야 Simulation이 Play함.
   
- Sensor 관련
    - SetSensorFile : Sensor 세팅 파일 Load
    - SetAddSensor : 차량에 Sensor 추가

- Scenario 관련
    - SetLoadMoraiScenario : Scenario 파일 Load
    
"""
class MORAI_gRPC:

    def __init__(self):        
        self.adaptor = SimAdapter()
        self.adaptor.connect(MORAI_SIM_ADDRESS, MORAI_SIM_PORT)


    def main(self):                
        # self.SetSimulationStart()
        # self.SetSpawnVehicle()
        # self.SetVehicleDestination()
        # self.SetSimPause()
        # self.SetSimResume()
        # time.sleep(15)
        # self.SetDestroyAllActors()
        self.SetSpawnObstacle()
        

    

    def SetSimulationStart(self):
        """
        Simulation Start,  Map Vehicle 선택 후 맵 진입
        """
        from proto.morai.simulation.start_param_pb2 import StartParam

        request = StartParam()
        request.map_and_vehicle.map_name = 'R_KR_PG_K-City'
        request.map_and_vehicle.ego_vehicle_model = '2023_Hyundai_Ioniq5'
        try:
            response = self.adaptor._simulation_stub.Start(request)
            print(f'SetMapVehicle Response : {response.description}')
        except Exception as e :
            print(f'SetMapVehicle Error : {e}')

    def SetSensorFile(self):
        """
        sensor.config file Load
        """
        from proto.morai.common.type_pb2 import StringValue
        sensor_file_name = 'SensorInfo_2023_Hyundai_Ioniq5'    

        request = StringValue()    
        request.value = sensor_file_name
        try:
            response = self.adaptor._sensor_stub.LoadSensorFile(request)
            print(f'SetSensorFile Response : {response.description}')
        except Exception as e :
            print(f'SetSensorFile Error : {e}')
            

    def SetSimPause(self):
        from proto.morai.common.type_pb2 import Empty
        request = Empty()    
        
        try:
            response = self.adaptor._simulation_stub.Pause(request)
            print(f'SetSimPause Response : {response.description}')
        except Exception as e :
            print(f'SetSimPause Error : {e}')


    def SetSimResume(self):
        from proto.morai.common.type_pb2 import Empty
        request = Empty()    
        
        try:
            response = self.adaptor._simulation_stub.Resume(request)
            print(f'SetSimResume Response : {response.description}')
        except Exception as e :
            print(f'SetSimResume Error : {e}')


    def SetSpawnVehicle(self):
        """
        NPC(Sur) Vehicle Spawn
        중복된 id.value 값이 사용되면 Simulator 사용에 문제가 될 수 있으니 주의필요.
        """
        from proto.morai.actor.actor_spawn_pb2 import VehicleSpawnParam
        from proto.morai.common.enum_pb2 import ObjectType

        request = VehicleSpawnParam()
        request.spawn_info.actor_info.id.value = '3'
        request.spawn_info.actor_info.object_type = ObjectType.OBJECT_TYPE_VEHICLE
        request.spawn_info.actor_info.client_key = 'Morai_Example'
        request.spawn_info.transform.location.x = 24.92
        request.spawn_info.transform.location.y = 1112.74
        request.spawn_info.transform.location.z = 0.78
        request.spawn_info.transform.rotation.x = 0.897
        request.spawn_info.transform.rotation.y = 1.474
        request.spawn_info.transform.rotation.z = 1.751

        request.spawn_info.model_name = '2015_Kia_K5'
        request.spawn_info.label = 'Sur-3'

        try:
            response = self.adaptor._actor_stub.SpawnVehicle(request)
            print(f'SetSpawnVehicle Response : {response.description}')
        except Exception as e :
            print(f'SetSpawnVehicle Error : {e}')

    
    def SetSpawnPedestrian(self):
        """
        NPC Pedestrian Spawn
        중복된 id.value 값이 사용되면 Simulator 사용에 문제가 될 수 있으니 주의필요.
        """
        from proto.morai.actor.actor_spawn_pb2 import PedestrianSpawnParam
        from proto.morai.common.enum_pb2 import ObjectType

        request = PedestrianSpawnParam()
        request.spawn_info.actor_info.id.value = '4'
        request.spawn_info.actor_info.object_type = ObjectType.OBJECT_TYPE_PEDESTRIAN
        request.spawn_info.actor_info.client_key = 'Morai_Example'
        request.spawn_info.transform.location.x = 24.92
        request.spawn_info.transform.location.y = 1110.74
        request.spawn_info.transform.location.z = 0.78
        request.spawn_info.transform.rotation.x = 0.897
        request.spawn_info.transform.rotation.y = 1.474
        request.spawn_info.transform.rotation.z = 1.751

        request.spawn_info.model_name = 'Man1'
        request.spawn_info.label = 'Ped-4'
        request.velocity = 5 #km/h
        request.active_dist = 10 #m
        request.move_dist = 30 #m
        request.start_action = True

        try:
            response = self.adaptor._actor_stub.SpawnPedestrian(request)
            print(f'SetSpawnPedestrian Response : {response.description}')
        except Exception as e :
            print(f'SetSpawnPedestrian Error : {e}')



    def SetSpawnObstacle(self):
        """
        NPC Obstacle Spawn
        중복된 id.value 값이 사용되면 Simulator 사용에 문제가 될 수 있으니 주의필요.
        
        """
        from proto.morai.actor.actor_spawn_pb2 import ObstacleSpawnParam
        from proto.morai.common.enum_pb2 import ObjectType

        request = ObstacleSpawnParam()
        request.spawn_info.actor_info.id.value = '5'
        request.spawn_info.actor_info.object_type = ObjectType.OBJECT_TYPE_OBSTACLE
        request.spawn_info.actor_info.client_key = 'Morai_Example'
        request.spawn_info.transform.location.x = 24.92
        request.spawn_info.transform.location.y = 1108.74
        request.spawn_info.transform.location.z = 0.78
        request.spawn_info.transform.rotation.x = 0.897
        request.spawn_info.transform.rotation.y = 1.474
        request.spawn_info.transform.rotation.z = 1.751
        request.spawn_info.model_name = 'CargoBox' 
        request.spawn_info.label = ''
        request.scale.x = 1.0
        request.scale.y = 1.0
        request.scale.z = 1.0

        try:
            response = self.adaptor._actor_stub.SpawnObstacle(request)
            print(f'SetSpawnObstacle Response : {response.description}')
        except Exception as e :
            print(f'SetSpawnObstacle Error : {e}')


    def SetDestroyActor(self):
        """
        생성된 Actor(Object, NPC vehicle, pedestrian, obstacle..)를 삭제.

        """
        from proto.morai.common.object_info_pb2 import ObjectInfo
        from proto.morai.common.enum_pb2 import ObjectType

        request = ObjectInfo()
        request.id.value = '5'
        request.object_type = ObjectType.OBJECT_TYPE_OBSTACLE
        request.client_key = 'Morai_Example'        

        try:
            response = self.adaptor._actor_stub.DestroyActor(request)
            print(f'SetDestroyActor Response : {response.description}')
        except Exception as e :
            print(f'SetDestroyActor Error : {e}')
            

    def SetDestroyAllActors(self):
        """
        생성된 모든 Actor(Object, NPC vehicle, pedestrian, obstacle..) 삭제.
        """        
        from proto.morai.common.type_pb2 import StringValue

        request = StringValue()

        request.value = 'Morai_Example'
        try:
            response = self.adaptor._actor_stub.DestroyAllActors(request)
            print(f'SetDestroyAllActors Response : {response.description}')
        except Exception as e :
            print(f'SetDestroyAllActors Error : {e}')


    def SetVehicleRoute(self):
        """
        MGeo 기반 NPC차량 주행경로 설정.
        list_idx_list에 현재 NPC Vehicle이 위치한 Mgeo Link Index부터 시작해서
        원하는 경로(link)의 idx를 입력한다.
        마지막 지점에 도착하면 NPC 차량의 제어가 정상적이지 않을 수 있으니 
        도착지점에서 적절한 처리를 해줘야 함. (e.g SetDestory 로 해당 NPC 차량을 삭제 처리 등.)
        """
        from proto.morai.actor.actor_set_pb2 import VehicleRoute
        from proto.morai.common.enum_pb2 import ObjectType
        from proto.morai.map.link_info_pb2 import LinkInfo

        request = VehicleRoute()
        request.actor_info.id.value = '3'
        request.actor_info.object_type = ObjectType.OBJECT_TYPE_VEHICLE
        request.actor_info.client_key = 'Morai_Example'
        request.decision_range = 1

        list_idx_list = ['A219BS010380','A219BS010813', 'A219BS010398','A219BS010663','A219BS010395']
        
        for idx in list_idx_list:
            link = LinkInfo()
            link.id.value = idx
            request.links.append(link)

        try:
            response = self.adaptor._actor_stub.SetVehicleRoute(request)
            print(f'SetVehicleRoute Response : {response.description}')
        except Exception as e :
            print(f'SetVehicleRoute Error : {e}')



    def SetVehicleDestination(self):
        """
        Vehicle 차량 위치와, Destination 기준으로 최단 경로 세팅         
        """
        from proto.morai.actor.actor_set_pb2 import VehicleDestination
        from proto.morai.common.enum_pb2 import ObjectType        

        request = VehicleDestination()                
        request.actor_info.id.value = '3'
        request.actor_info.object_type = ObjectType.OBJECT_TYPE_VEHICLE
        request.actor_info.client_key = 'Morai_Example'
        request.decision_range = 1
        request.position.x = 87.33
        request.position.y = 1190.58
        request.position.z = 0

        try:
            response = self.adaptor._actor_stub.SetVehicleDestination(request)
            print(f'SetVehicleDestination Response : {response.description}')
        except Exception as e :
            print(f'SetVehicleDestination Error : {e}')



        
    def SetVehiclePosition(self):
        """
        Ego 차량 위치 Setting        
        """
        from proto.morai.common.enum_pb2 import ObjectType        
        from proto.morai.actor.actor_set_pb2 import SetTransformParam
        request = SetTransformParam()
        request.actor_info.id.value = 'Ego'
        request.actor_info.object_type = ObjectType.OBJECT_TYPE_VEHICLE
        request.actor_info.client_key = 'Morai_Example'
        request.transform.location.x = 28.22
        request.transform.location.y = 1117.90
        request.transform.location.z = 0.79
        request.transform.rotation.x = 0.78
        request.transform.rotation.y = 1.351
        request.transform.rotation.z = 3.320

        try:
            response = self.adaptor._actor_stub.SetTransform(request)
            print(f'SetVehiclePosition Response : {response.description}')
        except Exception as e :
            print(f'SetVehiclePosition Error : {e}')
        



    def SetVehicleControlMode(self):
        from proto.morai.actor.actor_set_pb2 import VehicleControlModeParam
        from proto.morai.actor.actor_enum_pb2 import VehicleControlMode
        from proto.morai.common.enum_pb2 import ObjectType
        """
        Ego 차량의 ControlMode 선택.
        request mode 
        VehicleControlMode.VEHICLE_CONTROL_KEYBOARD = 키보드 제어
        VehicleControlMode.VEHICLE_CONTROL_AUTO_MODE = 외부 제어(알고리즘)
        VehicleControlMode.VEHICLE_CONTROL_CRUISE_MODE = MORAI 내부 제어
        """
        
        request = VehicleControlModeParam()
        request.actor_info.id.value = 'Ego'
        request.actor_info.object_type = ObjectType.OBJECT_TYPE_VEHICLE
        request.actor_info.client_key = 'Morai_Example'
        request.mode = VehicleControlMode.VEHICLE_CONTROL_CRUISE_MODE

        try:
            response = self.adaptor._actor_stub.SetVehicleControlMode(request)
            print(f'SetVehicleControlMode Response : {response.description}')
        except Exception as e :
            print(f'SetVehicleControlMode Error : {e}')
        
        


    def SetVehicleVelocity(self):
        """
        Ego 차량 Velocity setting
        request.velocity에 원하는 값(km/h)을 입력한다.
        """
        from proto.morai.actor.actor_set_pb2 import SetVelocityParam
        from proto.morai.common.enum_pb2 import ObjectType
        request = SetVelocityParam()    
        request.actor_info.id.value = 'Ego'
        request.actor_info.object_type = ObjectType.OBJECT_TYPE_VEHICLE
        request.actor_info.client_key = 'Morai_Example'
        request.velocity = 0  #km/h
        try:
            response = self.adaptor._actor_stub.SetVelocity(request)
            print(f'SetVehicleVelocity Response : {response.description}')
        except Exception as e :
            print(f'SetVehicleVelocity Error : {e}')    
    



    def GetEgoState(self):
        from proto.morai.common.object_info_pb2 import ObjectInfo
        from proto.morai.common.enum_pb2 import ObjectType
        """
        Ego 차량의 상태 조회.
        request.id.value = 'Ego'
        request.object_type = ObjectType.OBJECT_TYPE_VEHICLE
        
        Sur-2 차량 상태 조회 
        request.id.value = '2'
        request.object_type = ObjectType.OBJECT_TYPE_VEHICLE

        Obj-3 장애물 상태 조회
        request.id.value = '3'
        request.object_type = ObjectType.OBJECT_TYPE_OBSTACLE

        Ped-4 사람 상태 조회
        request.id.value = '4'
        request.object_type = ObjectType.OBJECT_TYPE_PEDESTRIAN
        """
        request = ObjectInfo()    
        request.id.value = 'Ego'
        request.object_type = ObjectType.OBJECT_TYPE_VEHICLE
        request.client_key = 'Morai_Example'
        
        try:
            response = self.adaptor._actor_stub.GetActorState(request)
            print(f'GetEgoState : {response}')
        except Exception as e :
            print(f'GetEgoState Error : {e}')    


    def SetAddSensor(self):
        from proto.morai.sensor.add_sensor_param_pb2 import AddSensorParam
        """
        SetAddSensor는 이미 센서가 설치되어 있으면 다음 index로 새로운 센서가 배치된다.
        계속해서 해당 def 호출된다면 많은 센서가 배치되어서 Simulator 성능저하가 발생함.
        """        
        request = AddSensorParam()
        request.vehicle_id.id.value = "Ego"
        request.vehicle_id.object_type = 1
        request.vehicle_id.client_key = 'Morai_Example'
        request.sensor_type = 1
        request.transform.location.x = 2.2
        request.transform.location.y = 0
        request.transform.location.z = 1.1
        request.transform.rotation.x = 0
        request.transform.rotation.y = 0
        request.transform.rotation.z = 0        
        try:
            response = self.adaptor._sensor_stub.AddSensor(request)
            print(f'SetAddSensor : {response}')
        except Exception as e :
            print(f'SetAddSensor Error : {e}')    


    def SetLoadMoraiScenario(self):
        from proto.morai.common.type_pb2 import StringValue
        request = StringValue()
        request.value = 'test'

        try:
            response = self.adaptor._scenario_stub.LoadMoraiScenario(request)
            print(f'SetLoadMoraiScenario : {response}')
        except Exception as e :
            print(f'SetLoadMoraiScenario Error : {e}')    

        
if __name__ == '__main__':

    example = MORAI_gRPC()    
    example.main()
