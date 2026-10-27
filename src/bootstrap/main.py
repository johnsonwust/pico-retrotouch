"""Small Flash bootstrap; applications/assets live on SD."""
import os,sys
print('MACTOUCH_DUALBOOT_START')
try:
    import sd_mount
    sys.path.insert(0,'/sd/MACAPPS')
    os.chdir('/sd/MACAPPS')
    import dualtouch
    dualtouch.run()
except Exception as exc:
    sys.print_exception(exc)
    print('MacTouch startup failed; reset to return to boot menu. SD was not formatted.')
