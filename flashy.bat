@ECHO OFF
SET ScriptDir=%~dp0
@REM SET ScriptDir=%ScriptDir:~0,-1%

CD /D %ScriptDir%
python -m transmitter %1
