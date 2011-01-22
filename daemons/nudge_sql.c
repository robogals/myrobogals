/*

   MySQL API

   Copyright 2007 - 2009 Nudge Pty Ltd
   Author: Mark Parncutt

*/

#include <mysql.h>
#include <stdio.h>
#include "nudge_sql.h"

int connecttodb(MYSQL *conn) {
   my_bool reconnect = 1;
   
   mysql_options(conn, MYSQL_OPT_RECONNECT, &reconnect);

   /* Connect to database */
   if (!mysql_real_connect(conn, SQL_HOST, SQL_USER, SQL_PASS, SQL_DB, 0, NULL, 0)) {
      fprintf(stderr, "Could not connect to MySQL: %s\n", mysql_error(conn));
      return -1;
   }
   return 0;
}
