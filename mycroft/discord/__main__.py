from mycroft.util.log import LOG
from mycroft.util import (
    check_for_signal,
    reset_sigint_handler,
    start_message_bus_client,
    wait_for_exit_signal
)
import mycroft.discord.discordservice as discordservice
from mycroft.util.process_utils import ProcessStatus, StatusCallbackMap


def on_ready():
    LOG.info('Discord service is ready.')


def on_error(e='Unknown'):
    LOG.error('Discord service failed to launch ({}).'.format(repr(e)))


def on_stopping():
    LOG.info('Discord service is shutting down...')


def main(ready_hook=on_ready, error_hook=on_error, stopping_hook=on_stopping):
    """Start the Discord Service and connect to the Message Bus"""
    LOG.info("Starting Discord Service")
    try:
        reset_sigint_handler()
        whitelist = ['mycroft.discord.service']
        bus = start_message_bus_client("DISCORD", whitelist=whitelist)
        callbacks = StatusCallbackMap(on_ready=ready_hook, on_error=error_hook,
                                      on_stopping=stopping_hook)
        status = ProcessStatus('discord', bus, callbacks)

        discordservice.init(bus)
        status.set_started()
    except Exception as e:
        status.set_error(e)
    else:
        status.set_ready()
        wait_for_exit_signal()
        status.set_stopping()


if __name__ == '__main__':
    main()
