/* 生命周期顺序；设备实现或测试替身通过明确回调提供。 */
#ifndef PS_INIT_TRIAL_SEQUENCE
#define PS_INIT_TRIAL_SEQUENCE
typedef struct {
 void *ctx;
 int (*set)(void *,const char *,const char *);
 int (*observe)(void *);
} PsTrialOps;
static int ps_trial_restore(PsTrialOps *o){
 /* 必须确认试验实例停止，才允许重新启动原厂实例。 */
 if(!o->set(o->ctx,"stop","x2d2-capture-trial"))return 0;
 if(!o->set(o->ctx,"start","camera-service"))return 0;
 if(!o->set(o->ctx,"start","camera-test"))return 0;
 return o->set(o->ctx,"start","camera-gui");
}
static int ps_trial_load(PsTrialOps *o){
 /* 先正常停止 D-Bus 客户端，避免上次客户端回调崩溃；此处不请求曝光。 */
 return o->set(o->ctx,"stop","camera-gui")&&
        o->set(o->ctx,"stop","camera-test")&&
        o->set(o->ctx,"stop","camera-service")&&
        o->set(o->ctx,"start","x2d2-capture-trial")&&o->observe(o->ctx);
}
static int ps_trial_clients(PsTrialOps *o){
 return o->set(o->ctx,"start","camera-test")&&o->set(o->ctx,"start","camera-gui");
}
static int ps_trial_restore_with_clients(PsTrialOps *o){
 return o->set(o->ctx,"stop","camera-gui")&&o->set(o->ctx,"stop","camera-test")&&ps_trial_restore(o);
}
static int ps_trial_adopt_direct(PsTrialOps *o){
 /* The capture service and camera-test already run; only retire the GUI stub. */
 return o->set(o->ctx,"stop","camera-gui")&&o->observe(o->ctx);
}
#endif
