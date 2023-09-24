# os_utils.py
# This utility module provides functions to manage output files post-merging.
# It's designed to handle file operations automatically, avoiding the need to
# manually modify or changing directly on the original merging script.

import os

EXE_FOLDER = "output/MAIN CONFERENCE"

def delete_redundant_output_files(foldername, filename, identifier_suffix="_cover"):
    """
    if x_cover.mp4 and x_cover.srt exists, delete x.mp4 and x.srt files.
    otherwise warning that somehow merge 
        (merge individual video into a session video and adding a 5_sec session cover) 
        is NOT successful
    Args:
        foldername (string): the folder name to make deletion
        filename (string): the x filename corresponding to x.mp4 and x.srt, and also x_cover.mp4 and x_cover.srt
    """
    # construct the full path for the files
    cover_mp4 = os.path.join(foldername, f"{filename}{identifier_suffix}.mp4")
    cover_srt = os.path.join(foldername, f"{filename}{identifier_suffix}.srt")
    
    mp4 = os.path.join(foldername, f"{filename}.mp4")
    srt = os.path.join(foldername, f"{filename}.srt")
    
    # check if the _cover files exist
    if os.path.exists(cover_mp4) and os.path.exists(cover_srt):
        # if the original files exist, delete them
        if os.path.exists(mp4):
            os.remove(mp4)
        if os.path.exists(srt):
            os.remove(srt)
    else:
        print("Warning: Merge operation (merge individual video into a session video and adding a 5_sec session cover) is NOT successful")


def get_duplicated_filenames(foldername, identifier_suffix, filetype="mp4"):
    """
    Identify duplicated filenames in the format: x.filetype and x_identifier_suffix.filetype.
    
    Args:
        foldername (str): Directory to search for duplicated files.
        identifier_suffix (str): The suffix used to identify potential duplicates.
        filetype (str, optional): The file extension/type to consider. Defaults to "mp4".
    
    Returns:
        set: A set of duplicated filenames without the file extension.
    """
    # List all files in the foldername directory with the specified filetype
    all_files = [f for f in os.listdir(foldername) if f.endswith(f".{filetype}")]
    
    # Identify duplicates based on provided criteria
    duplicates = set()
    for file in all_files:
        base_name = os.path.splitext(file)[0]
        
        # If it ends with the identifier_suffix, check for its original counterpart
        if base_name.endswith(identifier_suffix):
            original_file = base_name.replace(identifier_suffix, "") + f".{filetype}"
            
            if original_file in all_files:
                duplicates.add(os.path.splitext(original_file)[0])
    
    return duplicates

def remove_duplicated_one_folder(parent_foldername, op_foldername):
    """
    Remove duplicated files in one folder.
    """
    complete_foldername = os.path.join(parent_foldername, op_foldername)
    duplicated_mp4 = get_duplicated_filenames(complete_foldername, "_cover", "mp4")
    duplicated_srt = get_duplicated_filenames(complete_foldername, "_cover", "srt")
    assert sorted(duplicated_mp4) == sorted(duplicated_srt), "ERROR: the merged mp4 doesn't match the merged srt"
    print("❌ #", len(duplicated_srt), " to be deleted in 📃", complete_foldername)
    for filename in duplicated_srt:
        delete_redundant_output_files(complete_foldername, filename, "_cover")


def remove_duplicated_multiple_folder(parent_foldername, skip_foldername=["merged"]):
    """
    Remove duplicated files in multiple folders.
    """
    for foldername in os.listdir(parent_foldername):
        full_path = os.path.join(parent_foldername, foldername)

        # Check if the current item is a directory and not in the skip list
        if os.path.isdir(full_path) and foldername not in skip_foldername:
            remove_duplicated_one_folder(parent_foldername, foldername)
  
  
if __name__ == "__main__":
    remove_duplicated_one_folder(EXE_FOLDER, "merged")
    remove_duplicated_multiple_folder(EXE_FOLDER)