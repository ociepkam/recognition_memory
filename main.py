import atexit
from psychopy import visual, event, core, logging
import time
from numpy.random import shuffle

from os.path import join
import csv

from sources.experiment_info import experiment_info
from sources.load_data import load_config, prepare_words
from sources.screen import get_screen_res, get_frame_rate
from sources.show_info import show_info
from sources.check_exit import check_exit


part_id, part_sex, part_age, date = experiment_info()
NAME = "{}_{}_{}".format(part_id, part_sex, part_age)

RESULTS = list()
RESULTS.append(['TRIAL_NR', 'WORD', 'WORD_TYPE', 'ANSWER', 'ACC', 'RT'])

RAND = "" #str(random.randint(100, 999))

logging.LogFile(join('.', 'results', 'logging', NAME + '_' + RAND + '.log'), level=logging.INFO)


@atexit.register
def save_beh():
    logging.flush()
    with open(join('results', 'behavioral_data', 'beh_{}_{}.csv'.format(NAME, RAND)), 'w') as csvfile:
        beh_writer = csv.writer(csvfile)
        beh_writer.writerows(RESULTS)


config = load_config()

SCREEN_RES = get_screen_res()
win = visual.Window(SCREEN_RES, fullscr=True, monitor='testMonitor', units='pix',
                    screen=0, color=config["BACKGROUND_COLOR"], winType='pygame')
FRAMES_PER_SEC = get_frame_rate(win)

clock_image = visual.ImageStim(win=win, image=join('images', 'clock.png'), interpolate=True,
                               size=config['CLOCK_SIZE'], pos=config['CLOCK_POS'])


answers_order = ["exp", "new"]
shuffle(answers_order)

ans_1 = visual.TextStim(win=win, text=config["ANS_TEXT"][answers_order[0]], antialias=True, font=u'Arial',
                        height=config['ANS_SIZE'], wrapWidth=win.size[0], color=u'black', alignHoriz='center',
                        alignVert='center', pos=config["ANS1_POS"])

ans_2 = visual.TextStim(win=win, text=config["ANS_TEXT"][answers_order[1]], antialias=True, font=u'Arial',
                        height=config['ANS_SIZE'], wrapWidth=win.size[0], color=u'black', alignHoriz='center',
                        alignVert='center', pos=config["ANS2_POS"])

mouse = event.Mouse()
mouse.setVisible(False)

response_clock = core.Clock()
trial_nr = 1

words = prepare_words("words_sst.txt", "words_new.txt")

# EXPERIMENT
show_info(win, join('.', 'messages', "instruction.txt"), text_size=config['TEXT_SIZE'], screen_width=SCREEN_RES[0])


for idx, word in enumerate(words):

    word_stim = visual.TextStim(win=win, text=word[0], antialias=True, font=u'Arial', height=config['WORD_SIZE'],
                                        wrapWidth=win.size[0], color=u'black', alignHoriz='center', alignVert='center',
                                        pos=config["WORD_POS"])
    clock_is_shown = False
    answer = None
    rt = -1
    acc = None

    win.callOnFlip(response_clock.reset)
    event.clearEvents()

    word_stim.setAutoDraw(True)
    ans_1.setAutoDraw(True)
    ans_2.setAutoDraw(True)
    win.flip()

    while response_clock.getTime() < config["STIM_TIME"]:
        key = event.getKeys(config["KEYS"])
        if key:
            answer = key[0]
            rt = response_clock.getTime()
            acc = word[1] == answers_order[config["KEYS"].index(answer)]
            break
        check_exit()

    word_stim.setAutoDraw(False)
    ans_1.setAutoDraw(False)
    ans_2.setAutoDraw(False)
    win.flip()

    result = [idx + 1, word[0], word[1], answer, acc, rt]
    RESULTS.append(result)
    time.sleep(config["WAIT_TIME"])

show_info(win, join('.', 'messages', "end.txt"), text_size=config['TEXT_SIZE'], screen_width=SCREEN_RES[0])
