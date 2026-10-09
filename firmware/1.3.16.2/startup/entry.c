/* 原厂 GUI 首次 main 前准备回放扩展；失败返回原厂，不修改曝光或照片。
 * 每次开机最多尝试一次；持久 pending 未验收时下次启动直接回原厂。 */
#define _GNU_SOURCE
#ifdef GUI_EARLY_HOST_TEST
#define PROP_VALUE_MAX 92
static int __system_property_get(const char *n,char *b){(void)n;*b=0;return 0;}
#else
#include <sys/system_properties.h>
#endif
#include <sys/wait.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <poll.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#ifndef DATA
#define DATA "/data/x2d2-gui-early-v1"
#endif
#define RAM "/dev/x2d2-album-boot-v1"
#ifndef FULL
#define FULL "/data/x2d2-full-v1"
#endif
#ifndef BOOT_ID_FILE
#define BOOT_ID_FILE "/proc/sys/kernel/random/boot_id"
#endif
#include "reboot_pending.h"
#include "boot_idle_retry.h"
/* 健康确认会删除 pending，所以 pending 不能同时充当本次启动的防重入锁。
 * 单独保存内核 boot_id；正常关机中 GUI 被重拉起也不得再次创建 pending。 */
static int full_claim_boot(void){
 char boot[37]={0},old[37]={0};struct stat st;
 int fd=open(BOOT_ID_FILE,O_RDONLY|O_CLOEXEC|O_NOFOLLOW);if(fd<0)return 0;
 ssize_t n=read(fd,boot,36);close(fd);if(n!=36)return 0;
 for(int i=0;i<36;i++){
  if(i==8||i==13||i==18||i==23){if(boot[i]!='-')return 0;}
  else if(!((boot[i]>='0'&&boot[i]<='9')||(boot[i]>='a'&&boot[i]<='f')))return 0;
 }
 fd=open(FULL"/attempted.boot",O_RDONLY|O_CLOEXEC|O_NOFOLLOW);
 if(fd>=0){
  int valid=!fstat(fd,&st)&&S_ISREG(st.st_mode)&&st.st_nlink==1&&st.st_uid==getuid()&&st.st_size==36;
  n=read(fd,old,36);close(fd);if(!valid||n!=36||!memcmp(old,boot,36))return 0;
 }else if(errno!=ENOENT)return 0;
 fd=open(FULL"/attempted.boot.next",O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW,0600);
 if(fd<0)return 0;
 int ok=write(fd,boot,36)==36&&!fsync(fd);close(fd);
 if(!ok||rename(FULL"/attempted.boot.next",FULL"/attempted.boot"))return 0;
 fd=open(FULL,O_RDONLY|O_DIRECTORY|O_CLOEXEC);if(fd<0)return 0;
 ok=!fsync(fd);close(fd);return ok;
}
static void nap(void){struct timespec t={0,100000000};nanosleep(&t,0);}
static void audit(const char *event){
 int fd=open(DATA"/entry.log",O_WRONLY|O_APPEND|O_CREAT|O_CLOEXEC|O_NOFOLLOW,0600);if(fd<0)return;
 struct timespec ts={0};clock_gettime(CLOCK_MONOTONIC,&ts);
 dprintf(fd,"%ld.%03ld PID=%ld %s\n",ts.tv_sec,ts.tv_nsec/1000000,(long)getpid(),event);close(fd);
}
static int child(const char *exe,const char *a,const char *b,int ticks){
 pid_t p=fork();if(p<0)return 0;
 if(!p){if(setsid()<0)_exit(126);execl(exe,exe,a,b,(char*)0);_exit(127);}
 int st=0;for(int i=0;i<ticks;i++){
  pid_t done=waitpid(p,&st,WNOHANG);if(done==p)return WIFEXITED(st)&&WEXITSTATUS(st)==0;
  if(done<0&&errno!=EINTR)return 0;
  nap();
 }
 kill(-p,SIGKILL);kill(p,SIGKILL);while(waitpid(p,&st,0)<0&&errno==EINTR){}return 0;
}
static int context_ok(void){
 char b[80]={0};int fd=open("/proc/self/attr/current",O_RDONLY|O_CLOEXEC);if(fd<0)return 0;
 ssize_t n=read(fd,b,sizeof b-1);close(fd);return n>0&&!strcmp(b,"u:r:hbl_camera_service:s0");
}
static int port_ready(void){
 int fd=socket(AF_INET,SOCK_STREAM|SOCK_CLOEXEC|SOCK_NONBLOCK,0);if(fd<0)return 0;
 struct sockaddr_in a={0};a.sin_family=AF_INET;a.sin_port=htons(38407);a.sin_addr.s_addr=htonl(INADDR_LOOPBACK);
 int ok=connect(fd,(struct sockaddr*)&a,sizeof a)==0;
 if(!ok&&errno==EINPROGRESS){struct pollfd f={fd,POLLOUT,0};int error=1;socklen_t n=sizeof error;
  ok=poll(&f,1,30)>0&&!getsockopt(fd,SOL_SOCKET,SO_ERROR,&error,&n)&&!error;}
 close(fd);return ok;
}
static int once(void){
 if(access(DATA"/enabled",F_OK)||access(DATA"/disabled",F_OK)==0||errno!=ENOENT)return 0;
 int fd=open(DATA"/boot.pending",O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW,0600);if(fd<0)return 0;
 const char msg[]="GUI_EARLY_FIRST_BOOT_AWAITING_USER\n";
 int ok=write(fd,msg,sizeof msg-1)==sizeof msg-1&&!fsync(fd);close(fd);return ok;
}
/* 首次 GUI 尚未进入 main；把已验证的独立监督接管提前到这里。
 * 只在全包显式启用且本轮未尝试时调用；保护触发则仍走已验收的放大入口。 */
static void full_handoff(void){
 if(access(FULL"/enabled",F_OK)||access(FULL"/disabled",F_OK)==0||errno!=ENOENT)return;
 if(!full_claim_boot()){audit("FULL_ALREADY_ATTEMPTED_OR_BOOT_CLAIM_REFUSED");return;}
 /* Wait for the independent boot review, never erase a live task here. */
 if(access(FULL"/boot.pending",F_OK)==0){
  if(boot_no_job()){
   if(!boot_idle_retry()){audit("IDLE_BOOT_RETRY_REFUSED");return;}
   audit("IDLE_BOOT_RETRY_NO_CAPTURE_NO_DELETE");
  }else{
  char token[21];int resolved=0,reviewed=0;
  for(int i=0;i<250;i++){if(rp_review(token,&resolved)){reviewed=1;break;}nap();}
  if(!reviewed||access(FULL"/accepted",F_OK)!=0){audit("BOOT_REVIEW_NOT_CONFIRMED");return;}
  /* One retry per failed job; a real startup crash still fails closed. */
  if(!rp_menu_retry(FULL)){
   audit("BOOT_REVIEW_RETRY_REFUSED");return;
  }
  audit(resolved?"BOOT_REVIEW_RESOLVED":"BOOT_REVIEW_MENU_ONLY");
  }
 }else if(!boot_clear_retry_budget()){audit("RETRY_BUDGET_RESET_FAILED");return;}
 int fd=open(FULL"/boot.pending",O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW,0600);if(fd<0)return;
 const char msg[]="FULL_FIRST_BOOT_AWAITING_USER\n";
 int ok=write(fd,msg,sizeof msg-1)==sizeof msg-1&&!fsync(fd);close(fd);if(!ok)return;
 audit("FULL_HANDOFF_PREPARE_BEGIN");
 if(!child("/system/bin/sh",FULL"/prepare.sh",NULL,600)){
  audit("FULL_PREPARE_FAILED_FALLBACK_ZOOM");return;
 }
 /* 正常路径：guard 的第一个停止操作结束本 GUI，之后才重建 camera-service。
  * 绝不在提交了恢复意图后继续进入 GUI main，避免观察到中途重启的 D-Bus。 */
 for(int i=0;i<300;i++){
  char st[PROP_VALUE_MAX]={0};__system_property_get("init.svc.x2d2-trial-guard",st);
  if(i>20&&!strcmp(st,"stopped")&&access("/dev/x2d2-shutter-v1/restore.pending",F_OK)!=0&&errno==ENOENT){
   audit("FULL_GUARD_REFUSED_FALLBACK_ZOOM");return;
  }
  nap();
 }
 audit("FULL_HANDOFF_UNCONFIRMED_NO_GUI_MAIN");
 /* 不把未确认接管伪装成可操作界面。退出后 init 重启，pending 禁止再次全包尝试。 */
 _exit(1);
}
#ifndef GUI_EARLY_HOST_TEST
__attribute__((constructor))
#endif
static void entry(void){
 const char *value=getenv("X2D2_GUI_EARLY_MODE");if(!value)return;
 int server=!strcmp(value,"server"),gui=!strcmp(value,"gui");
 unsetenv("X2D2_GUI_EARLY_MODE");unsetenv("LD_PRELOAD");
 if(!context_ok()||getuid()!=0){if(server)_exit(120);return;}
 if(server){
  if(getppid()!=1||access(RAM"/prepared",F_OK))_exit(121);
  audit("EARLY_ZOOM_EXEC");
  execl(RAM"/server",RAM"/server","/mnt/media_rw/ssd/DCIM","/mnt/media_rw/cfe/DCIM",RAM"/scratch","38407","resident",(char*)0);_exit(127);
 }
 if(!gui||getppid()!=1)return;
 char power[PROP_VALUE_MAX]={0};__system_property_get("sys.powerctl",power);
 if(*power){audit("POWER_TRANSITION_NO_EXTENSION_START");return;}
 full_handoff();
 if(!once()){audit("FACTORY_GUI_PENDING_OR_DISABLED");return;}
 audit("EARLY_GUI_PREPARE_BEGIN");
 /* 子脚本有自己的有界 timeout；超时不执行未完成的 GUI。 */
 if(port_ready()){audit("FACTORY_GUI_PORT_OCCUPIED");return;}
 if(!child("/system/bin/sh",DATA"/prepare.sh",NULL,300)){audit("FACTORY_GUI_PREPARE_FAILED");return;}
 if(!child("/system/bin/setprop","ctl.start","x2d2-early-zoom",50)){audit("FACTORY_GUI_ZOOM_START_FAILED");return;}
 int ready=0;for(int i=0;i<50;i++){char state[PROP_VALUE_MAX]={0};__system_property_get("init.svc.x2d2-early-zoom",state);
  if(!strcmp(state,"running")&&port_ready()){ready=1;break;}nap();}
 if(!ready){child("/system/bin/setprop","ctl.stop","x2d2-early-zoom",50);audit("FACTORY_GUI_ZOOM_NOT_READY");return;}
 setenv("XDG_RUNTIME_DIR","/tmp",1);setenv("XDG_CACHE_HOME",RAM"/cache",1);
 setenv("QT_QPA_FONTDIR","/system/lib64/qt/lib/fonts",1);setenv("QML_DISABLE_DISK_CACHE","1",1);setenv("QT_SHADER_CACHE_DISABLE","1",1);
 audit("EARLY_GUI_EXEC_SAME_PID");
 execl(RAM"/gui",RAM"/gui","-platform","wayland-egl","--fullscreen",(char*)0);
 audit("FACTORY_GUI_EXEC_FAILED");
 child("/system/bin/setprop","ctl.stop","x2d2-early-zoom",50);
}
