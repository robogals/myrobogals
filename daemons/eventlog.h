/*

   Event logger

   Copyright 2009 Nudge Pty Ltd
   Author: Mark Parncutt

*/
extern int eventlog_open(char *filename);
extern int eventlog_close();
extern void eventlog(char *fmt, ...);
