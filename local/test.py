
import hl2ss
import hl2ss_aarui

host = '192.168.1.7'

tasks = [
    ("0", "Remove the nut and the air cleaner cover"),
    ("0", "Remove the wing nut and air filter assembly"),
    ("0", "Separate the inner paper filter from the outer foam filter. Carefully check both filters for holes or tears and replace if damaged."),
    ("0", "Separate the inner paper filter from the outer foam filter."),
    ("0", "Remove the wing nut and air filter assembly."),
    ("0", "Remove the nut and the air cleaner cover."),
]

client = hl2ss.ipc_umq(host, hl2ss.IPCPort.UNITY_MESSAGE_QUEUE)
client.open()

cb = hl2ss_aarui.command_buffer()
cb.initialize()
cb.set_tasks(tasks)

client.push(cb)
result = client.pull(cb)
print(f'Server response: {result}')

client.close()
