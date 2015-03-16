#!/usr/bin/python
#
#
#

import sys
from conf.redis_config import redis_client, redis_pubsub_channel


def publish(message):
    redis_client.publish(redis_pubsub_channel, message)
    


if __name__ == '__main__':
    message = sys.argv[1]

    publish(message)
