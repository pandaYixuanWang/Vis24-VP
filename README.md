# Vis24-VP

### Requirements
- **Operating System**: Due to filename constraints, Linux or MacOS is recommended.
- **Dependencies**: 

Install the required python libraries via `pip install -r requirements.txt`.

Additional required libraries, ffmpeg and cairo. (*Note: if cairo is installed through brew under MacOS, it is required to create a python environment through **brew's Python** to use it.*)

MacOS
```bash
brew install cairo
brew install ffmpeg
```

Linux
```bash
apt-get install libcairo2-dev
apt-get install ffmpeg
```

```
VIS24-VP
│
├── main.py
├── conference.py
├── metadata-file-2024.xlsx
├── preview-background-2024.png
│
├── Video and Subtitles by Session
│ └── MAIN CONFERENCE (get all files from https://drive.google.com/drive/folders/1pFwimftyVmth53dAbl2v3idKR59YDd4S)
│   └── session 1 (e.g. full0-VIS Opening)
│
├── output
│ └── MAIN CONFERENCE (get all files from https://drive.google.com/drive/folders/1VcjRnYwTCEtEj3fSQdzF-ApWETkfcP1C)
│   ├── merged
│   └── session 1 (e.g. full0-VIS Opening)
...
```
### Generate Merged Files
1. If necessary, modify the line `CSV_FILE = 'metadata-file-2024.xlsx'` to point to the correct file (e.g., `'metadata-file-2024-testing.xlsx'` for testing purposes)
2. Run the command:
    ```bash
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

### Changes from Vis23-VP
1. Updated the description of dependecies.
2. Generated a new `preview-background-2024` title background template with the updated color scheme. The source file was named as `preview-background-2024.psd`.
3. Update the text color scheme to match this year's theme (conference.py).
    ```python
    ctx.set_source_rgba(0.14510, 0.28235, 0.35686, 1) # Light Blue background - 2024
    ctx.set_source_rgba(0.14510, 0.28235, 0.35686, 1) # Light Blue - 2024
    ctx.set_source_rgba(0.07843, 0.15686, 0.20000, 1) # Grey Text - 2024
    ctx.set_source_rgba(0.97647, 0.63137, 0.22353) # Orange - 2024
    ```
4. Update the date and time mapping.
    ```python
    TIME_MAP = {
        '1': '08:30-9:45',
        '2': '10:15-11:30',
        '3': '13:30-14:45',
        '4': '15:15-16:30',
    }

    DATE_MAP = {
        'mon': 'Monday (Oct 14)',
        'tue': 'Tuesday (Oct 15)',
        'wed': 'Wednesday (Oct 16)',
        'thu': 'Thursday (Oct 17)',
        'fri': 'Friday (Oct 18)',
    }
    ```



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
