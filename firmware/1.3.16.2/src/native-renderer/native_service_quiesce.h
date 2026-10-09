/* Unknown asynchronous completion is NOT safe buffer release. This helper
 * stops only the existing isolated trial service, then checks the original
 * PID identity is gone. If stopping fails, caller MUST retain allocations. */
#ifndef NATIVE_SERVICE_QUIESCE_H
#define NATIVE_SERVICE_QUIESCE_H
#include "native_job_lease.h"
#include <dirent.h>
#include <stdlib.h>
#include <errno.h>
extern int __system_property_get(const char*,char*);
extern int __system_property_set(const char*,const char*);
typedef struct {unsigned pid;uint64_t start;} NativeServiceIdentity;
static int nsq_state(const char*name,const char*expected){
 char key[128],value[128]={0};snprintf(key,sizeof key,"init.svc.%s",name);
 return __system_property_get(key,value)>0&&!strcmp(value,expected);
}
static int nsq_identify(NativeServiceIdentity*out){
 if(!nsq_state("camera-service","stopped")||!nsq_state("x2d2-capture-trial","running"))return 0;
 DIR*d=opendir("/proc");if(!d)return 0;struct dirent*e;unsigned count=0;*out=(NativeServiceIdentity){0};
 while((e=readdir(d))){
  char*end;unsigned long pid=strtoul(e->d_name,&end,10);if(!pid||*end||pid>INT32_MAX)continue;
  char path[64],exe[128];snprintf(path,sizeof path,"/proc/%lu/exe",pid);
  ssize_t n=readlink(path,exe,sizeof exe-1);if(n<=0)continue;exe[n]=0;
  if(strcmp(exe,"/system/bin/camera-service"))continue;
  out->pid=(unsigned)pid;out->start=njl_process_start(out->pid);count++;
 }
 closedir(d);return count==1&&out->start;
}
static int nsq_gone(const NativeServiceIdentity*s){
 if(!s||!s->pid||!s->start||!nsq_state("x2d2-capture-trial","stopped"))return 0;
 char path[64];struct stat st;snprintf(path,sizeof path,"/proc/%u",s->pid);
 if(lstat(path,&st))return errno==ENOENT;
 uint64_t current=njl_process_start(s->pid);return current&&current!=s->start;
}
static int nsq_stop(const NativeServiceIdentity*s){
 if(nsq_gone(s))return 1;
 if(__system_property_set("ctl.stop","x2d2-capture-trial"))return 0;
 uint64_t until=njl_clock()+15000;
 do{if(nsq_gone(s))return 1;struct timespec delay={0,20000000};nanosleep(&delay,NULL);}while(njl_clock()<until);
 return 0;
}
#endif
