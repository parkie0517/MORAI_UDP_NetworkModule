# gRPC example-py

## Description
This repository contains a Python demo of a gRPC client. It demonstrates how to use gRPC for communication between a client and a server using Protocol Buffers (protobufs) for data serialization.


## Usage
### 1. Ready the SIM
You have to set MORAI Simulator as a server for this client example.

After log-in, you'll enter into map and vehicle select mode.


### 2. Build the Proto
Navigate to the src directory where the files are located, and build the Protocol Buffer files:

```
cd src
python ./build_proto.py
```
This script compiles the .proto files into Python code, which is necessary for the gRPC communication.


### 3. Run the Example Code
After building the proto files, you can run the example gRPC client:

```
python ./HMG_Example.py
```