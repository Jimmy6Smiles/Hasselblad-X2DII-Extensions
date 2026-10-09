/* 仅整包监督器构建使用；子进程与监督器属于同一独立 init cgroup。
 * camera-service 仍由另一个 init 服务运行，不能在这里直接 exec 代替。 */
#define IP_ROOT "/dev/x2d2-integrated-v1"
#ifndef IP_BOOT
#define IP_BOOT "/data/x2d2-integrated-v1"
#endif
static pid_t integration_children[3]={-1,-1,-1};
static pid_t integration_spawn(int which){
 pid_t pid=fork();if(pid)return pid;
 int fd=open(which==0?IP_ROOT"/backend.log":which==1?IP_ROOT"/zoom.log":IP_ROOT"/gui.log",O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
 if(fd<0)_exit(121);dup2(fd,1);dup2(fd,2);close(fd);
 if(which==0)execl(IP_ROOT"/integration-service",IP_ROOT"/integration-service","--resident-retain-inputs",(char*)0);
 else if(which==1)execl(IP_ROOT"/zoom-server",IP_ROOT"/zoom-server","/mnt/media_rw/ssd/DCIM","/mnt/media_rw/cfe/DCIM",IP_ROOT"/scratch","38407","resident",(char*)0);
 else{
  setenv("XDG_RUNTIME_DIR","/tmp",1);setenv("XDG_CACHE_HOME",IP_ROOT"/cache",1);
  setenv("QT_QPA_FONTDIR","/system/lib64/qt/lib/fonts",1);setenv("QML_DISABLE_DISK_CACHE","1",1);setenv("QT_SHADER_CACHE_DISABLE","1",1);
  execl(IP_ROOT"/gui",IP_ROOT"/gui","-platform","wayland-egl","--fullscreen",(char*)0);
 }
 _exit(127);
}
static int integration_stop_children(void){
#ifdef PS_NATIVE_COLOR_JOB
 /* Stop the DMA consumer before terminating ANY possible buffer owner.
  * A failed stop is not permission to kill the rendering worker. */
 while(!state("x2d2-capture-trial","stopped")){
  if(set_state(NULL,"stop","x2d2-capture-trial"))break;
  puts("NATIVE_QUIESCE_UNCONFIRMED_RETAINING_CHILDREN");nap();
 }
#endif
 int ok=1;
 for(int i=2;i>=0;i--){
  pid_t pid=integration_children[i];if(pid<=0)continue;int status=0;
  pid_t got=waitpid(pid,&status,WNOHANG);
  if(got==pid||(got<0&&errno==ECHILD)){integration_children[i]=-1;continue;}
  if(got<0){ok=0;continue;}
  kill(pid,SIGTERM);int result=bounded_wait(pid,&status,45000);
  if(result==0){kill(pid,SIGKILL);result=bounded_wait(pid,&status,1500);}
  if(result!=1)ok=0;else integration_children[i]=-1;
 }
 return ok;
}
static int integration_observe(void){
#ifdef PS_NATIVE_COLOR_JOB
 int native_cap=open(IP_ROOT"/native-drain-capable",O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
 if(native_cap<0)return 0;
 const char native_contract[]="STOP_NATIVE_BEFORE_OWNER_V1\n";
 int native_ok=write(native_cap,native_contract,sizeof native_contract-1)==sizeof native_contract-1&&!fsync(native_cap);close(native_cap);
 if(!native_ok)return 0;
#endif
 if(!set_state(NULL,"start","camera-test"))return 0;
 int unified=exact_file("/dev/x2d2-unified-boot/mode","DIRECT\n");
 int child_count=unified?2:3;
 for(int i=0;i<child_count;i++){
  integration_children[i]=integration_spawn(i);
  if(integration_children[i]<=0){integration_stop_children();return 0;}
 }
 puts("INTEGRATION_CHILDREN_STARTED_NOT_FEATURE_ACCEPTANCE");
 int ok=1;unsigned ticks=0;
 while(!interrupted){
#ifdef PS_NATIVE_COLOR_JOB
  if(access("/dev/x2d2-pregdc-trial/recovery.required",F_OK)==0){ok=0;break;}
#endif
  if(access(IP_ROOT"/stop",F_OK)==0)break;
  if(!state("x2d2-capture-trial","running")){ok=0;break;}
  if(unified&&!state("camera-gui","running")){ok=0;break;}
  for(int i=0;i<child_count;i++){
   int status=0;pid_t got=waitpid(integration_children[i],&status,WNOHANG);
   if(got==integration_children[i]){printf("INTEGRATION_CHILD_EXIT kind=%d status=%d\n",i,status);integration_children[i]=-1;ok=0;break;}
   if(got<0&&errno!=EINTR){ok=0;break;}
  }
  if(!ok)break;
  if(++ticks==150&&access(IP_BOOT "/accepted",F_OK)==0){
   if(unlink(IP_BOOT "/boot.pending")&&errno!=ENOENT){ok=0;break;}
   puts("ACCEPTED_BOOT_PROCESSES_ALIVE_NOT_JOB_ACCEPTANCE");
  }
  nap();
 }
 if(!integration_stop_children())return 0;
 char power[PROP_VALUE_MAX]={0};__system_property_get("sys.powerctl",power);
 if(!*power){int fd=open(IP_BOOT "/disabled",O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);if(fd>=0){fsync(fd);close(fd);}}
 return ok;
}
