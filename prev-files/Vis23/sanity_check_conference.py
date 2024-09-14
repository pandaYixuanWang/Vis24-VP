from glob import glob
import os.path as osp
import pandas as pd
from pathlib import Path

VIDEO_DIR = 'Video and Subtitles by Session/MAIN CONFERENCE'
CSV_FILE = 'metadata-file-2023.xlsx'
SHEET_NAME = 'metadata-file'

videos = list(glob(VIDEO_DIR + '/*/v-*.mp4'))
srts = list(glob(VIDEO_DIR + '/*/*.srt'))
sbvs = list(glob(VIDEO_DIR + '/*/*.sbv'))

print(f'Video count: {len(videos)}, SRT count: {len(srts)}, SBV count: {len(sbvs)}')
unmatched_video = []
unmatched_srts = []
unmatched_sbvs = []
for video in videos:
    if video.replace('.mp4', '.srt') in srts: continue
    if video.replace('.mp4', '.sbv') in sbvs: continue
    unmatched_video.append(video)
    

print(f"There are {len(unmatched_video)} videos without subtitles")
for video in unmatched_video: print(video)

unmatched_srts = [srt for srt in srts if srt.replace('.srt', '.mp4') not in videos]
print(f"There are {len(unmatched_srts)} srts without videos")
for srt in unmatched_srts: print(srt)

unmatched_sbvs = [sbv for sbv in sbvs if sbv.replace('.sbv', '.mp4') not in videos]
print(f"There are {len(unmatched_sbvs)} sbvs without videos")
for sbv in unmatched_sbvs: print(sbv)

print("----------------------------------------")


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

df = pd.read_excel(open(CSV_FILE, 'rb'), sheet_name=SHEET_NAME, engine='openpyxl')
cnt = 0
clean_df = df.loc[df['paper_id'].notna()]
session_time = None
session_date = None
n_total = clean_df.shape[0]
EXCEL_video_msg = []
EXCEL_subtitle_msg = []
EXCEL_other_msg = []
for index, row in clean_df.iterrows():
    session_folder = session_folder_convert(row['session_id'], row['session_name'])
    video = list(glob(f'{VIDEO_DIR}/{session_folder}/{row["paper_id"]}*.mp4'))
    assert len(video) <= 1
    if len(video) == 0:
        EXCEL_video_msg.append(f'Missing video: {session_folder}/{row["paper_id"]}*.mp4')
    else:
        videos = [x for x in videos if row["paper_id"] not in x]
    srt = list(glob(f'{VIDEO_DIR}/{session_folder}/{row["paper_id"]}*.srt'))
    sbv = list(glob(f'{VIDEO_DIR}/{session_folder}/{row["paper_id"]}*.sbv'))
    assert len(srt) <= 1 and len(sbv) <= 1
    if len(srt) == 0 and len(sbv) == 0:
        EXCEL_subtitle_msg.append(f'Missing subtitles for: {session_folder}/{row["paper_id"]}*.mp4')
    else:
        subtitle = srt if len(srt) == 1 else sbv
        if Path(video[0]).stem != Path(subtitle[0]).stem:
            EXCEL_other_msg.append(f"Inconsistent name: {video[0]}, {subtitle[0]}")


print(f"From excel, we know that there are {n_total} submissions")
print(f"We miss {len(EXCEL_video_msg)} videos and {len(EXCEL_subtitle_msg)} subtitles, and {len(EXCEL_other_msg)} inconsistent issues.")
print("Missing videos: ")
for msg in EXCEL_video_msg: print(msg)
print("Missing subtitles: ")
for msg in EXCEL_subtitle_msg: print(msg)
print("Inconsistent issues: ")
for msg in EXCEL_other_msg: print(msg)


if len(videos) > 0:
    print("Extra videos:")
    for video in videos: print(video)
