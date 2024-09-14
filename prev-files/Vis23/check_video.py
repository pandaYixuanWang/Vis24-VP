import subprocess
import yaml

def probe( filename ):
    '''get some information about a video file'''
    proc = subprocess.Popen( [
            'ffprobe', 
            '-show_format',
            '-show_streams',
            '-print_format', 'json',
            '-i', filename
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE )

    out, err = proc.communicate()
    if proc.returncode:
        return None

    raw_info = yaml.load(out, Loader=yaml.FullLoader)
    for s in raw_info['streams']:
        if s['codec_type'] == 'video':
            if 'display_aspect_ratio' in s:
                dar = s['display_aspect_ratio']
            else:
                dar = int( s['width'] ) / int( s['height'] )
            fps    = s['r_frame_rate']
            duration = raw_info['format']['duration']
            print(filename, dar, fps, duration)

def check(folder):
    from glob import glob
    files = glob(folder+'/*.mp4')
    for file in files:
        probe(file)

check(r'Video and Subtitles by Session\ASSOCIATED EVENTS\Vis4Good')