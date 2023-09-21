import logging
import time
from dataclasses import dataclass
import socket

import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_tcp

import config


@dataclass
class MapItem2:
    address: int
    length: int
    names: list[str]
    format: str = '>f'


@dataclass
class MapItem:
    address: int
    id: str
    name: str
    format: str = '>h'
    k: float = 1.0


class DataValue:

    def __init__(self, id, name, data_format, k):
        self.id = id
        self.name = name
        self.dt = 0
        self.value = ''
        self.format = data_format
        self.k = k

    def set_value(self, value):
        self.dt = time.time()
        self.value = self.repr_value(value)

    def repr_value(self, value):
        if self.k != 1:
            after_dot = len(str(int(1 / self.k))) - 1
            value = round(value * self.k, after_dot)
        return str(value)

    def serialize(self):
        return {
            'name': self.name,
            'value': self.value,
            'status': 1 if time.time() - self.dt < 2.0 else 0
        }


@dataclass
class MbMapItem:
    items: list[MapItem]
    start_addr: int
    quantity: int
    data_format: str


class DataHolder:

    def __init__(self, host: str, mb_map: list[MbMapItem], logger):
        try:
            self.host = host.split(':')[0]
            self.port = int(host.split(':')[1])
        except IndexError:
            self.host = host
            self.port = 502
        self.logger = logger
        self.last_update = 0
        self.min_period = 0.5
        self.mb_master = None
        self.data = {}
        self.mb_map = self.map_init(mb_map)
        self.mb_init()

    def mb_init(self):
        self.logger.debug('mb_init')
        self.mb_master = modbus_tcp.TcpMaster(host=self.host, port=self.port, timeout_in_sec=0.5)

    def map_init(self, mb_map):
        for m in mb_map:
            for i in m.items:
                self.data[i.id] = DataValue(id=i.id, name=i.name, data_format=i.format, k=i.k)
        return mb_map

    def update(self):
        self.logger.debug('start')
        if self.last_update + self.min_period > time.time():
            return
        for m in self.mb_map:
            try:
                data = self.mb_master.execute(1, cst.READ_INPUT_REGISTERS, m.start_addr, m.quantity, m.data_format)
                self.logger.debug(data)
            except socket.timeout:
                self.logger.error('socket timeout')
            except Exception:
                self.logger.exception('')
            else:
                for item in m.items:
                    try:
                        value = data[item.address - m.start_addr]
                        self.data[item.id].set_value(value)
                    except Exception:
                        self.logger.exception('')
        self.last_update = time.time()
        msg = []
        for m in self.data.values():
            msg.append(f'{m.id}={m.value}')
        self.logger.debug(f'end {",".join(msg)}')

    def get_data(self):
        data = []
        for d in self.data.values():
            data.append(d.serialize())
        return data


def init_service():
    logger = modbus_tk.utils.create_logger("console", level=logging.DEBUG)
    data_holders = {}
    server_name = '1'
    mb_map = [
        MbMapItem(
            items=[
                MapItem(address=1, name='Счетчик', id='counter', format='>H')
            ],
            quantity=1,
            start_addr=1,
            data_format='>H'),
        MbMapItem(
            items=[
                MapItem(address=154, name='Экструдер', id='extruder', format='>h', k=0.1),
                MapItem(address=165, name='Протяжка', id='pulling', format='>h', k=0.1),
                MapItem(address=175, name='Т1', id='t1', format='>h', k=0.1),
            ],
            quantity=175 - 154 + 2,
            start_addr=154,
            data_format='>' + 'h' * (175 - 154 + 2)),
        MbMapItem(
            items=[
                MapItem(address=112, name='Т2', id='t2', format='>h', k=0.1),
                MapItem(address=102, name='Т3', id='t3', format='>h', k=0.1),
                MapItem(address=92, name='Т4', id='t4', format='>h', k=0.1),
                MapItem(address=82, name='Т5', id='t5', format='>h', k=0.1),
                MapItem(address=72, name='Т6', id='t6', format='>h', k=0.1),
                MapItem(address=62, name='Т7', id='t7', format='>h', k=0.1),
                MapItem(address=52, name='Т8', id='t8', format='>h', k=0.1),
                MapItem(address=42, name='Т9', id='t9', format='>h', k=0.1),
                MapItem(address=32, name='Т10', id='t10', format='>h', k=0.1),
                MapItem(address=22, name='Т11', id='t11', format='>h', k=0.1),
                MapItem(address=12, name='Т12', id='t12', format='>h', k=0.1),
            ],
            quantity=112 - 12 + 2,
            start_addr=12,
            data_format='>' + 'h' * (112 - 12 + 2))
    ]
    dh = DataHolder(host=config.LINE1_HOST, mb_map=mb_map, logger=logging.getLogger(f'service.server_{server_name}'))
    data_holders[server_name] = dh

    server_name = '2'
    dh = DataHolder(host=config.LINE2_HOST, mb_map=mb_map, logger=logging.getLogger(f'service.server_{server_name}'))
    data_holders[server_name] = dh

    # server_name = '3'
    # dh = DataHolder(host='192.168.0.16:5204', mb_map=mb_map, logger=logging.getLogger(f'service.server_{server_name}'))
    # data_holders[server_name] = dh
    return data_holders
