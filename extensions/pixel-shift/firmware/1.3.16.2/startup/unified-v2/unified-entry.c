/* Init-owned dispatch with factory-domain GUI exec; no image operations. */
#define _GNU_SOURCE
#include <sys/system_properties.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
static int mode(char *b){
 int fd=open("/dev/x2d2-unified-boot/mode",O_RDONLY|O_CLOEXEC|O_NOFOLLOW);
 if(fd<0)return 0;ssize_t n=read(fd,b,15);close(fd);if(n<=0)return 0;b[n]=0;return 1;
}
__attribute__((constructor))static void entry(void){
 const char *v=getenv("X2D2_UNIFIED_MODE");if(!v)return;
 int gui=!strcmp(v,"gui"),storage=!strcmp(v,"storage"),boot=!strcmp(v,"boot"),recover=!strcmp(v,"recover");
 if(getuid()!=0||getppid()!=1||(!gui&&!storage&&!boot&&!recover))_exit(126);
 unsetenv("X2D2_UNIFIED_MODE");unsetenv("LD_PRELOAD");
 if(!gui){
  execl("/system/bin/sh","sh",boot?"/system/x2d2-boot-v2/unified-start.sh":recover?"/system/x2d2-boot-v2/unified-recover.sh":"/system/x2d2-boot-v2/unified-storage.sh",(char*)0);_exit(127);
 }
 char power[PROP_VALUE_MAX]={0};__system_property_get("sys.powerctl",power);if(*power)return;
 char b[16]={0};int seen=0;
 for(int i=0;i<100;i++){if(mode(b)){seen=1;break;}struct timespec t={0,50000000};nanosleep(&t,0);}
 if(seen&&!strcmp(b,"LEGACY\n")){
  setenv("X2D2_GUI_EARLY_MODE","gui",1);
  dlopen("/system/lib64/libx2d2-gui-early.so",RTLD_NOW|RTLD_GLOBAL);return;
 }
 if(!seen||strcmp(b,"DIRECT\n"))return; /* Factory GUI remains available. */
 setenv("XDG_RUNTIME_DIR","/tmp",1);setenv("XDG_CACHE_HOME","/dev/x2d2-integrated-v1/cache",1);
 setenv("QT_QPA_FONTDIR","/system/lib64/qt/lib/fonts",1);
 setenv("QML_DISABLE_DISK_CACHE","1",1);setenv("QT_SHADER_CACHE_DISABLE","1",1);
 execl("/system/x2d2-boot-v2/gui","/system/x2d2-boot-v2/gui","-platform","wayland-egl","--fullscreen",(char*)0);
 /* Failed exec returns to the unmodified factory GUI. */
}
