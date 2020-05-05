import warnings
import telegtoken
import json
import logging
import os.path
import datetime
import csv
from random import seed
from random import randint
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

players_names = ['example_player1_for_testing','example_player2_for_testing','example_player3_for_testing','example_player4_for_testing','example_player5_for_testing','example_player6_for_testing','example_player7_for_testing','example_player8_for_testing','example_player9_for_testing','example_player10_for_testing','example_player11_for_testing','example_player12_for_testing','example_player13_for_testing','example_player14_for_testing','example_player15_for_testing']
player_roles = []
player_roles_as_text = []
player_roles_are_assigned = False
num_mafias = 0
alternative_khoda = 'nobody... oh nobody...'
has_karagah_already_asked = True
door_to_join_open = False
backup_data_loaded = False

#----new variables defined 5 may 2020 ----
day_or_night = 0      #0=not initialized, 1=day, 2=night
daynight_num = 0      #0=not initialized, 1=first day or night, 2=second day or night, ...
last_night_message = 'game has not been initialized yet'
player_alive_or_dead = []  #1=alive, 0=dead
#-----------------------------------------

CHOOSING, TYPING_REPLY = range(2)

reply_keyboard = [['/start','add me to game'],
                  ['game overall status','what is my role'],
                  ['at night mafia kill','at night doctor heal'],
                  ['at night karagah ask','at night taktir shoot'],
                  ['set new khoda'],
                  ['set player dead','set player alive'],
                  ['from day to night', 'from night to day'],
                  ['open the door to join', 'close the door to join'],
                  ['remove all players', 'define new player'],
                  ['list all players', 'assign roles'],
                  ['list all players and roles']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

def start(update, context):
    global backup_data_loaded
    if backup_data_loaded == False:
        read_status()
        backup_data_loaded = True

    update.message.reply_text(
        'hello. robots has just started now. please select your command:',
        reply_markup=markup)

    return CHOOSING

def made_a_choice(update, context):
    global players_names
    global alternative_khoda
    global player_roles_are_assigned
    global player_roles
    global player_roles_as_text
    global has_karagah_already_asked
    global door_to_join_open
    global day_or_night
    global daynight_num
    next_state = CHOOSING
    text = update.message.text
    user_command = text
    user_id = update.message.from_user.name
    context.user_data['user_command'] = user_command
    is_admin = False

    if (user_id == '@bahman_canon'):
        is_admin = True

    if(user_command == 'remove all players'):
        if(is_admin == True):
            if(door_to_join_open == True):
                players_names = []
                player_roles= []
                player_roles_as_text = []
                player_roles_are_assigned = False
                alternative_khoda = 'nobody... oh nobody...'
                has_karagah_already_asked = True

                update.message.reply_text('now, i have cleaned up the list of players. the list is empty now')

                next_state = CHOOSING

                write_status() #backup status to disk to reload if crash
            else:
                update.message.reply_text('door to join should be OPEN in order to remove all players')
        else:
            update.message.reply_text('only admin can reset the player list...')
    elif (user_command == '/start'):
        update.message.reply_text('robot is up and running.')
        next_state = CHOOSING
    elif (user_command == 'set player dead' and is_admin == False):
        update.message.reply_text('only khoda can do this')
        next_state = CHOOSING
    elif (user_command == 'set player dead' and is_admin == True):
        if player_roles_are_assigned == False:
            update.message.reply_text('roles are not defined yet. therefore, game is not initialized')
            next_state = CHOOSING
        else:
            update.message.reply_text('all players in game:')

            for i in range(len(players_names)):
                current_player = players_names[i]
                if (player_roles_are_assigned == True):
                    if player_alive_or_dead[i] == 1:
                        current_alive_or_dead = 'alive'
                    elif player_alive_or_dead[i] == 0:
                        current_alive_or_dead = 'dead'
                    else:
                        current_alive_or_dead = 'error?'
                else:
                    current_alive_or_dead = 'not initialized yet'

                print_pair = [current_player, current_alive_or_dead]
                update.message.reply_text(print_pair)

            update.message.reply_text('------')
            update.message.reply_text('please select the player you wish to set as dead:')

            next_state = TYPING_REPLY
    elif (user_command == 'set player alive'):
        if player_roles_are_assigned == False:
            update.message.reply_text('roles are not defined yet. therefore, game is not initialized')
            next_state = CHOOSING

    elif (user_command == 'game overall status'):
        update.message.reply_text('all players in game:')

        for i in range(len(players_names)):
            current_player = players_names[i]
            if(player_roles_are_assigned==True):
                if player_alive_or_dead[i]==1:
                    current_alive_or_dead = 'alive'
                elif player_alive_or_dead[i]==0:
                    current_alive_or_dead = 'dead'
                else:
                    current_alive_or_dead = 'error?'
            else:
                current_alive_or_dead = 'not initialized yet'
            print_pair = [current_player, current_alive_or_dead]
            update.message.reply_text(print_pair)
        if player_roles_are_assigned == True:
            update.message.reply_text('------')

            status = ''
            if(day_or_night==0):
                update.message.reply_text("game is not initialized yet!")
            elif(day_or_night==1):
                status = status + 'day '
            elif(day_or_night==2):
                status = status + 'night '

            if(day_or_night!=0):
                status = status + str(daynight_num)
                update.message.reply_text('it is currently: '+status)

            if(day_or_night!=0 and daynight_num >= 2):
                update.message.reply_text('message from last night:')
                update.message.reply_text(last_night_message)

        next_state = CHOOSING

    elif (user_command == 'open the door to join'):
        if is_admin == True:
            door_to_join_open = True
            update.message.reply_text('the door to join is now OPEN.')
            next_state = CHOOSING

            write_status()  # backup status to disk to reload if crash
        else:
            update.message.reply_text('only admin can open the door')
            next_state = CHOOSING
    elif (user_command == 'close the door to join'):
        if is_admin == True:
            door_to_join_open = False
            update.message.reply_text('the door to join is now CLOSED.')
            next_state = CHOOSING

            write_status()  # backup status to disk to reload if crash
        else:
            update.message.reply_text('only admin can close the door')
            next_state = CHOOSING
    elif (user_command == 'first night karagah ask'):
        if(player_roles_are_assigned == True):
            if (user_id in players_names):
                index = players_names.index(user_id)
                player_role = player_roles[index]

                # 0 = not assigned yet
                # 1 = shahrvand / aadi
                # 2 = shahrvand / karagah
                # 3 = shahrvand / doctor
                # 4 = shahrvand / taktirandaz
                # 5 = mafia / aadi
                # 6 = mafia / raees mafia

                if(player_role == 2):
                    if(has_karagah_already_asked == False):
                        update.message.reply_text('ok, now listing all players:')
                        update.message.reply_text(players_names)

                        update.message.reply_text('please write the name of person you want to ask:')

                        next_state = TYPING_REPLY
                    else:
                        update.message.reply_text('you have already asked once. ;-) only once is allowed')
                        next_state = CHOOSING

                else:
                    update.message.reply_text('you are not karagah. only karagah can ask')
                    next_state = CHOOSING

            else:
                update.message.reply_text('you are not in players list.')
                next_state = CHOOSING
        else:
            update.message.reply_text('roles are not assigned yet. you are not karagah')
            next_state = CHOOSING


    elif (user_command == 'set new khoda'):
        if(is_admin == True):
            update.message.reply_text('ok, now listing all players:')
            update.message.reply_text(players_names)

            update.message.reply_text('-------------------------')
            update.message.reply_text('please choose the next khoda after you:')

            next_state = TYPING_REPLY
        else:
            update.message.reply_text('only admin can set new khoda')
    elif(user_command == 'define new player'):
        if(is_admin == True):
            if(door_to_join_open == True):
                update.message.reply_text('ok, please now type the name of the new player:')
                next_state = TYPING_REPLY
            else:
                update.message.reply_text('the door to join should be OPEN in order to define new player')
        else:
            update.message.reply_text('only admin can define new players...')
    elif(user_command == 'list all players'):
        update.message.reply_text('ok, now listing all players:')
        update.message.reply_text(players_names)
        next_state = CHOOSING
    elif(user_command == 'what is my role'):
        if(player_roles_are_assigned == True):
            if(user_id in players_names):
                user_index=players_names.index(user_id)
                update.message.reply_text('your role is ' + player_roles_as_text[user_index])

                # 0 = not assigned yet
                # 1 = shahrvand / aadi
                # 2 = shahrvand / karagah
                # 3 = shahrvand / doctor
                # 4 = shahrvand / taktirandaz
                # 5 = mafia / aadi
                # 6 = mafia / raees mafia

                if (player_roles[user_index]==5 or player_roles[user_index]==6):
                    update.message.reply_text('your mafia team members are:')

                    for i in range(len(player_roles)):
                        if(player_roles[i]==5 or player_roles[i]==6):
                            if(not i == user_index):
                                update.message.reply_text(players_names[i] + ' --> ' + player_roles_as_text[i])
            else:
                update.message.reply_text('i could not find you in the players list :-(')
        else:
            update.message.reply_text('roles are not assigned yet.')
        next_state = CHOOSING
    elif(user_command == 'list all players and roles'):
        if(player_roles_are_assigned == True):
            if (is_admin == True or user_id == alternative_khoda):
                update.message.reply_text('ok, please now listing everything:')

                for i in range(len(players_names)):
                    current_player = players_names[i]
                    current_role = player_roles_as_text[i]
                    print_pair = [current_player,current_role]
                    update.message.reply_text(print_pair)

                next_state = CHOOSING
            else:
                update.message.reply_text('only khoda can have a look at the roles')
        else:
            update.message.reply_text('roles are not assigned at this moment...')
            next_state = CHOOSING
    elif(user_command == 'assign roles'):
        if(is_admin == True):
            if(door_to_join_open == False):
                update.message.reply_text('ok, please tell me how many mafia will be in this game: (type some text to cancel)')
                next_state = TYPING_REPLY
            else:
                update.message.reply_text('door to join must be CLOSED in order to initiate random role assignment')
        else:
            update.message.reply_text('only admin can initiate random role assignment.')
    elif(user_command=='add me to game'):
        if user_id in players_names:
            update.message.reply_text('you are already in the game: '+user_id)

        else:
            if(door_to_join_open == True):
                players_names = players_names + [user_id]
                update.message.reply_text('ok, now you are added...'+user_id)

                player_roles= []
                player_roles_as_text = []
                player_roles_are_assigned = False
                alternative_khoda = 'nobody... oh nobody...'
                has_karagah_already_asked = True

                write_status()  # backup status to disk to reload if crash
            else:
                update.message.reply_text('the door to join is closed at the moment... please ask khoda to open the door.')

    update.message.reply_text('----------------------------------------',reply_markup=markup)
    return next_state

def typed_something_after_question(update, context):
    global players_names
    global num_mafias
    global alternative_khoda
    global has_karagah_already_asked
    global door_to_join_open
    global player_roles
    global player_roles_as_text
    global day_or_night
    global daynight_num

    text = update.message.text
    user_response = text
    user_command = context.user_data['user_command']
    user_id = update.message.from_user.name


    if(user_command=='define new player'):
        if(text in players_names):
            update.message.reply_text(text + ' already in players list.')
        else:
            player_roles= []
            player_roles_as_text = []
            player_roles_are_assigned = False
            alternative_khoda = 'nobody... oh nobody...'
            has_karagah_already_asked = True

            players_names = players_names + [text]
            update.message.reply_text('done adding ' + text)

            write_status()  # backup status to disk to reload if crash
    elif (user_command == 'set player dead'):
        user_to_set_dead = text

        if(not user_to_set_dead in players_names):
            update.message.reply_text('i could not find the player name')
        else:
            update.message.reply_text('setting dead: '+user_to_set_dead)

            dead_user_index = players_names.index(user_to_set_dead)

            if(player_alive_or_dead[dead_user_index] == 0):
                update.message.reply_text('player status was already: dead')
            else:
                player_alive_or_dead[dead_user_index]=0;
    elif (user_command == 'first night karagah ask'):
        user_to_ask = text

        if(user_to_ask in players_names):
            user_to_ask_index = players_names.index(user_to_ask)
            has_karagah_already_asked = True

            now = datetime.datetime.now()
            timestr = now.strftime('%Y%m%d-%H%M%S karagah ask successful.txt')
            save_file = open('textfiles/'+timestr, 'a')
            save_file.write('----list of all players starts here: ' + timestr + ' ----\n')

            for i in range(len(players_names)):
                write_pair = [players_names[i], player_roles[i], player_roles_as_text[i]]
                write_text = '<' + ' '.join([str(elem) for elem in write_pair]) + '>\n'
                save_file.write(write_text)

            save_file.write('----ends here: ' + timestr + ' ----')
            save_file.write('\nkaragah is asking: '+user_to_ask+' with index '+str(user_to_ask_index)+'\n')

            # 0 = not assigned yet
            # 1 = shahrvand / aadi
            # 2 = shahrvand / karagah
            # 3 = shahrvand / doctor
            # 4 = shahrvand / taktirandaz
            # 5 = mafia / aadi
            # 6 = mafia / raees mafia

            if(player_roles[user_to_ask_index] == 5):
                update.message.reply_text(players_names[user_to_ask_index] + ' is mafia. :-o')
                save_file.write('response to karagah: '+players_names[user_to_ask_index] + ' is mafia. :-o\n')
            else:
                update.message.reply_text(players_names[user_to_ask_index] + ' is shahrvand. :-)')
                save_file.write('response to karagah: ' + players_names[user_to_ask_index] + ' is shahrvand. :-)\n')

            save_file.write('karagah ask was invoked by '+user_id+'\ndone.')
            save_file.close()

            print('OBS. Karagah successfully asked...')
            write_status() #backup status to disk to reload if crash
        else:
            update.message.reply_text('i could not find that user. typing errors?')

    elif(user_command=='assign roles'):
        try:
            num_mafias = int(text)

            if (len(players_names) < 3 + num_mafias):
                update.message.reply_text('not enough players defined in the game')
            else:
                player_roles= []
                player_roles_as_text = []
                player_roles_are_assigned = False
                alternative_khoda = 'nobody... oh nobody...'
                has_karagah_already_asked = True

                assign_roles()
                update.message.reply_text('done assigning')

                write_status()  # backup status to disk to reload if crash
        except ValueError:
            update.message.reply_text('error parsing your requested mafia num... nothing done.')
    elif (user_command == 'set new khoda'):
        new_khoda_candidate = text
        if not new_khoda_candidate in players_names:
            update.message.reply_text('the new khoda candidate is not in players list. :-( typing errors??')
        else:
            alternative_khoda = new_khoda_candidate
            update.message.reply_text('ok, now '+new_khoda_candidate+' is set as khoda. he/she can read all players roles.')
            write_status()
    update.message.reply_text('...', reply_markup=markup)

    return CHOOSING

def done(update, context):
    update.message.reply_text('good bye. robot stopped now... use /start again to start robot again')
    return ConversationHandler.END

def main():
    warnings.simplefilter('error')
    updater = Updater(telegtoken.get_telegram_token(), use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [MessageHandler(Filters.regex('^(/start|set player dead|set player alive|game overall status|open the door to join|close the door to join|first night karagah ask|set new khoda|what is my role|add me to game|remove all players|define new player|list all players|assign roles|what is my role|list all players and roles)$'),
                                      made_a_choice),
                      ],

            TYPING_REPLY: [MessageHandler(Filters.text, typed_something_after_question),
                          ],
        },

        fallbacks=[MessageHandler(Filters.regex('^neverhappening'), done)]
    )

    dp.add_error_handler(error)
    dp.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()

def assign_roles():
    global num_mafias
    global players_names
    global player_roles
    global player_roles_as_text
    global player_roles_are_assigned
    global has_karagah_already_asked
    global player_alive_or_dead
    global day_or_night
    global daynight_num

    player_roles=[]
    player_roles_as_text=[]
    alternative_khoda = 'nobody... oh nobody...'
    has_karagah_already_asked = True

    day_or_night=1
    daynight_num=1

    num_doctor = 1
    num_karagah = 1
    num_taktirandaz = 1
    num_raeesmafia = 1

    num_players = len(players_names)
    player_roles= [0] * num_players
    player_alive_or_dead = [1] * num_players

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
        if player_roles[new_mafia_candidate] == 0:
            if(assigned_raeesmafia < num_raeesmafia):
                  player_roles[new_mafia_candidate] = 6
                  assigned_raeesmafia = assigned_raeesmafia + 1
            else:
                  player_roles[new_mafia_candidate] = 5

            assigned_mafia = assigned_mafia + 1

    # --- assign the doctor 3 ---
    assigned_doctor = 0

    while assigned_doctor < num_doctor:
        new_doctor_candidate = randint(0, num_players - 1)
        if player_roles[new_doctor_candidate] == 0:
            player_roles[new_doctor_candidate] = 3
            assigned_doctor = assigned_doctor + 1

    # --- assign the karagah 2 ---
    assigned_karagah = 0

    while assigned_karagah < num_karagah:
        new_karagah_candidate = randint(0, num_players - 1)
        if player_roles[new_karagah_candidate] == 0:
            player_roles[new_karagah_candidate] = 2
            assigned_karagah = assigned_karagah + 1

    # --- assign the taktirandaz 4 ---
    assigned_taktirandaz = 0

    while assigned_taktirandaz < num_taktirandaz:
        new_taktirandaz_candidate = randint(0, num_players - 1)
        if player_roles[new_taktirandaz_candidate] == 0:
            player_roles[new_taktirandaz_candidate] = 4
            assigned_taktirandaz = assigned_taktirandaz + 1

    # --- the rest should be normal citizen 1 ---
    for i in range(len(player_roles)):
        if player_roles[i] == 0:
            player_roles[i] = 1

    # 0 = not assigned yet
    # 1 = shahrvand / aadi
    # 2 = shahrvand / karagah
    # 3 = shahrvand / doctor
    # 4 = shahrvand / taktirandaz
    # 5 = mafia / aadi
    # 6 = mafia / raees mafia

    for i in range(num_players):
        if player_roles[i] == 0:
            player_roles_as_text = player_roles_as_text + ['error?']
        if player_roles[i] == 1:
            player_roles_as_text = player_roles_as_text + ['shahrvand / aadi']
        elif player_roles[i] == 2:
            player_roles_as_text = player_roles_as_text + ['shahrvand / karagah']
        elif player_roles[i] == 3:
            player_roles_as_text = player_roles_as_text + ['shahrvand / doctor']
        elif player_roles[i] == 4:
             player_roles_as_text = player_roles_as_text + ['shahrvand / taktirandaz']
        elif player_roles[i] == 5:
             player_roles_as_text = player_roles_as_text + ['mafia / aadi']
        elif player_roles[i] == 6:
             player_roles_as_text = player_roles_as_text + ['mafia / raees mafia']

    now = datetime.datetime.now()
    timestr = now.strftime('%Y%m%d-%H%M%S roles backup.txt')
    save_file = open('textfiles/'+timestr,'a')
    save_file.write('----starts here: '+timestr+' ----\n')

    for i in range(len(players_names)):
        write_pair = [players_names[i],player_roles[i],player_roles_as_text[i]]
        write_text = '<'+ ' '.join([str(elem) for elem in write_pair])+'>\n'
        save_file.write(write_text)

    save_file.write('----ends here: ' + timestr + ' ----')
    save_file.close()

    player_roles_are_assigned = True
    has_karagah_already_asked = False

def write_status():
    global players_names, player_roles, player_roles_as_text, player_roles_are_assigned
    global num_mafias, alternative_khoda, has_karagah_already_asked, door_to_join_open

def read_status():
    global players_names, player_roles, player_roles_as_text, player_roles_are_assigned
    global num_mafias, alternative_khoda, has_karagah_already_asked, door_to_join_open

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    logger.warning('Update %s caused error %s', update, context.error)

if __name__ == '__main__':
    main()
