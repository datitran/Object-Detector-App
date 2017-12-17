"""
Module interprets agent commands and dispatches an action


How to extend NLP commands:

1. Import: `from nlp.dispatch import Dispatchable, dispatcher`
2. Subclass `Dispatchable`, implementing the action in `__call__`. Call takes in a python dictionary (the `payload`)
3. Expand the `displatcher` with a command: `dispatcher['<command>'] = <Subclass of Dispatchable>`
"""

import json
import os
import typing

import paho.mqtt.client as mqtt
USER_ID = 1234
EXPLORER_SUB_TOPIC = 'dev/chloe/explorer/{}/statement'.format(USER_ID)
AGENT_TOPIC = 'dev/chloe/agent/{}/response'.format(USER_ID)
# EXPLORER_PUB_TOPIC = 'dev/chloe/explorer/{}/response'.format(USER_ID)


# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("Connection to client! rc: " + str(rc))


def on_publish(client, obj, mid):
    print("Publishing AI Response mid: " + str(mid))


def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(client, obj, level, string):
    print(string)


def on_message(client, obj, msg):
    try:
        json_string = str(msg.payload, 'utf-8')
        print('On msg: ' + json_string)
        payload = json.loads(json_string)
    except json.decoder.JSONDecodeError:
        return

    cmd = payload.get('command', 'default').lower(),

    action = interp_command(cmd, list(dispatcher.keys()))

    print('calling ' + action)
    dispatcher[action](payload)


mqttc = mqtt.Client()


# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# mqttc.on_log = on_log


url_str = os.environ.get('AIRAMQTT_URL', 'preprod-mqtt.aira.io')
port = int(os.environ.get('AIRAMQTT_PORT', '1883'))


mqttc.connect(url_str, port, 60)
mqttc.subscribe(EXPLORER_SUB_TOPIC, 0)


def interp_command(cmd_str: str, actions: typing.List[str]) -> str:
    """Output a discrete action to take from a user command in natural language.

    Args:
        cmd_str: user command
        actions: list of commands available from dispatcher

    Returns:
        str: single command for dispatcher to execute

    Examples:
        >>> interp_command('describe what is around me', ['describe','count'])
        'describe'
        >>> interp_command('count the number of objects in view', ['describe', 'count'])
        'count'
    """

    # faster, but less readable
    # return next((axn for axn in actions if axn in cmd_str), 'default')

    for axn in actions:
        if axn in cmd_str:
            return axn
    return 'default'


class Dispatchable:
    client = mqttc
    root_topic = AGENT_TOPIC

    def send(self, payload: typing.Dict, *, subtopic: typing.List[str] = list()):
        payload_json = json.dumps(payload)
        if not subtopic:
            self.client.publish(self.root_topic, payload=payload_json)
        else:
            self.client.publish(self.root_topic + '/' + '/'.join(subtopic),
                                payload=payload_json)


class Echo(Dispatchable):
    def __call__(self, msg):
        self.send(json.dumps(msg))


class NoOp(Dispatchable):
    def __call__(self, msg):
        pass


dispatcher = {
    'default': NoOp(),
    'debug': Echo(),
}


def _test_mqtt_loop():
    rc = 0
    while rc == 0:
        rc = mqttc.loop()
    print('rc: ' + str(rc))


if __name__ == '__main__':
    _test_mqtt_loop()
