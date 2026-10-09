/* 自写有限测试顺序；任何停机尝试后都尝试恢复原服务。
 * 未确认临时子进程退出时，禁止并行启动第二个存储进程。 */
typedef struct {void *ctx;int (*idle)(void*);int (*stop)(void*);int (*trial)(void*);
 int (*reap)(void*);int (*restore)(void*);} PsAlbumTrialOps;
static int ps_album_trial_sequence(PsAlbumTrialOps *o){
 if(!o->idle(o->ctx))return 2;
 int tested=0;
 if(o->stop(o->ctx))tested=o->trial(o->ctx);
 if(!o->reap(o->ctx))return 4;
 if(!o->restore(o->ctx))return 5;
 return tested?0:1;
}
