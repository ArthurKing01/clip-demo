import ffmpeg
import numpy as np
import os

_ffmpeg_video_args = {}
_ffmpeg_video_args.setdefault('format', 'rawvideo')
_ffmpeg_video_args.setdefault('pix_fmt', 'rgb24')
_ffmpeg_video_args.setdefault('frame_pts', True)
_ffmpeg_video_args.setdefault('vsync', 0)
_ffmpeg_video_args.setdefault('vf', f'fps={1}')

def getVideoFrames(p: str):
    ffmpeg_args = _ffmpeg_video_args
    try:
        video = ffmpeg.probe(p)['streams'][0]
        w, h = ffmpeg_args.get('s', f'{video["width"]}x{video["height"]}').split('x')
        w = int(w)
        h = int(h)
        out, _ = (
                    ffmpeg.input(p)
                    .output('pipe:', **ffmpeg_args)
                    .run(capture_stdout=True,capture_stderr=True, quiet=True)
                )
        video_frames = np.frombuffer(out, np.uint8).reshape([-1, h, w, 3])
    except Exception as e:
        print(e)
        raise e
    return video_frames

def cutVideo(start_t: str, length: int, input: str, output: str):
    os.system(f'ffmpeg -ss {start_t} -i {input} -t {length} -c:v copy -c:a copy output/{output}')
    # ffmpeg -ss 1:05 -i input.mp4 -t 10 -c:v copy -c:a copy output.mp4

def convertToTs(input: str):
    basename = os.path.basename(input)
    new_name = basename.split('.')[0] + '.ts'
    os.system(f'ffmpeg -i {input} -vcodec copy -acodec copy -vbsf h264_mp4toannexb output/{new_name}')
    return new_name

def mergeVideo(inputs: list[str], output: str):
    # os.system(f'ffmpeg -f concat -i file.txt -c copy output/merged_{output}')
    os.system(f'ffmpeg -i "concat:{"|".join(inputs)}" -acodec copy -vcodec copy -absf aac_adtstoasc output/merged_{output}')