/*

   Event logger

   Copyright 2009 Nudge Pty Ltd
   Author: Mark Parncutt

*/
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <time.h>
#include "eventlog.h"

static FILE *fp;

extern int eventlog_open(char *filename) {
    fp = fopen(filename, "a");
    if (fp == NULL) {
        fprintf(stderr, "eventlog.c: fatal: could not open file %s for appending.\n", filename);
        return -1;
    } else return 0;
}

extern int eventlog_close() {
    int returnval;
    returnval = fclose(fp);
    fp = NULL;
    return returnval;
}

extern void eventlog(char *fmt, ...) {
    va_list args;
    char time_string[128];
    struct tm *tmnow;
    time_t now;

    if (fp != NULL) {
        time(&now);
        if (!(tmnow = localtime(&now)))
            strcpy(time_string, "?");
        else
            strftime(time_string, 128, "%F %H:%M:%S", tmnow);
        fprintf(fp, "%s ", time_string);
        va_start(args, fmt);
        vfprintf(fp, fmt, args);
        va_end(args);
        fprintf(fp, "\n");
        fflush(fp);
    }
#ifdef DEBUG
    va_start(args, fmt);
    vprintf(fmt, args);
    va_end(args);
    printf("\n");
    fflush(stdout);
#endif
}
