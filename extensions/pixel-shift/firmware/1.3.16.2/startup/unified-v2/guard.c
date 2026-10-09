/* 自写独立 init 监督/恢复入口。仅固定服务名，不接收任意命令。
 * RAM 意图标记在第一次停止服务之前落地；正常重启会清空 RAM，默认不重试。
 * 无曝光、设置、照片访问。运行状态不等于取景功能验收。 */
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
#include <time.h>
#include "supervisor_isolation.h"
#include "init_trial_sequence.h"
#define ROOT "/dev/x2d2-shutter-v1"
static const char intent[]="X2D2_INIT_TRIAL_RESTORE_V1\n";
static volatile sig_atomic_t interrupted;
static int diagnostic;
static int integration;
static void on_signal(int x){(void)x;interrupted=1;}
static long long tick(void){struct timespec t;if(clock_gettime(CLOCK_MONOTONIC,&t))return -1;return (long long)t.tv_sec*1000+t.tv_nsec/1000000;}
static void nap(void){struct timespec t={0,100000000};nanosleep(&t,NULL);}
static int state(const char *name,const char *want){char key[96],v[PROP_VALUE_MAX]={0};snprintf(key,sizeof key,"init.svc.%s",name);return __system_property_get(key,v)>0&&!strcmp(v,want);}
static int bounded_wait(pid_t pid,int *status,int ms){
 long long start=tick();if(start<0)return -1;
 for(;;){pid_t p=waitpid(pid,status,WNOHANG);if(p==pid)return 1;if(p<0&&errno!=EINTR)return -1;
  long long now=tick();if(now<start)return -1;if(now-start>=ms)return 0;nap();}
}
static int set_state(void *unused,const char *operation,const char *name){
 (void)unused;char ctl[24];snprintf(ctl,sizeof ctl,"ctl.%s",operation);
 printf("SERVICE %s %s\n",operation,name);
 pid_t p=fork();if(p<0)return 0;
 if(!p){execl("/system/bin/setprop","setprop",ctl,name,(char*)0);_exit(127);}
 int status=0,w=bounded_wait(p,&status,5000);
 if(w!=1){if(w==0){kill(p,SIGKILL);bounded_wait(p,&status,1000);}return 0;}
 if(!WIFEXITED(status)||WEXITSTATUS(status))return 0;
 const char *want=!strcmp(operation,"start")?"running":"stopped";
 long long start=tick();if(start<0)return 0;
 for(;;){if(state(name,want))return 1;long long now=tick();if(now<start||now-start>=12000)return 0;nap();}
}
static int exact_file(const char *path,const char *expected){
 int fd=open(path,O_RDONLY|O_CLOEXEC|O_NOFOLLOW);if(fd<0)return 0;
 char b[128];struct stat st;size_t n=strlen(expected);
 int ok=n<sizeof b&&!fstat(fd,&st)&&S_ISREG(st.st_mode)&&st.st_uid==0&&st.st_nlink==1&&st.st_size==(off_t)n&&
  read(fd,b,n)==(ssize_t)n&&!memcmp(b,expected,n);close(fd);return ok;
}
static int checkpoint(void){
 int fd=open(ROOT"/restore.pending",O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);if(fd<0)return 0;
 int ok=write(fd,intent,sizeof intent-1)==sizeof intent-1&&!fsync(fd);close(fd);return ok;
}
static int gate_tick(unsigned mode){
 struct {uint64_t magic,session,sequence,deadline;uint32_t mode,ready;} g={
  UINT64_C(0x315447485350),1004,1,(uint64_t)tick()+2000,mode,0};
 _Static_assert(sizeof g==40,"gate ABI");
 int fd=open(ROOT"/gate.next",O_WRONLY|O_CREAT|O_TRUNC|O_NOFOLLOW|O_CLOEXEC,0600);
 if(fd<0)return 0;
 struct stat st;int ok=!fstat(fd,&st)&&S_ISREG(st.st_mode)&&st.st_uid==0&&st.st_nlink==1&&
  write(fd,&g,sizeof g)==sizeof g;
 close(fd);return ok&&!rename(ROOT"/gate.next",ROOT"/gate");
}
#ifdef PS_INTEGRATION_BUILD
#include "unified_lifecycle.inc"
#endif
static int observe(void *unused){
 (void)unused;
#ifdef PS_INTEGRATION_BUILD
 if(integration)return integration_observe();
#endif
 if(diagnostic){
  PsTrialOps ops={NULL,set_state,NULL};
  if(!ps_trial_clients(&ops))return 0;
  puts("PHYSICAL_DIAGNOSTIC_CLIENTS_RUNNING_NOT_READY_PROOF");
  for(int i=0;i<1200&&!interrupted;i++){
   if(!state("x2d2-capture-trial","running")||!gate_tick(3))return 0;
   if(exact_file(ROOT"/diagnostic.stop","FINISH_PHYSICAL_TEST\n"))break;
   nap();
  }
  puts("PHYSICAL_DIAGNOSTIC_WINDOW_FINISHED");return !interrupted;
 }
 for(int i=0;i<100&&!interrupted;i++){if(!state("x2d2-capture-trial","running"))return 0;nap();}
 puts("TRIAL_OBSERVATION_FINISHED_NOT_FUNCTIONAL_ACCEPTANCE");return !interrupted;
}
static int recover(PsTrialOps *ops){
 if(!exact_file(ROOT"/restore.pending",intent)){puts("NO_VALID_RECOVERY_INTENT_NO_SERVICE_CHANGES");return 2;}
 char power[PROP_VALUE_MAX]={0};__system_property_get("sys.powerctl",power);
 if(*power){puts("POWER_TRANSITION_NO_SERVICE_RESTART");return 2;}
 if(exact_file("/dev/x2d2-unified-boot/mode","DIRECT\n")){
  int f=open("/dev/x2d2-unified-boot/mode",O_WRONLY|O_TRUNC|O_CLOEXEC|O_NOFOLLOW);
  if(f<0)return 1;int ok=write(f,"FAILED\n",7)==7;close(f);if(!ok)return 1;
 }
 if(!((diagnostic||integration)?ps_trial_restore_with_clients(ops):ps_trial_restore(ops))){puts("RECOVERY_UNCONFIRMED_NO_OVERLAPPING_START");return 1;}
 if(rename(ROOT"/restore.pending",ROOT"/restore.completed")){puts("RECOVERY_RECORD_UNCONFIRMED");return 1;}
 puts("ORIGINAL_PROCESSES_RUNNING_FUNCTIONAL_RECOVERY_UNVERIFIED");return 0;
}
static int guard_main(int argc,char **argv){
 if(argc!=2||getuid()!=0||getppid()!=1||!ps_supervisor_isolated())return 2;
 int recovery=!strcmp(argv[1],"--recover");
 diagnostic=exact_file(ROOT"/diagnostic.once","AUTHORIZED_ONE_PHYSICAL_PRESS\n");
#ifdef PS_INTEGRATION_BUILD
 integration=exact_file(ROOT"/integration.once","AUTHORIZED_RETAIN_INPUTS_INTEGRATION\n");
#endif
 if(!recovery&&strcmp(argv[1],"--supervise"))return 2;
 int lock=open(ROOT"/control.lock",O_RDWR|O_CREAT|O_NOFOLLOW|O_CLOEXEC,0600);struct stat st;
 if(lock<0||fstat(lock,&st)||!S_ISREG(st.st_mode)||st.st_uid!=0||st.st_nlink!=1||flock(lock,LOCK_EX|LOCK_NB))return 2;
 int load=!recovery&&exact_file(ROOT"/load.once","AUTHORIZED_NO_CAPTURE\n");
 const char *log=recovery?ROOT"/recovery.log":load?ROOT"/trial.log":ROOT"/audit.log";
 int fd=open(log,O_WRONLY|O_CREAT|(recovery?O_APPEND:O_EXCL)|O_NOFOLLOW|O_CLOEXEC,0600);
 if(fd<0||fstat(fd,&st)||!S_ISREG(st.st_mode)||st.st_uid!=0||st.st_nlink!=1)return 2;
 dup2(fd,1);dup2(fd,2);close(fd);setvbuf(stdout,NULL,_IONBF,0);setvbuf(stderr,NULL,_IONBF,0);
 struct sigaction sa={0};sa.sa_handler=on_signal;sigaction(SIGTERM,&sa,NULL);sigaction(SIGINT,&sa,NULL);
 printf("INDEPENDENT_INIT_GUARD_PID=%ld MODE=%s\n",(long)getpid(),recovery?"recover":load?"load":"audit");
 PsTrialOps ops={NULL,set_state,observe};
 if(recovery)return recover(&ops);
 if(!load){puts("AUDIT_ONLY_NO_SERVICE_CHANGES");return 0;}
 int direct=exact_file("/dev/x2d2-direct-boot/result","DIRECT\n");
 int capture_ok=direct?(!state("camera-service","running")&&state("x2d2-capture-trial","running")):
   (state("camera-service","running")&&state("x2d2-capture-trial","stopped"));
 if(!capture_ok||!state("camera-test","running")||!state("camera-gui","running")||interrupted){puts("BASELINE_REFUSED_NO_SERVICE_CHANGES");return 2;}
 if(diagnostic&&!gate_tick(0)){puts("DIAGNOSTIC_GATE_FAILED_NO_SERVICE_CHANGES");return 2;}
 if(rename(ROOT"/load.once",ROOT"/load.consumed")||!checkpoint()){puts("INTENT_FAILED_NO_SERVICE_CHANGES");return 2;}
 if(direct){
  int adopted=open("/dev/x2d2-direct-boot/adopted",O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
  if(adopted<0)return recover(&ops);
  const char msg[]="DIRECT_CAPTURE_OWNED_BY_GUARD\n";
  int ok=write(adopted,msg,sizeof msg-1)==sizeof msg-1;close(adopted);
  if(!ok)return recover(&ops);
  puts("DIRECT_CAPTURE_ADOPT_NO_RESTART");
 }
 int unified=exact_file("/dev/x2d2-unified-boot/mode","DIRECT\n");
 int tested=unified?observe(NULL):direct?ps_trial_adopt_direct(&ops):ps_trial_load(&ops);printf("LOAD_SEQUENCE_COMPLETED=%d\n",tested);
 int restored=recover(&ops);return restored?restored:tested?0:1;
}
/* 仅用于独立 init 定义中的原厂报告脚本入口。在 shell main 执行前接管并退出，
 * 不执行报告脚本正文。先去掉预加载环境，避免 setprop 子进程递归载入监督器。 */
__attribute__((constructor)) static void guard_entry(void){
 const char *mode=getenv("X2D2_TRIAL_GUARD_MODE");
 int recovery=mode&&!strcmp(mode,"recover");
 if(!recovery&&(!mode||strcmp(mode,"supervise")))_exit(2);
 unsetenv("LD_PRELOAD");unsetenv("X2D2_TRIAL_GUARD_MODE");
 char *args[]={"x2d2-trial-guard",recovery?"--recover":"--supervise",NULL};
 _exit(guard_main(2,args));
}
