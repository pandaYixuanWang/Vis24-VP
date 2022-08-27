import pandas as pd
import os
import cairocffi as cairo
import subprocess
import yaml
import os
import re
import pathlib

IMG_BG_NAME = 'preview-background-2022.png'
CSV_FILE = 'VP_2022_metadata-TEST.xlsx'
title_img_dir = 'video_dir/title_img/'
input_vid_dir = 'video_dir/VIS Short/'
output_vid_dir = 'video_dir/VP_out_VIS Short/'
DIRS = [title_img_dir, input_vid_dir, output_vid_dir]
for dir in DIRS:
    pathlib.Path(dir).mkdir(parents=True, exist_ok=True)

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
    ctx.select_font_face( "Futura Medium" )
    ctx.set_font_size( 30 )
    ctx.set_source_rgba( 0, 0, 0, 1 )

    draw_text( [title_data[0].upper()], 1080, 112, 50 )

    # draw title
    ctx.select_font_face( "Gotham Bold" )
    ctx.set_source_rgba( 0, 0, 0, 1 )

    for fontsize in range( 60, 50, -2 ):

        ctx.set_font_size( fontsize )
        lines = linebreak( title_data[1], 1800 )

        if len(lines) < 4:
            break

    if len(lines) > 2:
        ctx.translate( 0,  0.3*fontsize )
    if len(lines) < 1:
        ctx.translate( 0,  0.3*fontsize )

    draw_text( lines, 90, 420-1.2*fontsize*len(lines), fontsize )

    # draw authors
    ctx.select_font_face( "Gotham Book" )
    ctx.set_source_rgba( 0, 0, 0, 1 )

    for author_fontsize in range( 50, 40, -2 ):

        ctx.set_font_size( author_fontsize )
        lines = linebreak( title_data[2], 1800, ',' )

        if len(lines) < 4:
            break

    draw_text( lines, 90, 480, 35 )
    
    # draw awards information
    if(title_data[6] == 'Best Paper' or title_data[6] == 'Honorable Mention'):
        ctx.select_font_face( "Gotham Bold" )
        ctx.set_source_rgba( 0, 0, 0, 1 )

        for session_fontsize in range( 60, 50, -2 ):

            ctx.set_font_size( session_fontsize )
            lines = linebreak( '*'+title_data[6], 1800, ',' )

            if len(lines) < 4:
                break

        draw_text( lines, 90, 570, 40 )
    
    # draw session info
    ctx.select_font_face( "Gotham Bold" )
    ctx.set_source_rgba( 0, 0, 0, 1 )

    for session_fontsize in range( 80, 40, -2 ):

        ctx.set_font_size( session_fontsize )
        lines = linebreak( title_data[4], 1800, ',' )

        if len(lines) < 4:
            break

    draw_text( lines, 90, 700, 40 )

    png_file = title_img_dir + pathlib.Path(title_data[3]).stem + '.png'

    final.write_to_png( png_file )



def generate_video(title_data, overwrite=False):
    
    # use FFMPEG to prepend image to video
    # filter syntax: https://ffmpeg.org/ffmpeg-filters.html#Filtergraph-syntax-1
    
    # check if preview already exists
    
    outfile = os.path.join( title_data[5] )
    

    if not overwrite and os.path.exists( outfile ):
        print( '  preview found in', outfile )
        return

    png_file = title_img_dir + pathlib.Path(title_data[3]).stem.replace('.mp4','.png')

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
        PATTERN = '(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)'
        if '-->' not in line: return line
        res = re.search(PATTERN, line)
        # only 25 + 5 seconds so we simplify the logic here
        return f'{res.group(1)}:{res.group(2)}:{int(res.group(3))+seconds:02},{res.group(4)} --> {res.group(5)}:{res.group(6)}:{int(res.group(7))+seconds:02},{res.group(8)}\n'
        
    with open(filename, encoding='utf8') as f:
        lines = f.readlines()
    lines = [line_delay(line, seconds) for line in lines]
    with open(output_filename, 'w', encoding='utf8') as f:
        f.writelines(lines)

if __name__ == '__main__':
    df = pd.read_excel(open(CSV_FILE, 'rb'),sheet_name='VP_ShortPaper', engine='openpyxl')
    clean_df = df.loc[df['Filename'].notna()]
    for index, row in clean_df.iterrows():

        video_metadata = [row['Type'],
                        row['Title'],
                        row['Authors'],
                        input_vid_dir + row['Filename'],
                        row['Session Name'] + ': ' + row['Session Time'],
                        #'Social Sciences, Software Tools, Journalism, and Storytelling: Friday, 0815 - 0830',
                        output_vid_dir + row['Filename'],
                        row['Award']
                        ]
        print(index, video_metadata, '\n\n')
        generate_img(video_metadata)
        # generate_video(video_metadata)
        srt_delay(input_vid_dir + row['Filename'].replace('.mp4','.srt'), output_vid_dir + row['Filename'].replace('.mp4','.srt'))
    
    
    