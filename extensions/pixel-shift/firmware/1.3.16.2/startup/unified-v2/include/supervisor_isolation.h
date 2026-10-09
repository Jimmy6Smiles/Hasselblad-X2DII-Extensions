/* 自写启动门槛：setsid 不会改变 Android 的进程回收 cgroup。
 * 不迁移进程、不修改 cgroup；未知布局一律拒绝热重启测试。 */
#ifndef PS_SUPERVISOR_ISOLATION_H
#define PS_SUPERVISOR_ISOLATION_H
#include <stdio.h>
#include <string.h>
#include <unistd.h>
static int ps_own_account_group(const char *text, long pid) {
 char expected[96];
 if(pid<=1)return 0;
 int n=snprintf(expected,sizeof expected,"/uid_0/pid_%ld",pid);
 if(n<0||(size_t)n>=sizeof expected)return 0;
 int found=0;
 for(const char *line=text;*line;){
  const char *end=strchr(line,'\n');if(!end)end=line+strlen(line);
  const char *colon=memchr(line,':',(size_t)(end-line));
  const char *path=colon?memchr(colon+1,':',(size_t)(end-colon-1)):NULL;
  if(!path)return 0;
  /* 只认已经核对的 Android acct 控制器，不把 cpuset/memory 当成回收隔离。 */
  size_t controllers=(size_t)(path-colon-1);
  if(controllers==7&&!memcmp(colon+1,"cpuacct",7)){
   if(found++||end-path-1!=n||memcmp(path+1,expected,(size_t)n))return 0;
  }
  line=*end?end+1:end;
 }
 return found==1;
}
static int ps_supervisor_isolated(void){
 char text[4096];FILE *f=fopen("/proc/self/cgroup","r");if(!f)return 0;
 size_t n=fread(text,1,sizeof text-1,f);int ok=!ferror(f)&&feof(f);fclose(f);
 text[n]=0;return ok&&ps_own_account_group(text,(long)getpid());
}
#endif
