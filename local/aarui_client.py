
import struct
import hl2ss


class aarui_command_buffer(hl2ss.umq_command_buffer):
    _MSG_INITIALIZE = 0x00000000
    _MSG_SET_TASKS = 0x00000010
    _MSG_SET_CURRENT_TASK_ID = 0x00000011
    _MSG_SET_TASK_LIST_ACTIVE = 0x00000012
    _MSG_SET_ALL_TASKS_DONE = 0x00000013
    _MSG_TOGGLE_TASKS_LIST = 0x00000014
    _MSG_SET_TASK_LIST_EYE_EVENTS_ACTIVE = 0x00000015
    _MSG_MUTE_AUDIO = 0x00000016
    _MSG_GET_USER_FEEDBACK_RESULT = 0x00000020
    _MSG_TRY_GET_USER_FEEDBACK_ON_USER_INTENT = 0x00000021
    _MSG_SHOW_SKIP_NOTIFICATION = 0x00000022

    def initialize(self):
        self.add(aarui_command_buffer._MSG_INITIALIZE, b'')

    def set_tasks(self, tasks):
        data = bytearray()
        for (level, text) in tasks:
            data.extend((level + text + '\n').encode('utf-8'))
        self.add(aarui_command_buffer._MSG_SET_TASKS, bytes(data))

    def set_current_task_id(self, id):
        self.add(aarui_command_buffer._MSG_SET_CURRENT_TASK_ID, struct.pack('<I', id))

    def set_task_list_active(self, active):
        self.add(aarui_command_buffer._MSG_SET_TASK_LIST_ACTIVE, struct.pack('<I', int(active)))

    def set_all_tasks_done(self):
        self.add(aarui_command_buffer._MSG_SET_ALL_TASKS_DONE, b'')

    def toggle_task_list(self):
        self.add(aarui_command_buffer._MSG_TOGGLE_TASKS_LIST, b'')

    def set_task_list_eye_events_active(self, active):
        self.add(aarui_command_buffer._MSG_SET_TASK_LIST_EYE_EVENTS_ACTIVE, struct.pack('<I', int(active)))
        
    def mute_audio(self, mute):
        self.add(aarui_command_buffer._MSG_MUTE_AUDIO, struct.pack('<I', int(mute)))

    def get_user_feedback_result(self):
        self.add(aarui_command_buffer._MSG_GET_USER_FEEDBACK_RESULT, b'')

    def try_get_user_feedback_on_user_intent(self, msg):
        self.add(aarui_command_buffer._MSG_TRY_GET_USER_FEEDBACK_ON_USER_INTENT, msg.encode('utf-8'))

    def show_skip_notification(self, show):
        self.add(aarui_command_buffer._MSG_SHOW_SKIP_NOTIFICATION, struct.pack('<I', int(show)))


tasks = [
    ("0", "Remove the nut and the air cleaner cover"),
    ("0", "Remove the wing nut and air filter assembly"),
    ("0", "Separate the inner paper filter from the outer foam filter. Carefully check both filters for holes or tears and replace if damaged."),
    ("0", "Separate the inner paper filter from the outer foam filter."),
    ("0", "Remove the wing nut and air filter assembly."),
    ("0", "Remove the nut and the air cleaner cover."),
]

host = '192.168.1.7'
port = hl2ss.IPCPort.UNITY_MESSAGE_QUEUE

client = hl2ss.ipc_umq(host, port)
client.open()

cb = aarui_command_buffer()
cb.initialize()
cb.set_tasks(tasks)
#cb.set_current_task_id(1)
#cb.set_task_list_active(True)
#cb.set_all_tasks_done()
#cb.toggle_task_list()
#cb.mute_audio(True)
cb.try_get_user_feedback_on_user_intent('go to next step')
cb.show_skip_notification(True)

client.push(cb)
result = client.pull(cb)
print(result)

while (True):
    cb = aarui_command_buffer()
    cb.get_user_feedback_result()
    client.push(cb)
    result = client.pull(cb)
    if (result != 0):
        break

print('got user feedback result')

client.close()
