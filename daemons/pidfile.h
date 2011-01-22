#define RGSMSD_PIDFILE "/var/home/myrobogals/var/rgsmsd.pid"

void pidfile_create(char *pidfile, int pid);
void pidfile_destroy(char *pidfile);
int pidfile_check(char *pidfile);
