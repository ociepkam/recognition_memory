from psychopy import event, logging


def check_exit(key='q'):
    stop = event.getKeys(keyList=[key])
    if len(stop) > 0:
        logging.critical('Experiment finished by user! {} pressed.'.format(key))
        exit(1)
