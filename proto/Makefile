.PHONY: all clean

PROTO_FILES := common.proto core.proto ai.proto gateway.proto pdf.proto

all:
	../scripts/generate-proto.sh

clean:
	rm -f *_pb2.py *_pb2_grpc.py *_pb2.pyi
