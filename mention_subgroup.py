#!/usr/bin/python3

import sys


def mention_subgroup(groups, sender, group_list):
    mentions = ''

    for group in groups:
        if group[:2].upper() in group_list.keys():
            for user in group_list[group[:2].upper()]:
                if user not in mentions and user != sender:
                    mentions += '@' + user + ' '

    return mentions
    
