/* 自写只读就绪检查；令牌 + 存活进程 + 原厂路径 + 已加载库，拒绝陈旧标记。 */
#ifndef PS_ALBUM_RUNTIME_H
#define PS_ALBUM_RUNTIME_H
#ifndef PS_ALBUM_REFRESH_ROOT
#define PS_ALBUM_REFRESH_ROOT "/dev/x2d2-album-refresh-v1"
#endif
static int album_runtime_ready(void){
 char text[64],extra,path[96],exe[128],line[1024];long pid=0;struct stat st;
 int fd=open(PS_ALBUM_REFRESH_ROOT"/ready",O_RDONLY|O_CLOEXEC|O_NOFOLLOW);if(fd<0)return 0;
 ssize_t n=-1;if(!fstat(fd,&st)&&S_ISREG(st.st_mode)&&st.st_uid==getuid()&&st.st_nlink==1&&st.st_size>0&&st.st_size<(off_t)sizeof text)n=read(fd,text,sizeof text-1);
 close(fd);if(n<=0)return 0;text[n]=0;
 if(sscanf(text,"ALBUM_RUNTIME_V1 %ld %c",&pid,&extra)!=1||pid<=1||pid>2147483647||kill((pid_t)pid,0))return 0;
 snprintf(path,sizeof path,"/proc/%ld/exe",pid);n=readlink(path,exe,sizeof exe-1);if(n<=0||n>=(ssize_t)sizeof exe-1)return 0;exe[n]=0;
 if(strcmp(exe,"/system/bin/camera-storage"))return 0;
 snprintf(path,sizeof path,"/proc/%ld/maps",pid);FILE *f=fopen(path,"r");if(!f)return 0;
 int found=0;while(fgets(line,sizeof line,f))if(strstr(line," " PS_ALBUM_REFRESH_ROOT "/album-observer.so\n"))found=1;
 fclose(f);return found;
}
#endif
