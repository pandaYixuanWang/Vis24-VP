cp "Video and Subtitles by Session\MAIN CONFERENCE\vr1-VR Invited Talks\v-vr-9714118_Solah_Preview.mp4" "Video and Subtitles by Session\MAIN CONFERENCE\vr1-VR Invited Talks\origin-v-vr-9714118_Solah_Preview.mp4"
ffmpeg -i "Video and Subtitles by Session\MAIN CONFERENCE\vr1-VR Invited Talks\origin-v-vr-9714118_Solah_Preview.mp4" -vf "scale='trunc(ih*dar):ih',setsar=1/1,pad='1024:576:(ow-iw)/2:(oh-ih)/2:white'" -acodec copy "Video and Subtitles by Session\MAIN CONFERENCE\vr1-VR Invited Talks\pad-v-vr-9714118_Solah_Preview.mp4"
ffmpeg -i "Video and Subtitles by Session\MAIN CONFERENCE\vr1-VR Invited Talks\pad-v-vr-9714118_Solah_Preview.mp4" -vf "scale=1920:1080" "Video and Subtitles by Session\MAIN CONFERENCE\vr1-VR Invited Talks\v-vr-9714118_Solah_Preview.mp4"
rm "Video and Subtitles by Session\MAIN CONFERENCE\vr1-VR Invited Talks\pad-v-vr-9714118_Solah_Preview.mp4"

cp "Video and Subtitles by Session\POSTERS\VIS Posters\v-vis-posters-1056.mp4" "Video and Subtitles by Session\POSTERS\VIS Posters\origin-v-vis-posters-1056.mp4"
ffmpeg -i "Video and Subtitles by Session\POSTERS\VIS Posters\origin-v-vis-posters-1056.mp4" -vf "scale = 1920:1080:force_original_aspect_ratio=decrease,setsar=1/1,pad='1920:1080:(ow-iw)/2:(oh-ih)/2:white'" -acodec copy "Video and Subtitles by Session\POSTERS\VIS Posters\v-vis-posters-1056.mp4"

ffmpeg -i "Video and Subtitles by Session\MAIN CONFERENCE\full31-Provenance and Guidance\v-full-1089_Block_Preview.mov" -vcodec h264 -acodec aac "Video and Subtitles by Session\MAIN CONFERENCE\full31-Provenance and Guidance\v-full-1089_Block_Preview.mp4"

cp "Video and Subtitles by Session\MAIN CONFERENCE\full28-DNA~Genome and Molecular Data~Vis\v-full-1578_Cheng_Preview.mp4" "Video and Subtitles by Session\MAIN CONFERENCE\full28-DNA~Genome and Molecular Data~Vis\origin-v-full-1578_Cheng_Preview.mp4"
ffmpeg -i "Video and Subtitles by Session\MAIN CONFERENCE\full28-DNA~Genome and Molecular Data~Vis\origin-v-full-1578_Cheng_Preview.mp4" -vf "scale='trunc(ih*dar):ih',setsar=1/1,pad='1920:1080:(ow-iw)/2:(oh-ih)/2:white'" -acodec copy "Video and Subtitles by Session\MAIN CONFERENCE\full28-DNA~Genome and Molecular Data~Vis\v-full-1578_Cheng_Preview.mp4"

cp "Video and Subtitles by Session\ASSOCIATED EVENTS\Vis4Good\w-vis4good-2457_Hattab_Preview.mp4" "Video and Subtitles by Session\ASSOCIATED EVENTS\Vis4Good\origin-w-vis4good-2457_Hattab_Preview.mp4"
ffmpeg -i "Video and Subtitles by Session\ASSOCIATED EVENTS\Vis4Good\origin-w-vis4good-2457_Hattab_Preview.mp4" -vf "scale='trunc(ih*dar):ih',setsar=1/1,pad='1920:1080:(ow-iw)/2:(oh-ih)/2:white'" -acodec copy "Video and Subtitles by Session\ASSOCIATED EVENTS\Vis4Good\w-vis4good-2457_Hattab_Preview.mp4"

cp "Video and Subtitles by Session\MAIN CONFERENCE\full13-Reflecting on Academia and our Field\v-tvcg-9747941_Guo_Preview.mp4" "Video and Subtitles by Session\MAIN CONFERENCE\full13-Reflecting on Academia and our Field\origin-v-tvcg-9747941_Guo_Preview.mp4"
ffmpeg -i "Video and Subtitles by Session\MAIN CONFERENCE\full13-Reflecting on Academia and our Field\origin-v-tvcg-9747941_Guo_Preview.mp4" -vf "scale='-2:1080',setsar=1/1,pad='1920:1080:(ow-iw)/2:(oh-ih)/2:white'" -acodec copy "Video and Subtitles by Session\MAIN CONFERENCE\full13-Reflecting on Academia and our Field\v-tvcg-9747941_Guo_Preview.mp4"


mv "Video and Subtitles by Session/ASSOCIATED EVENTS\TopoInVis\w-topoinvis-1005_wetzels_preview.srt" "Video and Subtitles by Session/ASSOCIATED EVENTS\TopoInVis\w-topoinvis-1005_Wetzels_Preview.srt"
mv "Video and Subtitles by Session/MAIN CONFERENCE\full23-Topology\v-full-1051_Kopee_Preview.sbv" "Video and Subtitles by Session/MAIN CONFERENCE\full23-Topology\v-full-1051_Koepp_Preview.sbv"
mv "Video and Subtitles by Session/MAIN CONFERENCE\short1-Visualization Systems and Graph Visualization\v-short-1098_Bako_preview.srt" "Video and Subtitles by Session/MAIN CONFERENCE\short1-Visualization Systems and Graph Visualization\v-short-1098_Bako_Preview.srt"
mv "Video and Subtitles by Session/MAIN CONFERENCE\full23-Topology\v-full-1051_Kopee_Preview.sbv" "Video and Subtitles by Session/MAIN CONFERENCE\full23-Topology\v-full-1051_Koepp_Preview.sbv"

rm "Video and Subtitles by Session\MAIN CONFERENCE\full28-DNA~Genome and Molecular Data~Vis\v-full-1193_L_Yi_Preview.mp4"
rm "Video and Subtitles by Session\MAIN CONFERENCE\full28-DNA~Genome and Molecular Data~Vis\v-full-1193_L_Yi_Preview.srt"