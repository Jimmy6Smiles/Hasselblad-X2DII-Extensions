/* No photograph access: bounded retry for an accepted installation with no job. */
static int boot_no_job(void){
 struct stat st;return lstat(RP_DATA"/pending",&st)<0&&errno==ENOENT;
}
static int boot_idle_retry(void){
 char b[128]={0},boot[40],archive[256];
 if(!boot_no_job()||!rp_boot(boot)||rp_read(FULL"/accepted",b,sizeof b-1)<0)return 0;
 memset(b,0,sizeof b);
 if(rp_read(FULL"/boot.pending",b,sizeof b-1)<0||strcmp(b,"FULL_FIRST_BOOT_AWAITING_USER\n"))return 0;
 /* One unclassified crash retry until a healthy boot clears boot.pending.
  * Known pre-service readiness timeouts do not consume this crash budget. */
 char status[128]={0};int transient=rp_read(FULL"/prepare.status",status,sizeof status-1)>0&&
  (!strcmp(status,"FAILED WAIT_CAMERA\n")||!strcmp(status,"FAILED WAIT_STORAGE\n"));
 if(!transient&&!rp_new(FULL"/empty-retry.used",boot))return 0;
 snprintf(archive,sizeof archive,FULL"/idle-boot.pending-%s",boot);
 return rp_sync(FULL)&&boot_no_job()&&rp_archive(FULL"/boot.pending",archive)&&rp_sync(FULL);
}
static int boot_clear_retry_budget(void){
 struct stat st;
 if(lstat(FULL"/boot.pending",&st)==0||errno!=ENOENT)return 0;
 if(unlink(FULL"/empty-retry.used")&&errno!=ENOENT)return 0;
 return rp_sync(FULL);
}
