/* 自写 init 监督入口；原厂存储由独立 init 服务启动，保留原厂 SELinux 域。
 * 不拍摄、不访问照片内容、不改设置或策略。所有恢复只针对固定服务名。 */
#define _GNU_SOURCE
#include <sys/system_properties.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include "supervisor_isolation.h"
#include "album_trial_sequence.h"
#include "album_runtime.h"
#include "storage_exit_policy.h"
#include "reboot_pending.h"
#define ROOT "/dev/x2d2-album-refresh-v1"
#define DATA "/data/x2d2-album-init-v2"
static const char intent[]="X2D2_STORAGE_INIT_RECOVERY_V2\n";
static volatile sig_atomic_t interrupted;
static void signal_stop(int n){(void)n;interrupted=1;}
static int64_t tick(void){struct timespec t;if(clock_gettime(CLOCK_MONOTONIC,&t))return -1;return (int64_t)t.tv_sec*1000+t.tv_nsec/1000000;}
static void nap(void){struct timespec t={0,100000000};nanosleep(&t,NULL);}
static int power_ok(void){char b[PROP_VALUE_MAX]={0};__system_property_get("sys.powerctl",b);return !*b;}
static int state(const char *name,const char *wanted){char key[96],b[PROP_VALUE_MAX]={0};snprintf(key,sizeof key,"init.svc.%s",name);return __system_property_get(key,b)>0&&!strcmp(b,wanted);}
static int wait_pid(pid_t p,int *status,int ms){
 int64_t start=tick();if(start<0)return -1;
 for(;;){pid_t q=waitpid(p,status,WNOHANG);if(q==p)return 1;if(q<0&&errno!=EINTR)return -1;
  int64_t now=tick();if(now<start)return -1;if(now-start>=ms)return 0;nap();}
}
static int exact(const char *path,const char *expected){
 char b[128];struct stat st;size_t n=strlen(expected);int fd=open(path,O_RDONLY|O_CLOEXEC|O_NOFOLLOW);if(fd<0)return 0;
 int ok=n<sizeof b&&!fstat(fd,&st)&&S_ISREG(st.st_mode)&&st.st_uid==0&&st.st_nlink==1&&st.st_size==(off_t)n&&read(fd,b,n)==(ssize_t)n&&!memcmp(b,expected,n);close(fd);return ok;
}
static int write_new(const char *path,const char *text){
 int fd=open(path,O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW,0600);if(fd<0)return 0;
 size_t n=strlen(text);int ok=write(fd,text,n)==(ssize_t)n&&!fsync(fd);close(fd);return ok;
}
static int ctl(const char *operation,const char *name){
 char key[32];snprintf(key,sizeof key,"ctl.%s",operation);printf("STORAGE_CTL %s %s\n",operation,name);
 pid_t p=fork();if(p<0)return 0;
 if(!p){execl("/system/bin/setprop","setprop",key,name,(char*)NULL);_exit(127);}
 int status=0,done=wait_pid(p,&status,5000);
 if(done!=1){if(!done){kill(p,SIGKILL);wait_pid(p,&status,1000);}return 0;}
 if(!WIFEXITED(status)||WEXITSTATUS(status))return 0;
 const char *wanted=!strcmp(operation,"start")?"running":"stopped";
 for(int i=0;i<100;i++){if(state(name,wanted))return 1;nap();}return 0;
}
static int readonly_prop(const char *service,const char *name,const char *expected){
 int pp[2];if(pipe2(pp,O_CLOEXEC|O_NONBLOCK))return 0;pid_t p=fork();
 if(p<0){close(pp[0]);close(pp[1]);return 0;}
 if(!p){close(pp[0]);fcntl(pp[1],F_SETFL,0);dup2(pp[1],1);dup2(pp[1],2);close(pp[1]);execl("/system/bin/odindb-send","odindb-send","-s",service,"-p",name,(char*)NULL);_exit(127);}
 close(pp[1]);int status=0,done=wait_pid(p,&status,4000);
 if(done!=1){kill(p,SIGKILL);wait_pid(p,&status,1000);close(pp[0]);return 0;}
 char b[512];ssize_t n=read(pp[0],b,sizeof b-1);close(pp[0]);if(n<0)return 0;b[n]=0;
 return WIFEXITED(status)&&WEXITSTATUS(status)==0&&!strcmp(b,expected);
}
static int not_started_or_stopped(const char *name){
 char key[96],value[PROP_VALUE_MAX]={0};snprintf(key,sizeof key,"init.svc.%s",name);
 __system_property_get(key,value);return !*value||!strcmp(value,"stopped");
}
static int reboot_review(void){
 char token[21];struct stat st;
 if(lstat(RP_DATA"/pending",&st))return errno==ENOENT;
 if(!rp_pending(token)||!not_started_or_stopped("x2d2-trial-guard")||!not_started_or_stopped("x2d2-capture-trial"))return 0;
 pid_t p=fork();if(p<0)return 0;
 if(!p){setpgid(0,0);execl(ROOT"/reboot-reconcile",ROOT"/reboot-reconcile",(char*)NULL);_exit(127);}
 setpgid(p,p);int status=0,done=wait_pid(p,&status,15000);
 if(done!=1){kill(-p,SIGKILL);kill(p,SIGKILL);wait_pid(p,&status,1000);return 0;}
 char seen[21];int resolved;
 return WIFEXITED(status)&&WEXITSTATUS(status)==0&&rp_review(seen,&resolved)&&!strcmp(seen,token);
}
static int idle(void *unused){
 (void)unused;
 if(exact("/dev/x2d2-unified-boot/mode","DIRECT\n"))
  return !interrupted&&power_ok()&&!state("camera-storage","running")&&access(RP_DATA"/pending",F_OK)!=0;
 return !interrupted&&power_ok()&&state("camera-storage","running")&&state("x2d2-storage-trial","stopped")&&
  readonly_prop("camera","exposure_status","exposure_status = E_ExposureStatus_None(0)\n")&&
  readonly_prop("storage","storage_processing_counter","storage_processing_counter = 0\n")&&reboot_review()&&
  readonly_prop("camera","exposure_status","exposure_status = E_ExposureStatus_None(0)\n")&&
  readonly_prop("storage","storage_processing_counter","storage_processing_counter = 0\n");
}
static int stop_original(void *unused){
 (void)unused;if(interrupted||!power_ok()||!write_new(ROOT"/restore.pending",intent))return 0;
 return exact("/dev/x2d2-unified-boot/mode","DIRECT\n")||ctl("stop","camera-storage");
}
static int trial(void *unused){
 (void)unused;if(interrupted||!power_ok()||state("camera-storage","running")||!ctl("start","x2d2-storage-trial"))return 0;
 int ready=0;
 for(int i=0;i<100&&!interrupted&&power_ok();i++){
  if(!state("x2d2-storage-trial","running"))break;
  if(album_runtime_ready()){ready=1;break;}nap();
 }
 if(!ready){puts("STORAGE_INIT_MODULE_NOT_READY");return 0;}
 /* 正确域再独立读回；不能仅凭可查询 metadata 推断传输身份。 */
 char b[80],path[96];int fd=open(ROOT"/ready",O_RDONLY|O_CLOEXEC|O_NOFOLLOW);if(fd<0)return 0;
 ssize_t n=read(fd,b,sizeof b-1);close(fd);if(n<=0)return 0;b[n]=0;long pid=0;char extra;
 if(sscanf(b,"ALBUM_RUNTIME_V1 %ld %c",&pid,&extra)!=1||pid<=1||pid>2147483647)return 0;
 snprintf(path,sizeof path,"/proc/%ld/attr/current",pid);fd=open(path,O_RDONLY|O_CLOEXEC|O_NOFOLLOW);if(fd<0)return 0;
 n=read(fd,b,sizeof b-1);close(fd);if(n<=0)return 0;b[n]=0;
 if(strcmp(b,"u:r:hbl_camera_service:s0")){puts("STORAGE_INIT_WRONG_DOMAIN");return 0;}
 printf("STORAGE_INIT_READY PID=%ld DOMAIN=%s NO_CAPTURE_NO_DELETE\n",pid,b);
 while(!interrupted&&power_ok()){
  if(access(DATA"/stop",F_OK)==0){puts("STORAGE_INIT_STOP_REQUEST");return 1;}
  if(errno!=ENOENT||!ps_supervisor_isolated()||!state("x2d2-storage-trial","running")||state("camera-storage","running")||!album_runtime_ready())return 0;
  for(int i=0;i<5&&!interrupted;i++)nap();
 }
 return 1;
}
static int stop_trial(void *unused){(void)unused;if(interrupted||!power_ok())return 0;return state("x2d2-storage-trial","stopped")||ctl("stop","x2d2-storage-trial");}
static int restore_original(void *unused){
 (void)unused;if(interrupted||!power_ok()){puts("POWER_TRANSITION_NO_RESTART");return 0;}
 int ok=state("camera-storage","running")||ctl("start","camera-storage");
 if(ok)puts("ORIGINAL_STORAGE_RUNNING_FUNCTIONAL_CHECK_PENDING");return ok;
}
static int recover(void){
 if(access(ROOT"/power-stopping",F_OK)==0){puts("SUPERVISOR_STOPPING_NO_RECOVERY_RESTART");return 2;}
 if(!exact(ROOT"/restore.pending",intent)){puts("NO_VALID_RECOVERY_INTENT");return 2;}
 if(!power_ok()){puts("POWER_TRANSITION_NO_RESTART");return 2;}
 if(!stop_trial(NULL)||!restore_original(NULL))return 1;
 if(rename(ROOT"/restore.pending",ROOT"/restore.completed"))return 1;
 write_new(DATA"/disabled","RESTORED_FACTORY_NO_AUTO_RETRY\n");
 puts("STORAGE_INIT_RECOVERY_COMPLETED");return 0;
}
static int guard_main(int recovery){
 if(getuid()!=0||getppid()!=1||!ps_supervisor_isolated())return 2;
 int lock=open(ROOT"/control.lock",O_RDWR|O_CREAT|O_CLOEXEC|O_NOFOLLOW,0600);struct stat st;
 if(lock<0||fstat(lock,&st)||!S_ISREG(st.st_mode)||st.st_uid!=0||st.st_nlink!=1||flock(lock,LOCK_EX|LOCK_NB))return 2;
 int load=!recovery&&exact(ROOT"/load.once","AUTHORIZED_STORAGE_INIT_NO_CAPTURE\n");
 const char *log=recovery?ROOT"/recovery.log":load?ROOT"/trial.log":ROOT"/audit.log";
 int fd=open(log,O_WRONLY|O_CREAT|(recovery?O_APPEND:O_EXCL)|O_CLOEXEC|O_NOFOLLOW,0600);
 if(fd<0||fstat(fd,&st)||!S_ISREG(st.st_mode)||st.st_uid!=0||st.st_nlink!=1)return 2;
 dup2(fd,1);dup2(fd,2);close(fd);setvbuf(stdout,NULL,_IONBF,0);setvbuf(stderr,NULL,_IONBF,0);
 struct sigaction sa={0};sa.sa_handler=signal_stop;sigaction(SIGTERM,&sa,NULL);sigaction(SIGINT,&sa,NULL);
 printf("STORAGE_INIT_GUARD_PID=%ld MODE=%s\n",(long)getpid(),recovery?"recover":load?"load":"audit");
 if(recovery)return recover();
 if(!load){puts("AUDIT_ONLY_NO_SERVICE_CHANGES");return 0;}
 if(rename(ROOT"/load.once",ROOT"/load.consumed"))return 2;
 PsAlbumTrialOps ops={NULL,idle,stop_original,trial,stop_trial,restore_original};
 int result=ps_album_trial_sequence(&ops);printf("STORAGE_INIT_SEQUENCE_RESULT=%d\n",result);
 if(interrupted||!power_ok()){
  write_new(ROOT"/power-stopping","SUPERVISOR_STOPPING_NO_RESTART\n");return result;
 }
 /* idle 前置拒绝尚未接管原服务，不应永久禁用存储扩展。 */
 if(ps_storage_should_disable(interrupted,power_ok(),exact(ROOT"/restore.pending",intent))){
  if(!result&&exact(ROOT"/restore.pending",intent))rename(ROOT"/restore.pending",ROOT"/restore.completed");
  write_new(DATA"/disabled","SUPERVISOR_EXIT_NO_AUTO_RETRY\n");
 }
 return result;
}
__attribute__((constructor))static void entry(void){
 const char *mode=getenv("X2D2_STORAGE_GUARD_MODE");int recovery=mode&&!strcmp(mode,"recover");
 if(!recovery&&(!mode||strcmp(mode,"supervise")))_exit(2);
 unsetenv("LD_PRELOAD");unsetenv("X2D2_STORAGE_GUARD_MODE");_exit(guard_main(recovery));
}
