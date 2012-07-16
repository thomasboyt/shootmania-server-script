import random


def scrambler(server):
    all_player_list = server.GetPlayerList(50, 0)
    player_list = []
    # remove spectators
    for player in all_player_list:
        if player['TeamId'] != -1:
            player_list.append(player)

    server.ChatSendServerMessage("Notice: Scrambling teams")

    random.shuffle(player_list)
    for index, player in enumerate(player_list):
        login = player['Login']
        if index % 2 == 0:
            server.ForcePlayerTeam(login, 0)
        else:
            server.ForcePlayerTeam(login, 1)