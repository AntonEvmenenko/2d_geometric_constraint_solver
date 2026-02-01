setlocal

set input_file=input.mp4
set output_file=output.gif

set crop=4 & :: pixels
set border_thickness=2 & :: pixels
set skip=0 & :: seconds

set /a temp=%border_thickness% * 2

ffmpeg ^
    -y ^
    -i %input_file% ^
    -ss %skip% ^
    -filter_complex "fps=24,crop=w=iw-%crop%:h=ih-%crop%,pad=w=%temp%+iw:h=%temp%+ih:x=%border_thickness%:y=%border_thickness%" ^
    %output_file%

endlocal