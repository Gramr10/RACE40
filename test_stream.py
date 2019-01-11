import io
import random
import picamera

# IMPORTANT: This file is a staring point for the module that shall be used to record the track.
# When in "learning mode" this module has to initiate recording. There should be 2 threads (one recording, and one storing the previous recording)

counter = 0

def write_now():
    # Randomly return True (like a fake motion detection routine)
    return random.randint(0, 10) == 0

def write_video(stream):
    print('Writing video!')
    with stream.lock:
        # Find the first header frame in the video
        for frame in stream.frames:
            if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                stream.seek(frame.position)
                break
        # Write the rest of the stream to disk
        global counter
        counter = counter + 1
        name = 'image' + str(counter) + '.h264'
        with io.open(name, 'wb') as output:
            output.write(stream.read())

stream = io.BytesIO()

with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.framerate = 80
    stream = picamera.PiCameraCircularIO(camera, seconds=20)
    camera.start_recording(stream, format='h264')
    try:
        while True:
            camera.wait_recording(1)
            if write_now():
                # Keep recording for 10 seconds and only then write the
                # stream to disk
                camera.wait_recording(5)
                write_video(stream)
                print('Ha!')
    finally:
        camera.stop_recording()
