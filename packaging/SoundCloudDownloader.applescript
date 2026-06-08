on run
	set webappPath to POSIX path of (path to resource "soundcloud_webapp.py")
	set resourcesPath to do shell script "/usr/bin/dirname " & quoted form of webappPath
	set logPath to "/tmp/soundcloud-downloader.log"
	
	set launchCommand to "export SOUNDCLOUD_DOWNLOADER_RESOURCES=" & quoted form of resourcesPath & "; /usr/bin/python3 " & quoted form of webappPath & " > " & quoted form of logPath & " 2>&1 &"
	do shell script launchCommand
	
	delay 0.8
	do shell script "/usr/bin/open http://127.0.0.1:8765/ >/dev/null 2>&1 || true"
end run

