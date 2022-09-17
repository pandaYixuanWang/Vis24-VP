from ctypes import alignment
from tkinter import CENTER
import pandas as pd
import os
import cairocffi as cairo
import subprocess
import yaml
import os
import re
from pathlib import Path
import os.path as osp
from glob import glob

IMG_BG_NAME = 'preview-background-2022.png'
CSV_FILE = 'Session Breakdown.xlsx'
SHEET_NAME = 'LATEST'
VIDEO_DIR = 'Video and Subtitles by Session'
OUTPUT_DIR = 'output'
title_img_dir = osp.join(OUTPUT_DIR, 'title_img')
Path(title_img_dir).mkdir(parents=True, exist_ok=True)

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


def generate_img(title_data):
   
    final = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    ctx = cairo.Context(final)

    def linebreak(text, max_width, sep=' '):
        lines = []

        for text in text.split("\\n"):
            tokens = text.split(sep)
            line = []

            for token in tokens:
                extline = line + [token]
                width = ctx.text_extents(sep.join(extline))[2]

                if width > max_width:
                    lines.append((sep.join(line) + sep))
                    line = [token]
                else:
                    line = extline

            lines.append(sep.join(line))

        return [l.strip() for l in lines]

    def draw_text(text, x, y, size):

        ctx.set_font_size(size)

        y += ctx.font_extents()[0]

        for num, line in enumerate(text):
            ctx.move_to(x, y)
            ctx.show_text(line)
            y = y + 1.2 * size

    img_bkgnd = cairo.ImageSurface.create_from_png( IMG_BG_NAME )

    # clear image
    ctx.rectangle( 0, 0, 1920, 1080 )
    ctx.set_source_rgba( 0, 0, 0, 1 )
    ctx.fill()

    ctx.set_source_surface( img_bkgnd )
    ctx.paint()

    # draw paper type
    ctx.select_font_face( "Tahoma Bold" )
    ctx.set_font_size( 50 )
    ctx.set_source_rgba( 0, 0, 0, 1 )

    draw_text( [title_data[0].upper()], 300, 400, 50 )

    # draw awards information
    if(title_data[6] == 'Best Paper' or title_data[6] == 'Honorable Mention'):
        ctx.select_font_face( "Tahoma" )
        ctx.set_source_rgba( 0.992, 0.7294, 0.192, 1 )

        # same line with type
        fontsize = 50
        ctx.set_font_size( fontsize )
        draw_text( [title_data[6].upper()], 900, 400, fontsize )

        # top right corner
        # fontsize = 80
        # ctx.set_font_size( fontsize )
        # lines = linebreak( title_data[6].upper(), 600)

        # if (title_data[6] == 'Honorable Mention'):
        #     draw_text( lines, 1350, 100, fontsize )
        # elif (title_data[6] == 'Best Paper'):
        #     draw_text( lines, 1350, 200, fontsize )
        
    # draw title
    ctx.select_font_face( "Tahoma" )
    ctx.set_source_rgba( 0.64, 0.04, 0.21, 1 )

    for fontsize in range( 60, 50, -2 ):

        ctx.set_font_size( fontsize )
        lines = linebreak( title_data[1], 1300 )

        if len(lines) < 4:
            break

    if len(lines) == 1:
        draw_text( lines, 300, 550, fontsize )
    else:
        draw_text( lines, 300, 700-1.2*fontsize*len(lines), fontsize )
    # if len(lines) > 2:
    #     ctx.translate( 0,  0.3*fontsize )
    # if len(lines) < 1:
    #     ctx.translate( 0,  0.3*fontsize )

    

    # draw authors
    ctx.select_font_face( "Tahoma" )
    ctx.set_source_rgba( 0.114, 0.192, 0.376, 1)

    for author_fontsize in range( 50, 40, -2 ):

        ctx.set_font_size( author_fontsize )
        lines = linebreak( title_data[2], 1500, ',' )

        if len(lines) < 4:
            break

    draw_text( lines, 300, 725, 35 )
    
    
    # draw session info
    ctx.select_font_face( "Tahoma" )
    ctx.set_source_rgba( 0, 0, 0, 1 )

    for session_fontsize in range( 80, 40, -2 ):

        ctx.set_font_size( session_fontsize )
        lines = linebreak( title_data[4], 2000)

        if len(lines) < 4:
            break

    draw_text( lines, 300, 875, 40 )

    png_file = osp.join(title_img_dir, Path(title_data[3]).stem + '.png')

    final.write_to_png( png_file )


def generate_video(title_data, overwrite=False):
    
    # use FFMPEG to prepend image to video
    # filter syntax: https://ffmpeg.org/ffmpeg-filters.html#Filtergraph-syntax-1
    
    # check if preview already exists
    
    outfile = osp.join( title_data[5] )
    

    if not overwrite and osp.exists( outfile ):
        print( '  preview found in', outfile )
        return

    png_file = title_img_dir + Path(title_data[3]).stem + '.png'

    input_file = title_data[3]
    info = probe( input_file )
    
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
        '-i', input_file,
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
        p = subprocess.Popen( cmd )
        p.wait()
    except:
        # on error, delete the output file
        os.unlink( outfile )
        print( '  abort, deleted', outfile )
        raise


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
        raise NotImplementedError('unhandle subtitles', line)
        
        
    with open(filename, encoding='utf8') as f:
        lines = f.readlines()
    lines = [line_delay(line, seconds) for line in lines]
    with open(output_filename, 'w', encoding='utf8') as f:
        f.writelines(lines)


def sbv_delay(filename, output_filename, seconds=5):
    def line_delay(line, seconds):
        # only 25 + 5 seconds so we simplify the logic here
        PATTERN = '(\d+):(\d+):(\d+).(\d+),(\d+):(\d+):(\d+).(\d+)'
        if '-->' not in line: return line
        res = re.search(PATTERN, line)
        if res is not None: return f'{res.group(1)}:{res.group(2)}:{int(res.group(3))+seconds:02}.{res.group(4)},{res.group(5)}:{res.group(6)}:{int(res.group(7))+seconds:02}.{res.group(8)}\n'
        raise NotImplementedError('unhandle subtitles', line)
        
    with open(filename, encoding='utf8') as f:
        lines = f.readlines()
    lines = [line_delay(line, seconds) for line in lines]
    with open(output_filename, 'w', encoding='utf8') as f:
        f.writelines(lines)


def subtitle_delay(filename, input_dir, output_dir):
    print(filename)
    if '.mp4' in filename: filename = filename.replace('.mp4', '')
    if osp.exists(osp.join(input_dir, filename + '.srt')):
        srt_delay(osp.join(input_dir, filename + '.srt'), osp.join(output_dir, filename + '.srt'))
    elif osp.exists(osp.join(input_dir, filename + '.sbv')):
        sbv_delay(osp.join(input_dir, filename + '.sbv'), osp.join(output_dir, filename + '.sbv'))
    else:
        print(f'Error: No subtitle is found for {osp.join(input_dir, filename)}')
        return
    

def check(video_filename):
    if not osp.exists(video_filename): return False
    return osp.exists(video_filename.replace('.mp4', '.srt')) or osp.exists(video_filename.replace('.mp4', '.sbv'))

# if __name__ == '__main__':
#     df = pd.read_excel(open(CSV_FILE, 'rb'),sheet_name='VP_ShortPaper', engine='openpyxl')
#     clean_df = df.loc[df['Filename'].notna()]
#     for index, row in clean_df.iterrows():
#         input_video_filename = osp.join(input_vid_dir, row['Filename'])
#         input_video_filename = osp.join(output_vid_dir, row['Filename'])
#         if not check(input_video_filename):
#             print(f"Error: missing files for {input_video_filename}")
#             continue
#         video_metadata = [row['Type'],
#                         row['Title'],
#                         row['Authors'],
#                         input_video_filename,
#                         row['Session Name'] + ': ' + row['Session Time'],
#                         #'Social Sciences, Software Tools, Journalism, and Storytelling: Friday, 0815 - 0830',
#                         output_vid_dir,
#                         row['Award']
#                         ]
#         print(index, video_metadata, '\n\n')
#         generate_img(video_metadata)
#         generate_video(video_metadata)
#         srt_delay(row['Filename'], input_vid_dir, output_vid_dir)
def get_video_filename(input_dir, filename):
    result = list(glob(osp.join(input_dir, filename + '*Preview.mp4')))
    if len(result) == 1: return Path(result[0]).name
    return ''

def type_convert(session_id):
    if 'cga' in session_id: return 'CG&A Paper'
    if 'short' in session_id: return 'VIS Short Paper'
    if 'sig' in session_id: return 'SIGGRAPH Paper'
    if 'vr' in session_id: return 'VR Paper'
    if 'full' in session_id: return 'VIS Full Paper'
    raise NotImplementedError('unknown session_id: ', session_id)

def time_convert(session_time):
    TIME_MAP = {
        '1': '0900-1015',
        '2': '1045-1200',
        '3': '1400-1515',
        '4': '1545-1700',
    }
    if session_time[-1] in TIME_MAP: return TIME_MAP[session_time[-1]]
    raise NotImplementedError('unknown session_time:', session_time)

def session_folder_convert(session_id, session_name):
    folder_name = f"{session_id}-{session_name}"
    if osp.exists(osp.join(VIDEO_DIR, folder_name)): return folder_name
    if osp.exists(osp.join(VIDEO_DIR, folder_name.replace('/', '-'))): return folder_name.replace('/', '-')
    if osp.exists(osp.join(VIDEO_DIR, folder_name.replace('/', '~'))): return folder_name.replace('/', '~')
    folder = glob(osp.join(VIDEO_DIR, session_id+'-*'))
    if len(folder) == 1:
        folder = Path(folder[0]).name
        print('Warning: possibly incorrect folder name:', folder_name, folder)
        return folder
    else:
        print("Error: fail to match folder name: ", folder_name)
        return ''
        # raise NotImplementedError('unknown folder_name:', folder_name)


if __name__ == '__main__':
    df = pd.read_excel(open(CSV_FILE, 'rb'),sheet_name=SHEET_NAME, engine='openpyxl')
    cnt = 0
    clean_df = df.loc[df['paper_id'].notna()]
    session_time = None
    for index, row in clean_df.iterrows():
        if not pd.isna(row['session']): session_time = time_convert(row['session'])
        session_folder = session_folder_convert(row['session_id'], row['session_name'])
        if session_folder == '':
            continue
        input_vid_dir = osp.join(VIDEO_DIR, session_folder)
        output_vid_dir = osp.join(OUTPUT_DIR, session_folder)
        Path(output_vid_dir).mkdir(parents=True, exist_ok=True)
        video_filename = get_video_filename(input_vid_dir, row['paper_id'])
        input_video_filename = osp.join(input_vid_dir, video_filename)
        output_video_filename = osp.join(output_vid_dir, video_filename)
        if video_filename == '' or not check(input_video_filename):
            # print(f"Error: missing files for {input_video_filename}")
            continue
        video_metadata = [type_convert(row['session_id']),
                        row['title'],
                        row['authors'],
                        input_video_filename,
                        row['session_name'] + ': ' + session_time,
                        #'Social Sciences, Software Tools, Journalism, and Storytelling: Friday, 0815 - 0830',
                        output_video_filename,
                        ''#row['Award']
                        ]
        # print(index, video_metadata, '\n\n')
        generate_img(video_metadata)
        # generate_video(video_metadata)
        # subtitle_delay(video_filename, input_vid_dir, output_vid_dir)
    