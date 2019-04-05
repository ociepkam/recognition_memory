from psychopy import visual, event, logging, clock
import codecs
import os


def read_text_from_file(file_name, insert=''):
    """
    Method that read message from text file, and optionally add some
    dynamically generated info.
    :param file_name: Name of file to read
    :param insert: dynamically generated info
    :return: message
    """
    if not isinstance(file_name, str):
        raise TypeError('file_name must be a string')
    msg = list()
    with codecs.open(file_name, encoding='utf-8', mode='r') as data_file:
        for line in data_file:
            if not line.startswith('#'):  # if not commented line
                if line.startswith('<--insert-->'):
                    if insert:
                        msg.append(insert)
                else:
                    msg.append(line)
    return ''.join(msg)


def show_info(win, file_name, text_size, screen_width, insert='', show_time=999999):
    """
    Clear way to show info message into screen.
    :param name: part name
    :param data: beh data
    :param win:
    :param file_name:
    :param screen_width:
    :param text_size:
    :param insert: extra text for read_text_from_file
    :return:
    """
    hello_msg = read_text_from_file(os.path.join(file_name), insert=insert)
    hello_msg = visual.TextStim(win=win, antialias=True, font=u'Arial',
                                text=hello_msg, height=text_size,
                                wrapWidth=screen_width, color=u'black',
                                alignHoriz='center', alignVert='center')
    hello_msg.draw()
    timer = clock.Clock()
    win.callOnFlip(timer.reset)
    event.clearEvents()
    win.flip()

    while timer.getTime() < show_time:
        event.clearEvents(eventType='mouse')
        key = event.getKeys()
        if key in [['q'], ['return'], ['space']]:
            if key == ['q']:
                logging.critical('Experiment finished by user! {} pressed.'.format(key[0]))
                exit(0)
            break
    win.flip()


def show_image(win, file_name, size):
    image = visual.ImageStim(win=win, image=os.path.join('images', file_name), interpolate=True, size=size)
    image.draw()
    win.flip()
    key = event.waitKeys(keyList=['q', 'return', 'space'])
    if key == ['q']:
        logging.critical('Experiment finished by user! {} pressed.'.format(key[0]))
        exit(0)
    win.flip()
