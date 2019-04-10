import atexit
from psychopy import visual, event, core, logging
import time
import random
from numpy.random import shuffle

from os.path import join
import csv

from sources.experiment_info import experiment_info
from sources.load_data import load_config, prepare_words
from sources.screen import get_screen_res, get_frame_rate
from sources.show_info import show_info
from sources.check_exit import check_exit
from sources.ophthalmic_procedure import ophthalmic_procedure
from sources.triggers import send_trigger, create_eeg_port, TriggerTypes, prepare_trigger


part_id, part_sex, part_age, experiment_version, date = experiment_info()
NAME = "{}_{}_{}_{}".format(experiment_version, part_id, part_sex, part_age)

RESULTS = list()
RESULTS.append(['TRIAL_NR', 'NAWL_NR', 'WORD', 'WORD_EMO', 'WORD_LIST', 'WORD_TYPE', 'ANSWER', 'ACC', 'RT'])

TRIGGERS_LIST = []
TRIGGER_NO = 0

RAND = str(random.randint(100, 999))

logging.LogFile(join('.', 'results', 'logging', NAME + '_' + RAND + '.log'), level=logging.INFO)


@atexit.register
def save_beh():
    logging.flush()
    with open(join('results', 'behavioral_data', 'beh_{}_{}.csv'.format(NAME, RAND)), 'w') as csvfile:
        beh_writer = csv.writer(csvfile)
        beh_writer.writerows(RESULTS)
    data = [row[0] + ':' + row[1] + '\n' for row in TRIGGERS_LIST]
    with open(join('results', 'triggers_maps', 'triggerMap_{}_{}.txt'.format(NAME, RAND)), 'w') as mapFile:
        for row in data:
            mapFile.writelines(row)


def run(words):
    global RESULTS, TRIGGER_NO, TRIGGERS_LIST, PORT_EEG
    for idx, word in enumerate(words):
        word_stim = visual.TextStim(win=win, text=word[1], antialias=True, font=u'Arial', height=config['WORD_SIZE'],
                                    wrapWidth=win.size[0], color=u'black', alignHoriz='center', alignVert='center',
                                    pos=config["WORD_POS"])

        trigger_name = "_{}_{}_{}_{}".format("new" if word[3]!=experiment_version else "exp", word[3], word[2], word[1])
        TRIGGER_NO, TRIGGERS_LIST = prepare_trigger(trigger_type=TriggerTypes.WORD, trigger_no=TRIGGER_NO,
                                                    triggers_list=TRIGGERS_LIST, trigger_name=trigger_name)

        answer = None
        rt = -1
        acc = None

        fixation.setAutoDraw(True)
        win.flip()
        time.sleep(config["FIX_TIME"])
        fixation.setAutoDraw(False)
        win.flip()
        time.sleep(config["WAIT_AFTER_FIX"])

        win.callOnFlip(response_clock.reset)
        event.clearEvents()

        word_stim.setAutoDraw(True)
        ans_1.setAutoDraw(True)
        ans_2.setAutoDraw(True)
        question.setAutoDraw(True)
        win.flip()

        send_trigger(port_eeg=PORT_EEG, trigger_no=TRIGGER_NO, send_eeg_triggers=config['EEG_TRIGGERS'])

        while response_clock.getTime() < config["STIM_TIME"]:
            key = event.getKeys(config["KEYS"])
            if key:
                rt = response_clock.getTime()
                send_trigger(port_eeg=PORT_EEG, trigger_no=TRIGGER_NO, send_eeg_triggers=config['EEG_TRIGGERS'])
                TRIGGER_NO, TRIGGERS_LIST = prepare_trigger(trigger_type=TriggerTypes.WORD, trigger_no=TRIGGER_NO,
                                                            triggers_list=TRIGGERS_LIST, trigger_name=trigger_name)
                answer = key[0]
                acc = word[4] == answers_order[config["KEYS"].index(answer)]
                break
            check_exit()
            if response_clock.getTime() > config["SHOW_CLOCK"]:
                clock_image.setAutoDraw(True)
                win.flip()

        word_stim.setAutoDraw(False)
        ans_1.setAutoDraw(False)
        ans_2.setAutoDraw(False)
        clock_image.setAutoDraw(False)
        question.setAutoDraw(False)
        win.flip()

        # ['TRIAL_NR', 'NAWL_NR', 'WORD', 'WORD_EMO', 'WORD_LIST', 'WORD_TYPE', 'ANSWER', 'ACC', 'RT']
        result = [idx + 1, word[0], word[1], word[2], word[3], word[4], answer, acc, rt]
        RESULTS.append(result)
        time.sleep(config["WAIT_TIME"])


config = load_config()

if config['EEG_TRIGGERS']:
    PORT_EEG = create_eeg_port()
else:
    PORT_EEG = None

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

question = visual.TextStim(win=win, text=config["QUESTION"], antialias=True, font=u'Arial',
                           height=config['QUESTION_SIZE'], wrapWidth=win.size[0], color=u'black', alignHoriz='center',
                           alignVert='center', pos=config["QUESTION_POS"])

fixation = visual.TextStim(win, color='black', text=config['FIX'], height=config['FIX_SIZE'])

mouse = event.Mouse()
mouse.setVisible(False)

response_clock = core.Clock()
trial_nr = 1

exp_words, train_words = prepare_words("Words.csv", experiment_version)

screen_res = {"width": SCREEN_RES[0], "height": SCREEN_RES[1]}
TRIGGER_NO, TRIGGERS_LIST = ophthalmic_procedure(win, screen_res, FRAMES_PER_SEC, TRIGGER_NO, TRIGGERS_LIST,
                                                 config["TEXT_SIZE"], send_eeg_triggers=config["EEG_TRIGGERS"])

# TRAINING
show_info(win, join('.', 'messages', "training.txt"), text_size=config['TEXT_SIZE'], screen_width=SCREEN_RES[0])
run(words=train_words[:config["TRAIN_TRIALS"]])


# EXPERIMENT
show_info(win, join('.', 'messages', "instruction.txt"), text_size=config['TEXT_SIZE'], screen_width=SCREEN_RES[0])
run(words=exp_words)


# END
show_info(win, join('.', 'messages', "end.txt"), text_size=config['TEXT_SIZE'], screen_width=SCREEN_RES[0])
