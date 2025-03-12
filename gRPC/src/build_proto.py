import os, sys
import subprocess
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(current_path, '..'))

class ProtoBuilder:
    def build(self, proto_path, output_path):
        subdirs = self._get_subdirectories(proto_path)
        for subdir in subdirs:
            real_proto_path = os.path.normpath(os.path.join(proto_path, subdir))
            self._build_core(proto_path, real_proto_path, output_path)
        

    def _get_subdirectories(self, root_path):
        subdirs = []
        for file in os.listdir(root_path):
            d = os.path.join(root_path, file)
            if os.path.isdir(d):
                subdirs.append(file)
                temp_subs = self._get_subdirectories(d)
                for temp_sub in temp_subs:
                    subdirs.append(f'{file}/{temp_sub}')

        return subdirs


    def _build_core(self, proto_root_path, proto_path, output_path):
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        args = f'-I{proto_root_path} --python_out={output_path} --grpc_python_out={output_path} {proto_path}/*.proto'
        command = f'python -m grpc_tools.protoc {args}'
        print(command)
        result = subprocess.call(command, shell=True)

        print(f'result code {result}')
    

if __name__ == '__main__':
    proto_path = os.path.normpath(os.path.join(current_path, '../morai_standard_proto'))
    protoc_path = os.path.normpath(os.path.join(current_path, 'proto'))
    
    builder = ProtoBuilder()
    builder.build(proto_path, protoc_path)