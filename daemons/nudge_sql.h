/*

   MySQL API

   Copyright 2007 - 2009 Nudge Pty Ltd
   Author: Mark Parncutt

*/

#include <mysql/mysql.h>

#define SQL_HOST "localhost"
#define SQL_USER "myrobogals"
#define SQL_PASS "myrobogals"
#define SQL_DB "myrobogals"

int connecttodb(MYSQL *conn);
