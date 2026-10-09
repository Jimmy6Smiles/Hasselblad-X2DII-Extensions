#ifndef PS_STORAGE_EXIT_POLICY_H
#define PS_STORAGE_EXIT_POLICY_H
/* 未接管、或监督器正在停止时，不写永久禁用；真实接管失败仍保护。 */
static int ps_storage_should_disable(int interrupted,int power_ok,int recovery_intent){
 return !interrupted&&power_ok&&recovery_intent;
}
#endif
