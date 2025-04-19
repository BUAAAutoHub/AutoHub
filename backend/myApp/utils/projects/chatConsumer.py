import json
import datetime

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from myApp.models import Group, User, Message, UserGroup


class ChatConsumer(WebsocketConsumer):
    '''
        Date        :   2025/4/18
        Author      :   tangling
        Description :   通过 Django Channels 技术实现
                        一个基于 WebSocket 的聊天室功能
                        用户可以加入特定房间进行实时聊天
    '''
    def connect(self):
        # get roomid from websocket request url kwargs
        self.room_id = int(self.scope['url_route']['kwargs']['roomId'])
        self.room = Group.objects.get(id=self.room_id)
        self.room_group_name = 'char_room_%s' % self.room_id

        # get userId from websocket request url
        self.user_id = int(self.scope['url_route']['kwargs']['userId'])

        # join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        # accept the connect request
        self.accept()

    def disconnect(self, code):
        # disconnect the websocket connection
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        # check if text_data is not none
        assert text_data is not None

        # read the message from webcokect scope['text']['message']
        ws_json_data = json.loads(text_data)
        message_content, send_user_id = str(ws_json_data['message']),
        int(ws_json_data['sender'])

        send_user = User.objects.get(id=send_user_id)
        send_time = datetime.datetime.now()
        # generate the message for all users in this room,
        # and flag these messages' unchecking status.
        for association in UserGroup.objects.filter(group_id=self.room.id):
            check_status = 'UC'
            if association.user.id == send_user_id:
                check_status = 'C'
            message = Message(
                type='A',
                status=check_status,
                content=message_content,
                time=send_time,
                group_id=self.room,
                send_user=send_user,
                receive_user=association.user
            )
            message.save()

        # send the message to others in this room.
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {
                'type': 'chat_message',
                'send_user_name': send_user.name,
                'send_user_id': send_user.id,
                'message': message_content,
                'send_time': send_time,
            }
        )

    def chat_message(self, event):
        send_time = str(event['send_time'])

        # set the message status to 'checked'
        for message in Message.objects.filter(time=send_time):
            if message.receive_user.id == self.user_id:
                message.status = 'C'
                message.save()
                break

        # send message to client
        self.send(text_data=json.dumps({
            'content': event['message'],
            'senderName': event['send_user_name'],
            'senderId': event['send_user_id'],
            'time': str(event['send_time'])
        }))
