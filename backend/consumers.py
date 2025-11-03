# from channels.generic.websocket import WebsocketConsumer
# import json
#
#
# class WSConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()
#
#         self.send(json.dumps({"message": "✅ Соединение установлено"}))
#
#     def send_json(self, data: dict):
#         self.send(text_data=json.dumps(data))
