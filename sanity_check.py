from glob import glob
import os.path as osp
FOLDER = 'Video and Subtitles by Session'

videos = list(glob(FOLDER + '/*/*.mp4'))
srts = list(glob(FOLDER + '/*/*.srt'))
sbvs = list(glob(FOLDER + '/*/*.sbv'))

print(f'Video count: {len(videos)}, SRT count: {len(srts)}, SBV count: {len(sbvs)}')
unmatched_video = []
unmatched_srts = []
unmatched_sbvs = []
for video in videos:
    if video.replace('.mp4', '.srt') in srts: print(video);continue
    if video.replace('.mp4', '.sbv') in sbvs: print(video);continue
    unmatched_video.append(video)
    

print(f"There are {len(unmatched_video)} videos without subtitles")
for video in unmatched_video: print(video)

unmatched_srts = [srt for srt in srts if srt.replace('.srt', '.mp4') not in videos]
print(f"There are {len(unmatched_srts)} srts without videos")
for srt in unmatched_srts: print(srt)

unmatched_sbvs = [sbv for sbv in sbvs if sbv.replace('.sbv', '.mp4') not in videos]
print(f"There are {len(unmatched_sbvs)} sbvs without videos")
for sbv in unmatched_sbvs: print(sbv)