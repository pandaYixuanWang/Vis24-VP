import pandas as pd
import os
import cairocffi as cairo
import subprocess
from sqlalchemy import over
import yaml
import os
import re
from pathlib import Path
import os.path as osp
from glob import glob
from tqdm import tqdm
from subprocess import call
from shutil import copy2
from utils import subtitle_delay, merge_subtitles

IMG_BG_NAME = 'preview-background-2022.png'
VIDEO_DIR = 'Video and Subtitles by Session/POSTERS'
CSV_FILE = 'Metadata Sheet (ALL COMBINED).xlsx'
SHEET_NAME = 'Posters'
OUTPUT_DIR = 'output/POSTERS'
title_img_dir = osp.join(OUTPUT_DIR, 'title_img')
merged_video_dir = osp.join(OUTPUT_DIR, 'merged')
Path(title_img_dir).mkdir(parents=True, exist_ok=True)
Path(merged_video_dir).mkdir(parents=True, exist_ok=True)

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


def generate_img(title_data, overwrite=False):

    # png_file = osp.join(title_img_dir, Path(title_data[3]).stem + '.png')
    png_file = osp.join(Path(title_data[5]).parent, Path(title_data[5]).stem + '.png')

    if osp.exists(png_file) and not overwrite:
        return
   
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

    draw_text( [title_data[0].upper()], 125, 400, 50 )

    # draw awards information
    if(title_data[6] == 'Best Paper' or title_data[6] == 'Honorable Mention'):
        x = 0

        if (title_data[6] == 'Best Paper'):    
            x = 1450
            ctx.rectangle( x, 385, 360, 95 )
        elif (title_data[6] == 'Honorable Mention'):
            x = 1220
            ctx.rectangle( x, 385, 590, 95 )

        # Background Colour:
        # ctx.set_source_rgba(0.114, 0.192, 0.376, 1) # Dark Blue Background
        ctx.set_source_rgba(0.13, 0.447, 0.725, 1) # Light Blue Background
        ctx.fill()
        
        ctx.select_font_face( "Tahoma" )
        # Text Colour:
        ctx.set_source_rgba( 0.992, 0.7294, 0.192, 1 ) # Gold Text
        # ctx.set_source_rgba(0.114, 0.192, 0.376, 1) # Dark Blue Text
        # ctx.set_source_rgba( 0.945, 0.341, 0.133, 1 ) # Orange Text
        
        # Position: same line with paper type
        fontsize = 50
        ctx.set_font_size( fontsize )
        draw_text( [title_data[6].upper()], x + 40, 400, fontsize )

        ## Position: top right corner
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
        lines = linebreak( title_data[1], 1450 )

        if len(lines) < 4:
            break

    if len(lines) == 1:
        draw_text( lines, 125, 550, fontsize )
    else:
        draw_text( lines, 125, 700-1.2*fontsize*len(lines), fontsize )
    

    # draw authors
    ctx.select_font_face( "Tahoma" )
    ctx.set_source_rgba( 0.114, 0.192, 0.376, 1)

    for author_fontsize in range( 50, 40, -2 ):

        ctx.set_font_size( author_fontsize )
        lines = linebreak( title_data[2], 1900, ',' )

        if len(lines) < 4:
            break

    draw_text( lines, 125, 725, 35 )
    
    
    # draw session info
    ctx.select_font_face( "Tahoma" )
    ctx.set_source_rgba( 0, 0, 0, 1 )

    for session_fontsize in range( 80, 40, -2 ):

        ctx.set_font_size( session_fontsize )
        lines = linebreak( title_data[4], 3000)

        if len(lines) < 4:
            break

    draw_text( lines, 125, 875, 40 )

    final.write_to_png( png_file )
    copy2(png_file, osp.join(title_img_dir, Path(title_data[5]).stem + '.png'))


def generate_video(title_data, overwrite=False):
    
    # use FFMPEG to prepend image to video
    # filter syntax: https://ffmpeg.org/ffmpeg-filters.html#Filtergraph-syntax-1
    
    # check if preview already exists
    
    outfile = osp.join( title_data[5] )
    

    if not overwrite and osp.exists( outfile ):
        return f'preview found in {outfile}'

    # png_file = osp.join(title_img_dir, Path(title_data[3]).stem + '.png')
    png_file = osp.join(Path(title_data[5]).parent, Path(title_data[5]).stem + '.png')

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
        call(cmd)
        return f'generate {outfile}'
    except Exception as e:
        # on error, delete the output file
        os.unlink( outfile )
        return f'failed to generate {outfile}'



    

def check(video_filename):
    if not osp.exists(video_filename): return False
    return True
    # return osp.exists(video_filename.replace('.mp4', '.srt')) or osp.exists(video_filename.replace('.mp4', '.sbv'))


def get_video_filename(input_dir, filename):
    result = list(glob(osp.join(input_dir, filename + '*.mp4')))
    if len(result) == 1: return Path(result[0]).name
    return ''


# def type_convert(session_id):
#     if 'cga' in session_id: return 'CG&A Paper'
#     if 'short' in session_id: return 'VIS Short Paper'
#     if 'sig' in session_id: return 'SIGGRAPH Paper'
#     if 'vr' in session_id: return 'VR Paper'
#     if 'full' in session_id: return 'VIS Full Paper'
#     raise NotImplementedError('unknown session_id: ', session_id)





def time_convert(session_time):
    TIME_MAP = {
        '1': '09:00-10:15',
        '2': '10:45-12:00',
        '3': '14:00-15:15',
        '4': '15:45-17:00',
    }
    if session_time[-1] in TIME_MAP: return TIME_MAP[session_time[-1]]
    raise NotImplementedError('unknown session_time:', session_time)


def session_folder_convert(session_id, session_name):
    return session_name + " Posters"

def get_duration(filename):
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
    raw_info = yaml.load(out, Loader=yaml.FullLoader)
    duration = float( raw_info['format']['duration'] )
    return duration

def merge(df, session_id, overwrite=False, strict=False):
    df = df.loc[df['session_id'] == session_id]
    assert df.shape[0] > 0
    session_name = list(df['session_name'])[0]
    session_folder = session_folder_convert(session_id, session_name)
    output_vid_dir = osp.join(OUTPUT_DIR, session_folder)
    filelist = [osp.join(output_vid_dir, get_video_filename(output_vid_dir, str(row['paper_id']))) for index, row in df.iterrows()]
    if not all(['.mp4' in filename for filename in filelist]):
        paper_ids = [row['paper_id'] for index, row in df.iterrows() if '.mp4' not in get_video_filename(output_vid_dir, str(row['paper_id']))]
        if strict: return f'Skip {session_folder} due to missing videos: {",".join(paper_ids)}'
        else: print(f'Some videos are missing in {session_folder} : {",".join(paper_ids)}. Still generating though.')
    filelist = [filename for filename in filelist if '.mp4' in filename]
    n = len(filelist)
    print(filelist, n)
    durations = [get_duration(filename) for filename in filelist]
    outfile = osp.join(output_vid_dir, f'{session_folder}.mp4').replace('-', '_')

    merge_subtitles([filename.replace('.mp4', '.srt') for filename in filelist], durations, outfile.replace('.mp4','.srt'))
    copy2(outfile.replace('.mp4','.srt'), merged_video_dir)
    if not overwrite and osp.exists(outfile):
        return f'merged video found in {outfile}'
    cmd = ['ffmpeg']
    for filename in filelist: cmd.append('-i'); cmd.append(filename)
    cmd = cmd + [
        '-filter_complex', ''.join([f'[{i}:v] [{i}:a] ' for i in range(n)]) + f'concat=n={n}:v=1:a=1 [v] [a]',
        '-map', '[v]',
        '-map', '[a]',
        '-y', outfile
    ]
    try:
        call(cmd)
        copy2(outfile, osp.join(merged_video_dir, f'{session_folder}.mp4'))
        return f'generate {outfile} successfully'
    except Exception as e:
        # on error, delete the output file
        os.unlink( outfile )
        return f'failed to generate {outfile}'
    





if __name__ == '__main__':
    df = pd.read_excel(open(CSV_FILE, 'rb'),sheet_name=SHEET_NAME, engine='openpyxl')
    cnt = 0
    clean_df = df.loc[df['paper_id'].notna()]
    session_time = None
    session_date = None
    n_total = clean_df.shape[0]
    print(n_total)
    for index, (_, row) in enumerate(clean_df.iterrows()):
        session_folder = session_folder_convert(row['session_id'], row['session_name'])
        if session_folder == '':
            print(f'[{index}/{n_total}]', f'Error: could not find folder {session_folder}')
            continue
        input_vid_dir = osp.join(VIDEO_DIR, session_folder)
        output_vid_dir = osp.join(OUTPUT_DIR, session_folder)
        Path(output_vid_dir).mkdir(parents=True, exist_ok=True)
        video_filename = get_video_filename(input_vid_dir, row['paper_id'])
        input_video_filename = osp.join(input_vid_dir, video_filename)
        output_video_filename = osp.join(output_vid_dir, video_filename)
        if video_filename == '' or not check(input_video_filename):
            print(f'[{index}/{n_total}]', f'Error: could not find video for {input_video_filename}, {video_filename}, {row["paper_id"]}')
            continue
        video_metadata = [session_folder,
                        row['title'],
                        row['authors'],
                        input_video_filename,
                        '',
                        output_video_filename,
                        ''
                        ]
        try:
            generate_img(video_metadata)
            msg = generate_video(video_metadata)
            subtitle_delay(video_filename, input_vid_dir, output_vid_dir)
            print(f'[{index}/{n_total}]', msg)
            cnt += 1
        except Exception as e:
            print(input_video_filename)
            raise Exception(e)
    print(f"process {cnt} files successfully")
    for session_id in sorted(set(clean_df['session_id'])):
        msg = merge(clean_df, session_id)
        print(msg)