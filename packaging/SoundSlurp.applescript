on run
	set appURL to "http://127.0.0.1:8765/"
	set healthURL to "http://127.0.0.1:8765/api/info"
	set webappPath to POSIX path of (path to resource "sound_slurp_webapp.py")
	set resourcesPath to do shell script "/usr/bin/dirname " & quoted form of webappPath
	set logPath to "/tmp/sound-slurp.log"
	
	set serverRunning to false
	try
		set healthResponse to do shell script "/usr/bin/curl -fsS --max-time 1 " & quoted form of healthURL
		if healthResponse contains "Sound Slurp" then
			set serverRunning to true
		else
			do shell script "pids=$(/usr/sbin/lsof -ti tcp:8765 -sTCP:LISTEN 2>/dev/null || true); if [ -n \"$pids\" ]; then /bin/kill $pids >/dev/null 2>&1 || true; fi"
			delay 0.2
		end if
	end try
	
	if serverRunning is false then
		set launchCommand to "export SOUND_SLURP_RESOURCES=" & quoted form of resourcesPath & "; export SOUND_SLURP_ASSETS=" & quoted form of resourcesPath & "; export SOUND_SLURP_NO_AUTO_OPEN=1; /usr/bin/python3 " & quoted form of webappPath & " > " & quoted form of logPath & " 2>&1 &"
		do shell script launchCommand
		delay 0.8
	end if
	
	do shell script "/usr/bin/open " & quoted form of appURL & " >/dev/null 2>&1 || true"
end run
