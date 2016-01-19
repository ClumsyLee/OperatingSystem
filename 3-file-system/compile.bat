path \wrk-v1.2\tools\x86;%path%
cd \wrk-v1.2\base\ntos
nmake -nologo x86=
copy /y \WRK-v1.2\base\ntos\BUILD\EXE\wrkx86.exe \WINDOWS\system32\
