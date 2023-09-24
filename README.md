# Vis23-VP
### Requirements
- **Operating System**: Due to filename constraints, Linux or MacOS is recommended.
- **Dependencies**: Install the required libraries. recommending `conda-forge`.
    ```
    pandas cairocffi sqlalchemy pyyaml tqdm
    ```

```
VIS23-VP
│
├── main.py
├── conference.py
├── metadata-file-2023.xlsx
├── preview-background-2023.png
│
├── Video and Subtitles by Session
│ └── MAIN CONFERENCE
│ └── session 1 (e.g. full0-VIS Opening)
│
├── output
│ └── MAIN CONFERENCE
│ ├── merged
│ └── session 1 (e.g. full0-VIS Opening)
...
```
### Generate Merged Files
1. If necessary, modify the line `CSV_FILE = 'metadata-file-2023-testing.xlsx'` to point to the correct file.
2. Run the command:
    ```
    python conference.py
    ```

For each `.mp4` and `.srt` file corresponding to a paper under a session folder (e.g. `x.mp4` and `x.srt`), in the output folder with the same file structure, this will produce:
- `x.mp4`, `x.srt`, `x.png` - A title slide (5 sec) followed by the original video (25 sec), totaling 30 seconds.
- `session_name.mp4`, `session_name.srt` - A concatenation of all the `x.mp4` and `x.srt` files in the session folder.
- `session_name_cover.mp4`, `session_name_cover.srt`, `session_name.png` - A session name slide (5 sec) followed by the concatenated session video.

#### Clean Up
To remove the concatenated files and only keep the files with session titles (e.g., remove `session_name.mp4 session_name.srt`, and only keep the `session_name_cover.mp4 session_name_cover.srt`) run:
    ```
    python os_utils.py
    ```
  - Modify `EXE_FOLDER` to `"output/POSTER"` if necessary.


### Changes from Vis22-VP
1. Added awards information in the `metadata-file`.
2. Generated a new `preview-background-2023` title background template.
    - Modifications can be made in `preview-background-2023.psd`.
3. Updated the text color scheme to match this year's theme.
    1. search `ctx.set_source_rgba( 0.549, 0.22, 0, 1 ) # darker yellow - 2023`
    2. search `ctx.set_source_rgba( 0.769, 0.439, 0, 1) # lighter yellow`
4. Adjusted the date to Monday-Sunday mapping.
   - search for 
    ```
    DATE_MAP = {
        'mon': 'Monday (Oct 23)',
        'tue': 'Tuesday (Oct 24)',
        'wed': 'Wednesday (Oct 25)',
        'thu': 'Thursday (Oct 26)',
        'fri': 'Friday (Oct 27)',
    }
    ```
   -  potentially need to change 
   ```
   TIME_MAP = {
        '1': '09:00-10:15',
        '2': '10:45-12:00',
        '3': '14:00-15:15',
        '4': '15:45-17:00',
    } 
    ```
    in `conference.py`
5. Created a mapping for new types of papers.
    ```
    if 'v-ismar' in paper_id: return 'ISMAR Paper'
    if 'v-vr' in paper_id: return 'VR Paper'
    ```

##### Error Handling
Some errors were addressed and solutions implemented:
- Using `shell = false` in `subprocess.Popen([])` in `probe()` to prevent shell-related errors.
- unify inconsistent sample aspect ratio with
    ```
    filter += '[1:v]scale=w=1920:h=1080,setsar=1:1[v1];'  
    # ! add setsar=1:1 here to resolve error that SAR 81:256 does not match  SAR 1:1
    ```
- Adjusted folder naming by replacing "&" with "_".
    ```
    if osp.exists(osp.join(VIDEO_DIR, folder_name.replace('&', '_'))): return folder_name.replace('&', '_') 
    # ! replace e.g. "Dashboards & Multiple Views" to "Dashboards _ Multiple Views"
    ```
- Resolved subtitle format errors in `.srt`/`.sbv` files, e.g.
   ```
   line = line.replace(', ', ',') # ! resolve error that '0:00:24.419, 0:00:26.0\n' has a space in ", "
   ```
- Added a function to refine subtitle formatting in           `refine_subtitle_format()`.




 


----------------------------------------------------------------
"# Vis22-VP" 

1. Install necessary libs. I recommend you run the code in Linux/MacOS because it would be a little hard to install cairocffi correctly in Windows (You can contact me if you need).
2. First download videos from `GoogleDrive/Task2/` and run `python sanity_check.py` to fix some typos in filenames.
3. Download some videos from `GoogleDrive/Task2/output/reencode` to replace some videos (incorrect format or display ratio, now I convert them, but it would be better if they provide a new version).
4. Run `python main.py` to process them.
