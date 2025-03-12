from lib.common.compress_util import decompress
from proto.morai.common.type_pb2 import StringValue
from proto.morai.map.get_neighbor_link_param_pb2 import GetNeighborLinkParam
from proto.morai.map.link_info_pb2 import LinkInfo
from proto.morai.map.map_enum_pb2 import NeighborLinkType

import json


class Map:
    def __init__(self, sim_adapter, map_name=None):
        # MGeo Data Dic
        self.mgeo_data = dict()

        self._sim_adapter = sim_adapter        
        if map_name != None:
            self.get_mgeo_data(map_name)


    def get_mgeo_data(self, map_name):
        param = StringValue()
        param.value = map_name

        compressed_mgeo = self._sim_adapter.get_mgeo(param)
        try:
            for mgeo_obj in compressed_mgeo.objects :
                file_name = mgeo_obj.filename
                comp_data = mgeo_obj.compressed_data
                self.mgeo_data[file_name] = decompress(comp_data) 
        except AttributeError as e:
            print(e)

    
    def get_neighbor_link(self, neighbor_link_type, link_id):
        param = GetNeighborLinkParam()
        param.type = neighbor_link_type
        param.target_link_id.value = link_id
        
        return self.simulation_world._sim_adapter.get_neighbor_link(param)


    def get_vehicles_on_link(self, link_id):
        param = LinkInfo()
        param.id.value = link_id
        param.waypoint_idx = 0

        return self.simulation_world._sim_adapter.get_vehicles_on_link(param)