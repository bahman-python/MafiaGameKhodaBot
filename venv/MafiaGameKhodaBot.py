# testing git
# this is a bot I have developed, only for playing Mafia game together with my friends.

import telegtoken
import logging
import json
import os.path
import datetime
import csv
from random import seed
from random import randint
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)

# OBS! Two things
# (1) A directory called textfiles should exist next to this Python file so that backup files are saved there.
# if it does not exist there, an error will occurr.
# (2) Store your telegram bot token in a separate file called telegtoken.py in the same directory as this file
# write the following in there:
#def get_telegram_token():
#    telegram_token = "TYPE YOUR TELEGRAM TOKEN HERE"
#    return telegram_token
#
# In telegram, you should make a bot and get a token for it from BotFather.

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
players = ['example_player1_for_testing','example_player2_for_testing','example_player3_for_testing','example_player4_for_testing','example_player5_for_testing','example_player6_for_testing','example_player7_for_testing','example_player8_for_testing','example_player9_for_testing','example_player10_for_testing','example_player11_for_testing','example_player12_for_testing','example_player13_for_testing','example_player14_for_testing','example_player15_for_testing']
roles = []
roles_text = []
roles_are_assigned = False
num_mafias = 0
after1stnight_khoda = 'nobody... oh nobody...'
did_karagah_ask_first_time = True
door_to_join_open = False
backup_data_loaded = False

CHOOSING, TYPING_REPLY = range(2)

reply_keyboard = [['/start','print debug info'],
                  ['add me to game', 'set new khoda'],
                  ['remove all players', 'define new player'],
                  ['list all players', 'assign roles'],
                  ['what is my role', 'first night karagah ask'],
                  ['open the door to join','close the door to join'],
                  ['list all players and roles','done']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

def start(update, context):
    global backup_data_loaded
    if backup_data_loaded == False:
        read_status()
        backup_data_loaded = True
        update.message.reply_text('OBS! Backup is being restored!!!')

    update.message.reply_text(
        "hello. robots has just started now!!! please select your command:",
        reply_markup=markup)

    return CHOOSING

def made_a_choice(update, context):
    global players
    global after1stnight_khoda
    global roles_are_assigned
    global roles
    global roles_text
    global did_karagah_ask_first_time
    global door_to_join_open
    next_state = CHOOSING   #by default, for avoiding gettings stuck...
    text = update.message.text
    user_command = text
    user_id = update.message.from_user.name
    context.user_data["user_command"] = user_command
    is_admin = False

    if (user_id == '@bahman_canon'):
        is_admin = True

    #update.message.reply_text("started -- made_a_choice -- with input: " + text)

    if(user_command == 'remove all players'):
        if(is_admin == True):
            if(door_to_join_open == True):
                players = []
                roles = []
                roles_text = []
                roles_are_assigned = False
                after1stnight_khoda = 'nobody... oh nobody...'
                did_karagah_ask_first_time = True

                update.message.reply_text("now, i have cleaned up the list of players. the list is empty now")

                next_state = CHOOSING

                write_status() #backup status to disk to reload if crash
            else:
                update.message.reply_text("door to join should be OPEN in order to remove all players")
        else:
            update.message.reply_text("only admin can reset the player list...")
    elif (user_command == '/start'):
        update.message.reply_text("robot is up and running!")
        next_state = CHOOSING
    elif (user_command == 'print debug info'):
        if is_admin == False:
            update.message.reply_text("debug info not available...")
            next_state=CHOOSING
        else:
            update.message.reply_text("debug info:")
            update.message.reply_text("players=")
            update.message.reply_text(players)
            update.message.reply_text("roles=")
            update.message.reply_text(roles)
            update.message.reply_text("roles_text=")
            update.message.reply_text(roles_text)
            update.message.reply_text("roles_are_assigned=")
            update.message.reply_text(roles_are_assigned)
            update.message.reply_text("num_mafias=")
            update.message.reply_text(num_mafias)
            update.message.reply_text("after1stnight_khoda=")
            update.message.reply_text(after1stnight_khoda)
            update.message.reply_text("did_karagah_ask_first_time=")
            update.message.reply_text(did_karagah_ask_first_time)
            update.message.reply_text("door_to_join_open=")
            update.message.reply_text(door_to_join_open)


            next_state=CHOOSING
    elif (user_command == 'open the door to join'):
        if is_admin == True:
            door_to_join_open = True
            update.message.reply_text("the door to join is now OPEN!")
            next_state = CHOOSING

            write_status()  # backup status to disk to reload if crash
        else:
            update.message.reply_text("only admin can open the door")
            next_state = CHOOSING
    elif (user_command == 'close the door to join'):
        if is_admin == True:
            door_to_join_open = False
            update.message.reply_text("the door to join is now CLOSED!")
            next_state = CHOOSING

            write_status()  # backup status to disk to reload if crash
        else:
            update.message.reply_text("only admin can close the door")
            next_state = CHOOSING
    elif (user_command == 'first night karagah ask'):
        if(roles_are_assigned == True):
            if (user_id in players):
                index = players.index(user_id)
                player_role = roles[index]

                # 0 = not assigned yet
                # 1 = shahrvand / aadi
                # 2 = shahrvand / karagah
                # 3 = shahrvand / doctor
                # 4 = shahrvand / taktirandaz
                # 5 = mafia / aadi
                # 6 = mafia / raees mafia

                if(player_role == 2):
                    if(did_karagah_ask_first_time == False):
                        update.message.reply_text("ok, now listing all players:")
                        update.message.reply_text(players)

                        update.message.reply_text("please write the name of person you want to ask:")

                        next_state = TYPING_REPLY
                    else:
                        update.message.reply_text("you have already asked once! ;-) only once is allowed")
                        next_state = CHOOSING

                else:
                    update.message.reply_text("you are not karagah! only karagah can ask")
                    next_state = CHOOSING

            else:
                update.message.reply_text("you are not in players list!")
                next_state = CHOOSING
        else:
            update.message.reply_text("roles are not assigned yet. you are not karagah")
            next_state = CHOOSING


    elif (user_command == 'set new khoda'):
        if(is_admin == True):
            update.message.reply_text("ok, now listing all players:")
            update.message.reply_text(players)

            update.message.reply_text('-------------------------')
            update.message.reply_text("please choose the next khoda after you:")

            next_state = TYPING_REPLY
        else:
            update.message.reply_text("only admin can set new khoda")
    elif(user_command == 'define new player'):
        if(is_admin == True):
            if(door_to_join_open == True):
                update.message.reply_text("ok, please now type the name of the new player:")
                next_state = TYPING_REPLY
            else:
                update.message.reply_text("the door to join should be OPEN in order to define new player")
        else:
            update.message.reply_text("only admin can define new players...")
    elif(user_command == 'list all players'):
        update.message.reply_text("ok, now listing all players:")
        update.message.reply_text(players)
        next_state = CHOOSING
    elif(user_command == 'what is my role'):
        if(roles_are_assigned == True):
            #update.message.reply_text("ok, now trying to find you in players list...")
            if(user_id in players):
                user_index=players.index(user_id)
                #update.message.reply_text("you are at location " + str(user_index))
                update.message.reply_text("your role is " + roles_text[user_index])

                # 0 = not assigned yet
                # 1 = shahrvand / aadi
                # 2 = shahrvand / karagah
                # 3 = shahrvand / doctor
                # 4 = shahrvand / taktirandaz
                # 5 = mafia / aadi
                # 6 = mafia / raees mafia

                if (roles[user_index]==5 or roles[user_index]==6):
                    update.message.reply_text("your mafia team members are:")

                    for i in range(len(roles)):
                        if(roles[i]==5 or roles[i]==6):
                            if(not i == user_index):
                                update.message.reply_text(players[i] + " --> " + roles_text[i])
            else:
                update.message.reply_text("i could not find you in the players list :-(")
        else:
            update.message.reply_text("roles are not assigned yet!")
        next_state = CHOOSING
    elif(user_command == 'list all players and roles'):
        if(roles_are_assigned == True):
            if (is_admin == True or user_id == after1stnight_khoda):
                update.message.reply_text("ok, please now listing everything:")

                for i in range(len(players)):
                    current_player = players[i]
                    current_role = roles_text[i]
                    print_pair = [current_player,current_role]
                    update.message.reply_text(print_pair)

                #update.message.reply_text("done listing everything...")
                next_state = CHOOSING
            else:
                update.message.reply_text("only khoda can have a look at the roles")
        else:
            update.message.reply_text("roles are not assigned at this moment...")
            next_state = CHOOSING
    elif(user_command == 'assign roles'):
        if(is_admin == True):
            if(door_to_join_open == False):
                update.message.reply_text("ok, please tell me how many mafia will be in this game: (type some text to cancel)")
                next_state = TYPING_REPLY
            else:
                update.message.reply_text("door to join must be CLOSED in order to initiate random role assignment")
        else:
            update.message.reply_text("only admin can initiate random role assignment.")
    elif(user_command=='add me to game'):
        #update.message.reply_text("ok, now adding you to the game...")
        if user_id in players:
            update.message.reply_text("you are already in the game: "+user_id)

        else:
            if(door_to_join_open == True):
                players = players + [user_id]
                update.message.reply_text("ok, now you are added..."+user_id)

                roles = []
                roles_text = []
                roles_are_assigned = False
                after1stnight_khoda = 'nobody... oh nobody...'
                did_karagah_ask_first_time = True

                write_status()  # backup status to disk to reload if crash
            else:
                update.message.reply_text("the door to join is closed at the moment... please ask khoda to open the door.")

        #update.message.reply_text("ok, now listing all players:")
        #update.message.reply_text(players)

    if(next_state==CHOOSING):
        #update.message.reply_text("finished -- made_a_choice --",reply_markup=markup)
        update.message.reply_text("...", reply_markup=markup)
    else:
        #update.message.reply_text("finished -- made_a_choice --")
        update.message.reply_text("...", reply_markup=markup)

    return next_state

def typed_something_after_question(update, context):
    global players, num_mafias, after1stnight_khoda, did_karagah_ask_first_time, door_to_join_open, roles, roles_text
    text = update.message.text
    user_response = text
    user_command = context.user_data["user_command"]
    user_id = update.message.from_user.name

    #update.message.reply_text("started -- typed_something_after_question -- with input: " + text)
    #update.message.reply_text("the user command is:" + user_command)

    if(user_command=='define new player'):
        #update.message.reply_text("ok, now adding the new user: " + text)
        if(text in players):
            update.message.reply_text(text + " already in players list!")
        else:
            roles = []
            roles_text = []
            roles_are_assigned = False
            after1stnight_khoda = 'nobody... oh nobody...'
            did_karagah_ask_first_time = True

            players = players + [text]
            update.message.reply_text("done adding " + text)

            write_status()  # backup status to disk to reload if crash
    elif (user_command == 'first night karagah ask'):
        user_to_ask = text

        if(user_to_ask in players):
            user_to_ask_index = players.index(user_to_ask)
            did_karagah_ask_first_time = True

            # --- log successful karagah asking ---
            now = datetime.datetime.now()
            timestr = now.strftime("%Y%m%d-%H%M%S karagah ask successful.txt")
            save_file = open("textfiles/"+timestr, 'a')
            save_file.write("----list of all players starts here: " + timestr + " ----\n")

            for i in range(len(players)):
                write_pair = [players[i], roles[i], roles_text[i]]
                write_text = '<' + ' '.join([str(elem) for elem in write_pair]) + '>\n'
                save_file.write(write_text)

            save_file.write("----ends here: " + timestr + " ----")
            save_file.write("\nkaragah is asking: "+user_to_ask+" with index "+str(user_to_ask_index)+"\n")
            # ----------

            # 0 = not assigned yet
            # 1 = shahrvand / aadi
            # 2 = shahrvand / karagah
            # 3 = shahrvand / doctor
            # 4 = shahrvand / taktirandaz
            # 5 = mafia / aadi
            # 6 = mafia / raees mafia

            if(roles[user_to_ask_index] == 5):
                update.message.reply_text(players[user_to_ask_index] + " is mafia! :-o")
                save_file.write("response to karagah: "+players[user_to_ask_index] + " is mafia! :-o\n")
            else:
                update.message.reply_text(players[user_to_ask_index] + " is shahrvand! :-)")
                save_file.write("response to karagah: " + players[user_to_ask_index] + " is shahrvand! :-)\n")

            save_file.write("karagah ask was invoked by "+user_id+"\ndone!")
            save_file.close()

            print("OBS! Karagah successfully asked...")
            write_status() #backup status to disk to reload if crash
        else:
            update.message.reply_text("i could not find that user! typing errors?")

    elif(user_command=='assign roles'):
        try:
            num_mafias = int(text)

            #update.message.reply_text("ok, now assigning roles based on " + text + " mafias in game")

            if (len(players) < 3 + num_mafias):
                update.message.reply_text("not enough players defined in the game")
            else:
                roles = []
                roles_text = []
                roles_are_assigned = False
                after1stnight_khoda = 'nobody... oh nobody...'
                did_karagah_ask_first_time = True

                assign_roles()
                update.message.reply_text("done assigning")

                write_status()  # backup status to disk to reload if crash
        except ValueError:
            update.message.reply_text("error parsing your requested mafia num... nothing done!")
    elif (user_command == 'set new khoda'):
        new_khoda_candidate = text
        if not new_khoda_candidate in players:
            update.message.reply_text("the new khoda candidate is not in players list! :-( typing errors??")
        else:
            after1stnight_khoda = new_khoda_candidate
            update.message.reply_text("ok, now "+new_khoda_candidate+" is set as khoda! he/she can read all players roles.")
            write_status()
    #update.message.reply_text("finished -- typed_something_after_question --", reply_markup=markup)
    update.message.reply_text("...", reply_markup=markup)

    return CHOOSING

def done(update, context):
    update.message.reply_text("good bye. robot stopped now!!! use /start again to start robot again")
    return ConversationHandler.END

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater(telegtoken.get_telegram_token(), use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [MessageHandler(Filters.regex('^(/start|print debug info|open the door to join|close the door to join|first night karagah ask|set new khoda|what is my role|add me to game|remove all players|define new player|list all players|assign roles|what is my role|list all players and roles)$'),
                                      made_a_choice),
                      ],

            TYPING_REPLY: [MessageHandler(Filters.text, typed_something_after_question),
                          ],
        },

        fallbacks=[MessageHandler(Filters.regex('^done'), done)]
    )

    dp.add_handler(conv_handler)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

def assign_roles():
    global num_mafias
    global players
    global roles
    global roles_text
    global roles_are_assigned
    global did_karagah_ask_first_time

    roles=[]
    roles_text=[]
    after1stnight_khoda = 'nobody... oh nobody...'
    did_karagah_ask_first_time = True

    num_doctor = 1
    num_karagah = 1
    num_taktirandaz = 1
    num_raeesmafia = 1

    num_players = len(players)
    roles = [0] * num_players

    # 0 = not assigned yet
    # 1 = shahrvand / aadi
    # 2 = shahrvand / karagah
    # 3 = shahrvand / doctor
    # 4 = shahrvand / taktirandaz
    # 5 = mafia / aadi
    # 6 = mafia / raees mafia

    # --- assign the mafia team ( mafia / aadi --> 5 , raeesmafia --> 6) ---
    assigned_mafia = 0
    assigned_raeesmafia = 0

    while assigned_mafia < num_mafias:
        new_mafia_candidate = randint(0, num_players - 1)
        if roles[new_mafia_candidate] == 0:
            if(assigned_raeesmafia < num_raeesmafia):
                  roles[new_mafia_candidate] = 6
                  assigned_raeesmafia = assigned_raeesmafia + 1
            else:
                  roles[new_mafia_candidate] = 5

            assigned_mafia = assigned_mafia + 1

    # --- assign the doctor 3 ---
    assigned_doctor = 0

    while assigned_doctor < num_doctor:
        new_doctor_candidate = randint(0, num_players - 1)
        if roles[new_doctor_candidate] == 0:
            roles[new_doctor_candidate] = 3
            assigned_doctor = assigned_doctor + 1

    # --- assign the karagah 2 ---
    assigned_karagah = 0

    while assigned_karagah < num_karagah:
        new_karagah_candidate = randint(0, num_players - 1)
        if roles[new_karagah_candidate] == 0:
            roles[new_karagah_candidate] = 2
            assigned_karagah = assigned_karagah + 1

    # --- assign the taktirandaz 4 ---
    assigned_taktirandaz = 0

    while assigned_taktirandaz < num_taktirandaz:
        new_taktirandaz_candidate = randint(0, num_players - 1)
        if roles[new_taktirandaz_candidate] == 0:
            roles[new_taktirandaz_candidate] = 4
            assigned_taktirandaz = assigned_taktirandaz + 1

    # --- the rest should be normal citizen 1 ---
    for i in range(len(roles)):
        if roles[i] == 0:
            roles[i] = 1

    # 0 = not assigned yet
    # 1 = shahrvand / aadi
    # 2 = shahrvand / karagah
    # 3 = shahrvand / doctor
    # 4 = shahrvand / taktirandaz
    # 5 = mafia / aadi
    # 6 = mafia / raees mafia

    # --- assign the roles
    for i in range(num_players):
        if roles[i] == 0:
            roles_text = roles_text + ["error?"]
        if roles[i] == 1:
            roles_text = roles_text + ["shahrvand / aadi"]
        elif roles[i] == 2:
            roles_text = roles_text + ["shahrvand / karagah"]
        elif roles[i] == 3:
            roles_text = roles_text + ["shahrvand / doctor"]
        elif roles[i] == 4:
             roles_text = roles_text + ["shahrvand / taktirandaz"]
        elif roles[i] == 5:
             roles_text = roles_text + ["mafia / aadi"]
        elif roles[i] == 6:
             roles_text = roles_text + ["mafia / raees mafia"]

    now = datetime.datetime.now()
    timestr = now.strftime("%Y%m%d-%H%M%S roles backup.txt")
    save_file = open("textfiles/"+timestr,'a')
    save_file.write("----starts here: "+timestr+" ----\n")

    for i in range(len(players)):
        write_pair = [players[i],roles[i],roles_text[i]]
        write_text = '<'+ ' '.join([str(elem) for elem in write_pair])+'>\n'
        save_file.write(write_text)

    save_file.write("----ends here: " + timestr + " ----")
    save_file.close()

    roles_are_assigned = True
    did_karagah_ask_first_time = False

    #print(roles)
    #print(roles_text)

def write_status():
    global players, roles, roles_text, roles_are_assigned
    global num_mafias, after1stnight_khoda, did_karagah_ask_first_time, door_to_join_open

    now = datetime.datetime.now()
    timestr = now.strftime("%Y%m%d-%H%M%S status backup.txt")
    save_file = open("textfiles/"+timestr, 'a')
    save_file.write("----starts here: " + timestr + " ----\n")

    save_file.write("<players>\n")
    save_file.write(json.dumps(players))
    save_file.write("\n")

    save_file.write("\n<roles>\n")
    save_file.write(json.dumps(roles))
    save_file.write("\n")

    save_file.write("\n<roles_text>\n")
    save_file.write(json.dumps(roles_text))
    save_file.write("\n")

    save_file.write("\n<roles_are_assigned>\n")
    save_file.write(json.dumps(roles_are_assigned))
    save_file.write("\n")

    save_file.write("\n<num_mafias>\n")
    save_file.write(json.dumps(num_mafias))
    save_file.write("\n")

    save_file.write("\n<after1stnight_khoda>\n")
    save_file.write(json.dumps(after1stnight_khoda))
    save_file.write("\n")

    save_file.write("\n<did_karagah_ask_first_time>\n")
    save_file.write(json.dumps(did_karagah_ask_first_time))
    save_file.write("\n")

    save_file.write("\n<door_to_join_open>\n")
    save_file.write(json.dumps(door_to_join_open))
    save_file.write("\n")

    save_file.write("----ends here: " + timestr + " ----")
    save_file.close()

    print("status backed up to file "+timestr+" for recovery if crash happens")

    save_lastvalidbackup = open("textfiles/last_valid_backup.txt", 'w')
    save_lastvalidbackup.write(timestr)
    save_lastvalidbackup.close()

def read_status():
    global players, roles, roles_text, roles_are_assigned
    global num_mafias, after1stnight_khoda, did_karagah_ask_first_time, door_to_join_open

    if(os.path.exists("textfiles/last_valid_backup.txt")):
        print("reading last_valid_backup.txt...")

        read_file = open("textfiles/last_valid_backup.txt",'r')

        lastvalidbackup_filename = read_file.readline()
        read_file.close()

        print("it is pointing to "+lastvalidbackup_filename+" as last valid backup!")

        if(os.path.exists("textfiles/"+lastvalidbackup_filename)):
            print("reading "+lastvalidbackup_filename)

            read_backup_file = open("textfiles/"+lastvalidbackup_filename,'r')
            backup_file_contents = read_backup_file.readlines()
            read_backup_file.close()

            if(len(backup_file_contents) != 25):
                print("invalid length of backup file! skipping")
            else:
                print("length of backup file ok. reading in...")

                players_input = backup_file_contents[2].rstrip("\n")
                roles_input = backup_file_contents[5].rstrip("\n")
                roles_text_input = backup_file_contents[8].rstrip("\n")
                roles_are_assigned_input = backup_file_contents[11].rstrip("\n")
                num_mafias_input = backup_file_contents[14].rstrip("\n")
                after1stnight_khoda_input = backup_file_contents[17].rstrip("\n")
                did_karagah_ask_first_time_input = backup_file_contents[20].rstrip("\n")
                door_to_join_open_input = backup_file_contents[23].rstrip("\n")

                #print("players_input: "+players_input)
                #print("roles_input: "+roles_input)
                #print("roles_text_input: "+roles_text_input)
                #print("roles_are_assigned_input: "+roles_are_assigned_input)
                #print("num_mafias_input: "+num_mafias_input)
                #print("after1stnight_khoda_input: "+after1stnight_khoda_input)
                #print("did_karagah_ask_first_time_input: "+did_karagah_ask_first_time_input)
                #print("door_to_join_open_input: "+door_to_join_open_input)
                #print("now parsing")

                players_input = players_input.replace('[','').replace(']','').replace(', ',',').replace('"','')
                players_input_parsed = players_input.split(',')
                if players_input_parsed == ['']:
                    players=[]
                else:
                    players = players_input_parsed

                roles_input = roles_input.replace('[', '').replace(']', '').replace(', ', ',').replace('"', '')
                roles_input_parsed = roles_input.split(',')
                if roles_input_parsed ==['']:
                    roles=[]
                else:
                    roles = roles_input_parsed

                for i in range(len(roles)):
                    if roles[i] != '':
                      roles[i] = int(roles[i])

                roles_text_input = roles_text_input.replace('[', '').replace(']', '').replace(', ', ',').replace('"', '')
                roles_text_input_parsed = roles_text_input.split(',')
                if roles_text_input_parsed ==['']:
                    roles_text=[]
                else:
                    roles_text = roles_text_input_parsed

                if(roles_are_assigned_input.lower()=='true'):
                    roles_are_assigned = True
                else:
                    roles_are_assigned = False

                num_mafias = int(num_mafias_input)

                after1stnight_khoda = after1stnight_khoda_input.replace('"','')

                if(did_karagah_ask_first_time_input.lower()=='true'):
                    did_karagah_ask_first_time = True
                else:
                    did_karagah_ask_first_time = False

                if(door_to_join_open_input.lower()=='true'):
                    door_to_join_open = True
                else:
                    door_to_join_open = False
        else:
            print(lastvalidbackup_filename+" did not exist! :-(")
            print("skipped reloading from backup...")

            os.remove("textfiles/last_valid_backup.txt")
            print("removed last_valid_backup.txt due to pointing to non-existing file")
    else:
        print("last_valid_backup.txt does not exist... skipped loading!")

if __name__ == '__main__':
    main()
