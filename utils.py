import os.path as osp
import re
from pathlib import Path
from subprocess import call
import subprocess
import yaml

def srt_delay(filename, output_filename, seconds=5):
    
    def line_delay(line, seconds):
        # only 25 + 5 seconds so we simplify the logic here
        if '-->' not in line: return line
        PATTERN = '(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)'
        res = re.search(PATTERN, line)
        if res is not None: return f'{res.group(1)}:{res.group(2)}:{int(res.group(3))+seconds:02},{res.group(4)} --> {res.group(5)}:{res.group(6)}:{int(res.group(7))+seconds:02},{res.group(8)}\n'
        PATTERN = '(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+)'
        res = re.search(PATTERN, line)
        if res is not None: return f'{res.group(1)}:{res.group(2)}:{int(res.group(3))+seconds:02},{res.group(4)} --> {res.group(5)}:{res.group(6)}:{int(res.group(7))+seconds:02},{0}\n'
        PATTERN = '(\d+):(\d+),(\d+) --> (\d+):(\d+),(\d+)'
        res = re.search(PATTERN, line)
        if res is not None: return f'0:{res.group(1)}:{int(res.group(2))+seconds:02},{res.group(3)} --> {0}:{res.group(4)}:{int(res.group(5))+seconds:02},{res.group(6)}\n'
        PATTERN = '(\d+):(\d+):(\d+) --> (\d+):(\d+):(\d+)'
        res = re.search(PATTERN, line)
        if res is not None: return f'{res.group(1)}:{res.group(2)}:{int(res.group(3))+seconds:02},0 --> {res.group(4)}:{res.group(5)}:{int(res.group(6))+seconds:02},0\n'
        raise NotImplementedError('unhandle subtitles', line)
    if not osp.exists(filename):
        print("script not found: ", filename)
        return

    with open(filename, encoding='utf8', errors='replace') as f:
        lines = f.readlines()
    lines = [line_delay(line, seconds) for line in lines]
    with open(output_filename, 'w', encoding='utf8') as f:
        f.writelines(lines)


def sbv_delay(filename, output_filename, seconds=5):
    def line_delay(line, seconds):
        # only 25 + 5 seconds so we simplify the logic here
        PATTERN = '(\d+):(\d+):(\d+).(\d+),(\d+):(\d+):(\d+).(\d+)'
        res = re.search(PATTERN, line)
        if res is not None: 
            return f'{res.group(1)}:{res.group(2)}:{int(res.group(3))+seconds:02},{res.group(4)} --> {res.group(5)}:{res.group(6)}:{int(res.group(7))+seconds:02}.{res.group(8)}\n'
        if line.count(':') < 2: return line
        raise NotImplementedError('unhandle subtitles', line)
        
    with open(filename, encoding='utf8') as f:
        lines = f.readlines()
    lines = [line_delay(line, seconds) for line in lines]
    COUNTER = 1
    ret = []
    for line in lines:
        if '-->' not in line:
            ret.append(line)
        else:
            ret.append(str(COUNTER)+'\n')
            ret.append(line)
            COUNTER += 1

    with open(output_filename.replace('sbv', 'srt'), 'w', encoding='utf8') as f:
        f.writelines(ret)


def subtitle_delay(filename, input_dir, output_dir, overwrite=False):
    if '.mp4' in filename: filename = filename.replace('.mp4', '')
    if osp.exists(osp.join(output_dir, filename + '.srt')) and not overwrite: 
        return
    if osp.exists(osp.join(input_dir, filename + '.srt')):
        srt_delay(osp.join(input_dir, filename + '.srt'), osp.join(output_dir, filename + '.srt'))
    elif osp.exists(osp.join(input_dir, filename + '.sbv')):
        sbv_delay(osp.join(input_dir, filename + '.sbv'), osp.join(output_dir, filename + '.sbv'))
    else:
        print(f'Error: No subtitle is found for {osp.join(input_dir, filename)}')
        return



def merge_subtitles(files, durations, outfile):
    def time_delay(t1, t2):
        h1, m1, s1, ms1 = t1
        h2, m2, s2, ms2 = t2
        ms = (ms1 + ms2)
        s = (s1 + s2 + ms // 1000)
        m = (m1 + m2 + s // 60)
        h = (h1 + h2 + m // 60)
        return h, m%60, s%60, ms%1000
    def time2str(t):
        return f'{t[0]}:{t[1]:02}:{t[2]:02},{t[3]:03}'
    def line_delay(line, t):
        PATTERN = '(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)'
        res = re.search(PATTERN, line)
        if res is not None:
            h1, m1, s1, ms1 = int(res.group(1)), int(res.group(2)), int(res.group(3)), int(res.group(4))
            h2, m2, s2, ms2 = int(res.group(5)), int(res.group(6)), int(res.group(7)), int(res.group(8))
            return f'{time2str(time_delay((h1,m1,s1,ms1), t))} --> {time2str(time_delay((h2,m2,s2,ms2), t))}\n'
        raise Exception('error in sparse time: ', line)
    accumulate_t = 0
    t = (0, 0, 0, 0)
    counter = 1
    lines = []
    for i, file in enumerate(files):
        if osp.exists(file):
            with open(file, encoding='utf8') as f:
                for line in f.readlines():
                    if len(line.strip()) < 3 and line.strip().isdigit():
                        lines.append(f'{counter}\n')
                        counter += 1
                    elif '-->' in line:
                        lines.append(line_delay(line, t))
                    else:
                        lines.append(line)
            lines.append('\n')
        accumulate_t += durations[i]
        t = (int(accumulate_t//3600), int(accumulate_t//60) % 60, int(accumulate_t) % 60, int(1000*accumulate_t) % 1000)
    
        
    with open(outfile, 'w', encoding='utf8') as f:
        f.writelines(lines)


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

    info          = dict()                
    info['video'] = dict()
    info['audio'] = dict()
    info['duration'] = float( raw_info['format']['duration'] )
    info['size']     = float( raw_info['format']['size'] ) / 1048576.

    for s in raw_info['streams']:

        if s['codec_type'] == 'video':
            info['video']['codec']  = s['codec_name']
            info['video']['format'] = s['pix_fmt']
            info['video']['width']  = int( s['width'] )
            info['video']['height'] = int( s['height'] )
            #info['video']['aspect'] = s['display_aspect_ratio']
            info['video']['fps']    = s['r_frame_rate']
            
        elif s['codec_type'] == 'audio':
            
            info['audio']['codec'] = s['codec_name']

    if 'codec' not in info['audio']:
        info['audio']['codec'] = '-'

    return info

def add_title_img(video_file, png_file=None, overwrite=False):
    
    # use FFMPEG to prepend image to video
    # filter syntax: https://ffmpeg.org/ffmpeg-filters.html#Filtergraph-syntax-1
    
    # check if preview already exists
    
    outfile = osp.join(Path(video_file).parent, Path(video_file).stem + '_cover.mp4')
    if png_file is None:
        png_file = osp.join(Path(video_file).parent, Path(video_file).stem + '.png')

    if not overwrite and osp.exists( outfile ):
        return f'preview found in {outfile}'

    info = probe( video_file )
    filter  = '[0:v]trim=duration=5,fade=t=out:st=4.5:d=0.5[v0];'
    filter += 'aevalsrc=0:d=5[a0];'
    filter += '[1:v]scale=w=1920:h=1080[v1];'

    if info['audio']['codec'] == '-':
        filter += 'aevalsrc=0:d=25[a1];'
    else:
        filter += '[1:a]anull[a1];'

    filter += '[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]'
    
    cmd = [
        'ffmpeg',
        '-v', 'error',
        '-framerate', info['video']['fps'],
        '-f', 'image2pipe',
        '-vcodec', 'png',
        '-loop', '1',
        '-i', png_file,
        '-i', video_file,
        '-filter_complex', filter,
        '-map', '[v]',
        '-map', '[a]',
        '-crf', '20',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-profile:v', 'main',
        '-preset', 'slow',
        '-y', outfile
    ]
    try:
        call(cmd)
        return f'generate {outfile}'
    except Exception as e:
        # on error, delete the output file
        return f'failed to generate {outfile}'
    