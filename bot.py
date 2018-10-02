#!.venv/bin/python

import os
import time
import re
from slackclient import SlackClient
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

slack_client = SlackClient([BOTTOKEN])


def get_num_users_in_channel(channel):
    response = slack_client.api_call(
        'conversations.members',
        channel=channel
    )
    if not response['ok']:
        print(
            f'Something went wrong fetching channel members. Response from server:\n{response}')
        return
    num_members = len(response['members'])
    while response['response_metadata']['next_cursor']:
        response = slack_client.api_call(
            'conversations.members',
            channel=channel,
            cursor=response['response_metadata']['next_cursor']
        )
        num_members += len(response['members'])
    return num_members


def send_message_ephemeral(text, channel, user):
    slack_client.api_call(
        'chat.postEphemeral',
        channel=channel,
        text=text,
        as_user=True,
        user=user
    )


def handle_here(message):
    if '<!here>' in message['text']:
        user = message['user']
        num_users_in_channel = get_num_users_in_channel(message['channel'])
        warn_message = f"Hey <@{user}>, you used a global notifier command that notified {num_users_in_channel} users. Are you sure you wanted to notify all these users or only some? Please check the topic for more specific groups you want to contact."
        send_message_ephemeral(warn_message, message['channel'], user)


def process_events(slack_events):
    for event in slack_events:
        if event['type'] == 'message':
            handle_here(event)


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        while True:
            process_events(slack_client.rtm_read())
    else:
        print("Connection failed. Exception traceback printed above.")
