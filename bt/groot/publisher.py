"""Minimal Groot2 monitor protocol over ZeroMQ.

Implements the publisher side of the Groot2 wire protocol so the Python
behaviour tree running in py-trees can be observed live in Groot2.

Wire-protocol reference: BehaviorTree.CPP
  include/behaviortree_cpp/loggers/groot2_protocol.h
  src/loggers/groot2_publisher.cpp
"""
import struct
import threading
import uuid
from typing import Dict, Optional

import py_trees as pt
import zmq
from py_trees.behaviour import Behaviour

PROTOCOL_ID = 2

REQ_FULLTREE = ord("T")
REQ_STATUS = ord("S")
REQ_BLACKBOARD = ord("B")
REQ_REMOVE_ALL_HOOKS = ord("A")
REQ_DISABLE_ALL_HOOKS = ord("X")

STATUS_IDLE = 0
STATUS_RUNNING = 1
STATUS_SUCCESS = 2
STATUS_FAILURE = 3
STATUS_SKIPPED = 4

_PT_TO_GROOT = {
    pt.common.Status.INVALID: STATUS_IDLE,
    pt.common.Status.RUNNING: STATUS_RUNNING,
    pt.common.Status.SUCCESS: STATUS_SUCCESS,
    pt.common.Status.FAILURE: STATUS_FAILURE,
}


def _request_header(req_type: int, request_id: int) -> bytes:
    return struct.pack("<BBI", PROTOCOL_ID, req_type, request_id)


def _reply_header(req_type: int, request_id: int, tree_uuid: bytes) -> bytes:
    if len(tree_uuid) != 16:
        raise ValueError("tree_uuid must be exactly 16 bytes")
    return struct.pack("<BBI", PROTOCOL_ID, req_type, request_id) + tree_uuid


def _parse_request_header(buf: bytes):
    if len(buf) < 6:
        return None
    protocol, req_type, request_id = struct.unpack("<BBI", buf[:6])
    return protocol, req_type, request_id


class Groot2Publisher:
    """Run a Groot2 monitor endpoint for a py-trees tree.

    `uid_table` maps the Groot2 node UID (uint16) to the py-trees Behaviour.
    `tree_xml` is the original BT.CPP-style XML string used to author the tree;
    it is returned verbatim to FULLTREE requests so Groot2 renders the same
    layout the user designed.
    """

    def __init__(self, tree_xml: str, uid_table: Dict[int, Behaviour], port: int = 1667):
        self.tree_xml = tree_xml
        self.uid_table = uid_table
        self.server_port = port
        self.publisher_port = port + 1
        self.tree_uuid = uuid.uuid4().bytes

        self._ctx = zmq.Context.instance()
        self._server: Optional[zmq.Socket] = None
        self._publisher: Optional[zmq.Socket] = None

        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._status_lock = threading.Lock()

    def start(self) -> None:
        self._server = self._ctx.socket(zmq.REP)
        self._server.bind(f"tcp://*:{self.server_port}")
        self._publisher = self._ctx.socket(zmq.PUB)
        self._publisher.bind(f"tcp://*:{self.publisher_port}")
        self._thread = threading.Thread(target=self._serve, name="Groot2Publisher", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._server is not None:
            self._server.close(linger=0)
        if self._publisher is not None:
            self._publisher.close(linger=0)

    def _serve(self) -> None:
        poller = zmq.Poller()
        poller.register(self._server, zmq.POLLIN)
        while not self._stop.is_set():
            try:
                events = dict(poller.poll(timeout=100))
            except zmq.error.ZMQError:
                return
            if self._server in events:
                try:
                    frames = self._server.recv_multipart()
                except zmq.error.ZMQError:
                    return
                reply = self._handle(frames)
                try:
                    self._server.send_multipart(reply)
                except zmq.error.ZMQError:
                    return

    def _handle(self, frames):
        if not frames:
            return [b""]
        parsed = _parse_request_header(frames[0])
        if parsed is None:
            return [b""]
        protocol, req_type, request_id = parsed
        if protocol != PROTOCOL_ID:
            return [_reply_header(req_type, request_id, self.tree_uuid), b""]

        header = _reply_header(req_type, request_id, self.tree_uuid)
        if req_type == REQ_FULLTREE:
            return [header, self.tree_xml.encode("utf-8")]
        if req_type == REQ_STATUS:
            return [header, self._status_buffer()]
        if req_type == REQ_BLACKBOARD:
            return [header, b""]
        if req_type in (REQ_REMOVE_ALL_HOOKS, REQ_DISABLE_ALL_HOOKS):
            return [header, b""]
        return [header, b""]

    def _status_buffer(self) -> bytes:
        with self._status_lock:
            buf = bytearray()
            for uid, node in self.uid_table.items():
                if uid < 0 or uid > 0xFFFF:
                    continue
                status_byte = _PT_TO_GROOT.get(node.status, STATUS_IDLE)
                buf += struct.pack("<HB", uid, status_byte)
            return bytes(buf)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()
