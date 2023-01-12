import xbmc, xbmcaddon, xbmcgui, xbmcplugin, os, sys, xbmcvfs, glob
import shutil
import urllib
import re
import time
from resources.lib.modules.backtothefuture import PY2
from resources.lib.modules import maintenance

# Code to map the old translatePath
if PY2:
    translatePath = xbmc.translatePath
    loglevel = xbmc.LOGNOTICE
else:
    translatePath = xbmcvfs.translatePath
    loglevel = xbmc.LOGINFO

AddonID ='script.ezmaintenanceplus'
packagesdir    =  translatePath(os.path.join('special://home/addons/packages',''))
thumbnails    =  translatePath('special://home/userdata/Thumbnails')
dialog = xbmcgui.Dialog()
setting = xbmcaddon.Addon().getSetting
iconpath = translatePath(os.path.join('special://home/addons/' + AddonID,'icon.png'))
# if setting('autoclean') == 'true':
    # control.clearCache()

notify_mode = setting('notify_mode')
auto_clean  = setting('startup.cache')
filesize = int(setting('filesize_alert'))
filesize_thumb = int(setting('filesizethumb_alert'))
maxpackage_zips = int(setting('packagenumbers_alert'))

total_size2 = 0
total_size = 0
count = 0

for dirpath, dirnames, filenames in os.walk(packagesdir):
    count = 0
    for f in filenames:
        count += 1
        fp = os.path.join(dirpath, f)
        total_size += os.path.getsize(fp)
total_sizetext = "%.0f" % (total_size/1024000.0)

if int(total_sizetext) > filesize:
    choice2 = xbmcgui.Dialog().yesno("[COLOR=red]Autocleaner[/COLOR]", 'The packages folder is [COLOR red]' + str(total_sizetext) +' MB [/COLOR] - [COLOR red]' + str(count) + '[/COLOR] zip files' + '\n' + 'The folder can be cleaned up without issues to save space...' + '\n' + 'Do you want to clean it now?', yeslabel='Yes',nolabel='No')
    if choice2 == 1:
        maintenance.purgePackages()

for dirpath2, dirnames2, filenames2 in os.walk(thumbnails):
    for f2 in filenames2:
        fp2 = os.path.join(dirpath2, f2)
        total_size2 += os.path.getsize(fp2)
total_sizetext2 = "%.0f" % (total_size2/1024000.0)

if int(total_sizetext2) > filesize_thumb:
    choice2 = xbmcgui.Dialog().yesno("[COLOR=red]Autocleaner[/COLOR]", 'The images folder is [COLOR red]' + str(total_sizetext2) + ' MB   [/COLOR]' + '\n' + 'The folder can be cleaned up without issues to save space...' + '\n' + 'Do you want to clean it now?', yeslabel='Yes',nolabel='No')
    if choice2 == 1:
        maintenance.deleteThumbnails()

total_sizetext = "%.0f" % (total_size/1024000.0)
total_sizetext2 = "%.0f" % (total_size2/1024000.0)

if notify_mode == 'true': xbmc.executebuiltin('Notification(%s, %s, %s, %s)' % ('Maintenance Status',  'Packages: '+ str(total_sizetext) +  ' MB'  ' - Images: ' + str(total_sizetext2) + ' MB' , '5000', iconpath))
time.sleep(3)
if auto_clean  == 'true': maintenance.clearCache()

maintenance.logMaintenance("Service started")

class Monitor(xbmc.Monitor):

    def __init__(self):
        xbmc.Monitor.__init__(self)
        maintenance.logMaintenance("Monitor init")
        maintenance.determineNextMaintenance()

    def onSettingsChanged(self):
        maintenance.logMaintenance("onSettingsChanged")
        maintenance.determineNextMaintenance()

if __name__ == '__main__':

    monitor = Monitor()

    while not monitor.abortRequested():
        # Sleep/wait for abort for 10 seconds
        if monitor.waitForAbort(10):
            # Abort was requested while waiting. We should exit
            break
        maintenance.logMaintenance("monitor loop")
        if not xbmc.Player().isPlayingVideo():
            nextMaintenance = maintenance.getNextMaintenance()
            maintenance.logMaintenance("time.time() = %s, nextMaintenance = %s" % (str(time.time()), str(nextMaintenance)))
            if nextMaintenance > 0 and time.time() >= nextMaintenance:
                xbmc.log("ezmaintenanceplus: AutoClean started", level=loglevel)
                maintenance.clearCache()
                xbmc.log("ezmaintenanceplus: AutoClean done", level=loglevel)
                maintenance.determineNextMaintenance()
                #xbmc.executebuiltin('Notification(%s, %s, %s, %s)' % ('Maintenance' , 'Clean Completed' , '3000', iconpath))

    del monitor

