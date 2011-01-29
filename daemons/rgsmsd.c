/*

   Nudge SMS Daemon

   Copyright (C) 2007 - 2009 Nudge Pty Ltd
   Authors: Mark Parncutt, James Ramsay
   
   Modified for myRobogals by Mark Parncutt, 2011

*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <signal.h>
#include "nudge_sql.h"
#include "smsglobal.h"
#include "rgsmsd.h"
#include "pidfile.h"
#include "eventlog.h"

static int doexit = 0;
static void handle_exit();

int main(int argc, char **argv) {
	/* MySQL variables */
	MYSQL *updateconn;
	MYSQL *utf8conn;
	MYSQL_RES *res;
	MYSQL_ROW row;
	MYSQL_RES *res2;
	MYSQL_ROW row2;
	char query[100];

	/* SMS variables */
	char msg[8192];
	char sender_id[17];
	int route_id;
	int unicode;
	int split;
	int count;
	int m_id = 0;
	int r_id = 0;
	int msgarray[2][101][2];

	/* Control variables */
	int i = 0;
	int j = 0;
	int oddeven = 0;
	sigset_t sigset;
	int otherpid = 0;
	char procdirname[20];
	char c;
	int foreground = 0;

	/* Check/create pidfile */
	otherpid = pidfile_check(RGSMSD_PIDFILE);
	if (otherpid > 0) {
		sprintf(procdirname, "/proc/%d", otherpid);
		struct stat st;
		if (stat(procdirname, &st) != 0) {
			fprintf(stderr, "rgsmsd is already running!\n");
			exit(-1);
		} else {
			pidfile_destroy(RGSMSD_PIDFILE);
		}
	}
	//pidfile_create(RGSMSD_PIDFILE, getpid());

	/* Parse command-line options */
	while ((c = getopt(argc, argv, "f")) != -1) {
		switch (c) {
			case 'f':
				foreground = 1;
				break;
			case '?':
				fprintf(stderr, "Unknown option -%c\n", optopt);
				fprintf(stderr, "rgsmsd not started.\n");
				return -1;
		}
	}

	/* 
	   Add some signals to the list of signals we want to block during a batch:
		SIGINT - equivalent of Ctrl-C, default behaviour is to terminate program
		SIGTERM - signal sent by the OS to tell a program to stop (e.g. from "killall rgsmsd")
	*/
	sigemptyset(&sigset);
	sigaddset(&sigset, SIGINT);
	sigaddset(&sigset, SIGTERM);
	signal(SIGINT, handle_exit);
	signal(SIGTERM, handle_exit);

	/* Initialise SMS APIs */
	if (smsglobal_smsinit() != 0) {
		fprintf(stderr, "rgsmsd: Failed to initialise SMS API, exiting\n");
		return -1;
	}
	
	if (eventlog_open(RGSMSD_ERROR_LOG) != 0) exit(-1);

	updateconn = mysql_init(NULL);
	if (connecttodb(updateconn) != 0) {
		fprintf(stderr, "Couldn't connect to MySQL (update connection), exiting.\n");
		return -1;
	}
	utf8conn = mysql_init(NULL);
	if (connecttodb(utf8conn) != 0) {
		fprintf(stderr, "Couldn't connect to MySQL (utf8 connection), exiting.\n");
		return -1;
	}
	mysql_set_character_set(utf8conn, "utf8");
	mysql_query(utf8conn, "SET NAMES 'utf8'");

	/* Daemonise unless foreground flag given */
	if (!foreground) {
		i = fork();
		if (i < 0) {
			fprintf(stderr, "rgsmsd: there is no fork\n");
			exit(-1);
		}
		if (i>0) {
			printf("rgsmsd started.\n");
			/* Parent process exits */
			exit(0);
		}
	} else {
		printf("rgsmsd running...\n");
	}

	/* The neverending loop begins... */
	while(1) {

		/* 
		   Block some signals while processing a batch.
		   Program termination in the middle of a batch could
		   potentially result in multiple SMSes being sent.
		*/
		sigprocmask(SIG_BLOCK, &sigset, NULL);

		mysql_query(utf8conn, "SELECT m.id AS m_id, "
				  "m.body, m.senderid, m.unicode, m.split, "
				  "r.to_number, r.gateway, r.id AS r_id "
				"FROM rgmessages_smsmessage AS m, "
				  "rgmessages_smsrecipient AS r "
				"WHERE m.id = r.message_id "
				  "AND m.status = 0 AND r.status IN (0, 20, 22) "
				  "AND r.scheduled_date < NOW() "
				"LIMIT 100");

		res = mysql_use_result(utf8conn);
		i = 0;
		while((row = mysql_fetch_row(res)) != NULL) {
			/* Protection against multiples */
			r_id = atoi(row[7]);

			msgarray[oddeven][i][0] = r_id;
			msgarray[oddeven][i][1] = 0;
#ifdef DEBUG
			printf("Adding %d\n", msgarray[oddeven][i][0]);
#endif
			for (j = 0; msgarray[!oddeven][j][0] != '\0'; j++) {
				if (msgarray[!oddeven][j][0] == r_id) {
					eventlog("%d; duplicate reminder",
							   r_id);
					exit(-1);
					break;
				}
			}
			
			strncpy(sender_id, row[2], 16);
			sender_id[16] = '\0';
			strcpy(msg, row[1]);
			unicode = atoi(row[3]);
			split = atoi(row[4]);

			/* Select route */
			/* Only one route is available right now */
			route_id = DEFAULT_ROUTE;
			
			msgarray[oddeven][i][1] = smsglobal_sendsms(msg, row[5], sender_id, r_id);
			i++;
		}
		mysql_free_result(res);
		res = NULL;

		msgarray[oddeven][i][0] = '\0';
		msgarray[oddeven][i][1] = '\0';

		/* Update database */
		for (j = 0; msgarray[oddeven][j][0] != '\0'; j++) {
#ifdef DEBUG
			printf("Reading %d\n", msgarray[oddeven][j][0]);
#endif
			sprintf(query, "UPDATE `rgmessages_smsrecipient` SET `status` = %d WHERE `id` = %d", msgarray[oddeven][j][1], msgarray[oddeven][j][0]);

			// For messages which will be retried, disable the multiple-message protection
			if (msgarray[oddeven][j][2] == 20 || msgarray[oddeven][j][2] == 22) {
				msgarray[oddeven][j][0] = 0;
			}

			mysql_query(updateconn, query);
			mysql_commit(updateconn);
		}

		oddeven = !oddeven;
		
		// Flag completed jobs as completed
		mysql_query(utf8conn, "SELECT id FROM rgmessages_smsmessage WHERE `status` = 0");
		res = mysql_use_result(utf8conn);
		while((row = mysql_fetch_row(res)) != NULL) {
			m_id = atoi(row[0]);
			sprintf(query, "SELECT COUNT(*) FROM rgmessages_smsrecipient WHERE `status` IN (0, 20, 22) AND `message_id` = %d", m_id);
			mysql_query(updateconn, query);
			res2 = mysql_use_result(updateconn);
			row2 = mysql_fetch_row(res2);
			count = atoi(row2[0]);
			mysql_free_result(res2);
			
			if (count == 0) {
				sprintf(query, "UPDATE rgmessages_smsmessage SET `status` = 1 WHERE `id` = %d", m_id);
				mysql_query(updateconn, query);
				mysql_commit(updateconn);
			}
		}
		mysql_free_result(res);

		/* It's now safe to allow the program to exit, if requested */
		sigprocmask(SIG_UNBLOCK, &sigset, NULL);
		if (doexit) break;

		usleep(250000);
	}

	smsglobal_smsclose();
	mysql_close(utf8conn);
	utf8conn = NULL;
	mysql_close(updateconn);
	updateconn = NULL;
	eventlog_close();
	pidfile_destroy(RGSMSD_PIDFILE);
	return 0;
}

static void handle_exit() {
#ifdef DEBUG
	printf("Caught signal, exiting\n");
#endif
	doexit = 1;
}
