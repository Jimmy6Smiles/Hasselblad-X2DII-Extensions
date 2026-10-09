/* Two bounded boot phases; no service control, exposure or photo access. */
#define _GNU_SOURCE
#include <sys/stat.h>
#include <sys/xattr.h>
#include <dirent.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define P "/system/x2d2-boot-v2"
#define R "/dev/x2d2-integrated-v1"
#define S "/dev/x2d2-shutter-v1"
#define N "/dev/x2d2-pregdc-trial"
#define A "/dev/x2d2-album-refresh-v1"
#define U "/dev/x2d2-menu-session-v1"
static void die(const char *s) { perror(s); exit(1); }
static const char *path(const char *s, char *b) {
#ifdef HOST_TEST
 const char *root=getenv("FIXTURE"); if(!root)exit(2);
#else
 const char *root="";
#endif
 if(snprintf(b,1024,"%s%s",root,s)>=1024)exit(2);return b;
}
static void dir(const char *s,int label) {
 char b[1024];path(s,b);if(mkdir(b,0700))die(s);
#ifndef HOST_TEST
 const char context[]="u:object_r:sel_device:s0";
 if(label&&setxattr(b,"security.selinux",context,sizeof context,0))die(s);
#else
 (void)label;
#endif
}
static void write_all(int fd,const void *data,size_t n) {
 const char *p=data;while(n){ssize_t k=write(fd,p,n);if(k<0&&errno==EINTR)continue;if(k<=0)die("write");p+=k;n-=(size_t)k;}
}
static void textfile(const char *s,const char *text) {
 char b[1024];int fd=open(path(s,b),O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
 if(fd<0)die(s);write_all(fd,text,strlen(text));if(close(fd))die("close");
}
static void copy(const char *src,const char *dst) {
 char a[1024],b[1024],buf[65536];struct stat st;
 int in=open(path(src,a),O_RDONLY|O_NOFOLLOW|O_CLOEXEC);if(in<0)die(src);
 if(fstat(in,&st)||!S_ISREG(st.st_mode))die("source type");
 int out=open(path(dst,b),O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);if(out<0)die(dst);
 for(;;){ssize_t n=read(in,buf,sizeof buf);if(n<0&&errno==EINTR)continue;if(n<0)die("read");if(!n)break;write_all(out,buf,(size_t)n);}
 if(close(in)||close(out))die("close");
}
static void linkfile(const char *src,const char *dst) {
 char a[1024],b[1024];struct stat st;path(src,a);path(dst,b);
 if(lstat(a,&st)||!S_ISREG(st.st_mode))die(src);
 if(symlink(a,b))die(dst);
}
static void early(void) {
 const char *dirs[]={R,S,N,A,U,"/dev/x2d2-direct-boot",NULL};
 for(int i=0;dirs[i];i++)dir(dirs[i],1);
 dir("/dev/x2d2-storage-prepare-once",0);dir(R"/jobs",0);dir(R"/cache",0);dir(R"/scratch",0);
 copy(P"/shutter.so",S"/shutter.so");copy(P"/album-observer.so",A"/album-observer.so");
 /* Capture constructor consumes this gate; keep it before dispatch. */
 textfile(N"/authorized.once","PREGDC_JOB_SCOPED_NATIVE_COLOR_V1\n");
 char p[1024];DIR *d=opendir(path(P"/ui",p));if(!d)die("ui");
 struct dirent *e;errno=0;
 while((e=readdir(d))){if(e->d_name[0]=='.')continue;
  char src[512],dst[512];
  if(snprintf(src,sizeof src,P "/ui/%s",e->d_name)>=(int)sizeof src||snprintf(dst,sizeof dst,U "/%s",e->d_name)>=(int)sizeof dst)exit(2);
  linkfile(src,dst);errno=0;
 }
 if(errno)die("readdir");if(closedir(d))die("closedir");
}
static void late(void) {
 copy(P"/diagnostic-iq.bin",N"/diagnostic-iq.bin");copy(P"/native-color.conf",N"/candidate.conf");copy(P"/native-color.sp",N"/candidate.sp");
 const char *names[]={"integrated-job","integration-service","native-auto6","worker","raw-pack","full-jpeg","zoom-server","overlap-prepare","overlap-container","readiness-check","reboot-reconcile","native-first-frame-scoped","native-job-cache","native-job-render","native-preview-commit","native-stream-render","jpeg-stream-join","first-frame-jpeg","jpeg-flow-pack",NULL};
 for(int i=0;names[i];i++){char src[512],dst[512];snprintf(src,sizeof src,P"/%s",names[i]);snprintf(dst,sizeof dst,R"/%s",names[i]);linkfile(src,dst);}
 textfile(S"/integration.once","AUTHORIZED_RETAIN_INPUTS_INTEGRATION\n");textfile(S"/load.once","AUTHORIZED_NO_CAPTURE\n");
}
static int run(const char *phase) {
 umask(077);
 if(!strcmp(phase,"early"))early();else if(!strcmp(phase,"late"))late();
 else if(!strcmp(phase,"probe")){
  dir("/dev/x2d2-fast-init-probe",1);
  copy(P"/album-observer.so","/dev/x2d2-fast-init-probe/copy.so");
  linkfile(P"/worker","/dev/x2d2-fast-init-probe/worker");
 }else return 2;return 0;
}
#ifdef HOST_TEST
int main(int argc,char **argv){return argc==2?run(argv[1]):2;}
#else
__attribute__((constructor))static void entry(void) {
 const char *v=getenv("X2D2_BOOT_PREP");if(!v)return;
 if(getuid()!=0)_exit(126);char phase[16];if(strlen(v)>=sizeof phase)_exit(126);strcpy(phase,v);
 unsetenv("X2D2_BOOT_PREP");unsetenv("LD_PRELOAD");_exit(run(phase));
}
#endif
