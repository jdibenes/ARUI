
import os
import numpy as np
import cv2
import hl2ss_imshow
import hl2ss
import hl2ss_mp
import hl2ss_io
import hl2ss_aarui

# Settings --------------------------------------------------------------------

host = '192.168.1.7'
port = hl2ss.IPCPort.UNITY_MESSAGE_QUEUE
data = './data'

video_compression_factor = 1/50

vlc_bitrate = hl2ss.get_video_codec_bitrate(hl2ss.Parameters_RM_VLC.WIDTH, hl2ss.Parameters_RM_VLC.HEIGHT, hl2ss.Parameters_RM_VLC.FPS, video_compression_factor)

pv_width = 1280
pv_height = 720
pv_framerate = 30
pv_bitrate = hl2ss.get_video_codec_bitrate(pv_width, pv_height, pv_framerate, video_compression_factor)

ports = [
    hl2ss.StreamPort.RM_VLC_LEFTFRONT,
    hl2ss.StreamPort.RM_VLC_RIGHTFRONT,
    hl2ss.StreamPort.RM_DEPTH_LONGTHROW,
    hl2ss.StreamPort.PERSONAL_VIDEO,
    hl2ss.StreamPort.MICROPHONE,
]

tasks = [
    ("0", "Remove the nut and the air cleaner cover"),
    ("0", "Remove the wing nut and air filter assembly"),
    ("0", "Separate the inner paper filter from the outer foam filter. Carefully check both filters for holes or tears and replace if damaged."),
    ("0", "Separate the inner paper filter from the outer foam filter."),
    ("0", "Remove the wing nut and air filter assembly."),
    ("0", "Remove the nut and the air cleaner cover."),
]

#------------------------------------------------------------------------------

if __name__ == '__main__':
    hl2ss.start_subsystem_pv(host, hl2ss.StreamPort.PERSONAL_VIDEO)

    client = hl2ss.ipc_umq(host, port)
    client.open()

    cb = hl2ss_aarui.command_buffer()
    cb.initialize()
    cb.set_tasks(tasks)

    client.push(cb)
    result = client.pull(cb)
    print(f'Server response: {result}')

    client.close()

    #

    producer = hl2ss_mp.producer()
    producer.configure_rm_vlc(False, host, hl2ss.StreamPort.RM_VLC_LEFTFRONT, hl2ss.ChunkSize.RM_VLC, hl2ss.StreamMode.MODE_1, hl2ss.VideoProfile.H265_MAIN, vlc_bitrate)
    producer.configure_rm_vlc(False, host, hl2ss.StreamPort.RM_VLC_LEFTLEFT, hl2ss.ChunkSize.RM_VLC, hl2ss.StreamMode.MODE_1, hl2ss.VideoProfile.H265_MAIN, vlc_bitrate)
    producer.configure_rm_vlc(False, host, hl2ss.StreamPort.RM_VLC_RIGHTFRONT, hl2ss.ChunkSize.RM_VLC, hl2ss.StreamMode.MODE_1, hl2ss.VideoProfile.H265_MAIN, vlc_bitrate)
    producer.configure_rm_vlc(False, host, hl2ss.StreamPort.RM_VLC_RIGHTRIGHT, hl2ss.ChunkSize.RM_VLC, hl2ss.StreamMode.MODE_1, hl2ss.VideoProfile.H265_MAIN, vlc_bitrate)
    producer.configure_rm_depth_longthrow(False, host, hl2ss.StreamPort.RM_DEPTH_LONGTHROW, hl2ss.ChunkSize.RM_DEPTH_LONGTHROW, hl2ss.StreamMode.MODE_1, hl2ss.PngFilterMode.Paeth)
    producer.configure_rm_imu(host, hl2ss.StreamPort.RM_IMU_ACCELEROMETER, hl2ss.ChunkSize.RM_IMU_ACCELEROMETER, hl2ss.StreamMode.MODE_1)
    producer.configure_rm_imu(host, hl2ss.StreamPort.RM_IMU_GYROSCOPE, hl2ss.ChunkSize.RM_IMU_GYROSCOPE, hl2ss.StreamMode.MODE_1)
    producer.configure_rm_imu(host, hl2ss.StreamPort.RM_IMU_MAGNETOMETER, hl2ss.ChunkSize.RM_IMU_MAGNETOMETER, hl2ss.StreamMode.MODE_1)
    producer.configure_pv(False, host, hl2ss.StreamPort.PERSONAL_VIDEO, hl2ss.ChunkSize.PERSONAL_VIDEO, hl2ss.StreamMode.MODE_1, pv_width, pv_height, pv_framerate, hl2ss.VideoProfile.H265_MAIN, pv_bitrate, 'bgr24')
    producer.configure_microphone(False, host, hl2ss.StreamPort.MICROPHONE, hl2ss.ChunkSize.MICROPHONE, hl2ss.AudioProfile.AAC_24000)
    producer.configure_si(host, hl2ss.StreamPort.SPATIAL_INPUT, hl2ss.ChunkSize.SPATIAL_INPUT)

    for port in ports:
        producer.initialize(port, 256)

    for port in ports:
        producer.start(port)

    wr = {port : hl2ss_io.wr_process_producer(os.path.join(data, f'{hl2ss.get_port_name(port)}.bin'), producer, port, 'aarui_multirecorder'.encode('utf-8')) for port in ports}

    for port in ports:
        wr[port].start()

    while (True):
        cv2.imshow('dummy', np.zeros((32, 32), dtype=np.uint8))
        key = cv2.waitKey(1)
        if ((key & 0xFF) == 27):
            break

    for port in ports:
        wr[port].stop()

    for port in ports:
        wr[port].join()

    for port in ports:
        producer.stop(port)

    hl2ss.stop_subsystem_pv(host, hl2ss.StreamPort.PERSONAL_VIDEO)
