#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "pidfile.h"

void pidfile_create(char *pidfile, int pid) {
	FILE *fp;
	fp = fopen(pidfile, "w");

	if (!fp) {
		fprintf(stderr, "Fatal: could not open pidfile %s for writing\n", pidfile);
		exit(-1);
	}

	fprintf(fp, "%d\n", pid);
	fclose(fp);
}

void pidfile_destroy(char *pidfile) {
	unlink(pidfile);
}

int pidfile_check(char *pidfile) {
	FILE *fp;
	int pid;
	fp = fopen(pidfile, "r");

	if (!fp) {
		/* pidfile does not exist */
		return 0;
	} else {
		fscanf(fp, "%d\n", &pid);
	}
	return pid;
}
