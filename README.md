# MORAI - Network Module example (UDP)

This is an example of sending and receiving UDP data in `MORAI SIM: Drive`  
For more details, please refer to the MORAI manual.  
Link : https://help-morai-sim.scrollhelp.site/

```
├── lib                
│    ├── define          # UDP network - Protocol configure
│    └── network         # UDP network manager class│    
│
├── EgoNetwork           
│    ├── CmdControl      # Ego Vehicle Control Command
│    ├── Publisher       # UDP Protocol received from the MOARI SIM related to Ego
│    └── Subscriber      # UDP Protocol send to the MOARI SIM related to Ego
│
├── Sensor              
│
└── Etc

```

# Requirement

- python >= 3.7


# 카메라 영상 보기
## Setup
```
pip install opencv-python
```

## Runninng
```
python ./Sensor/Camera.py
```

# Cmd 보내기
## Setup
```
- 요기 들어가기 ./EgoNetwork/CmdControl/MoraiCmdController.py
- IP에 시뮬레이터 ip 넣기
- port에 시뮬레이터에 보이는 Host PORT 넣기
- 저장하기
```

## Runninng
```
python ./EgoNetwork/CmdControl/MoraiCmdController.py
```