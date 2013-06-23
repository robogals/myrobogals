/*

   SMSGlobal API client using libcurl

   Copyright 2009 Nudge Pty Ltd
   Author: Mark Parncutt
   
   Modified for myRobogals by Mark Parncutt, 2011

*/

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <curl/curl.h>

// 2013-05-17
//#include <curl/types.h>

#include <curl/easy.h>
#include "smsglobal.h"
#include "rgsmsd.h"
#include "nudge_sql.h"
static MYSQL *smsconn;

static smsglobal_id_t smsglobal_id;
static int status;
static char buffer[4];

int smsglobal_smsinit() {
    smsconn = mysql_init(NULL);
    if (connecttodb(smsconn) != 0) {
        fprintf(stderr, "smsinit: could not connect to MySQL database\n");
        return -1;
    }
    return curl_global_init(CURL_GLOBAL_ALL);
}

void smsglobal_smsclose() {
    mysql_close(smsconn);
    smsconn = NULL;
}

static void write_smsglobal_id() {
    char query[128];
    sprintf(query, "UPDATE `rgmessages_smsrecipient` SET `gateway_msg_id` = '%s' WHERE `id` = %d",
            smsglobal_id.smsglobal_msg_id,
            smsglobal_id.r_id);
    mysql_query(smsconn, query);
}

static size_t parse_smsglobal_output(void *ptr, size_t size, size_t nmemb, FILE *stream) {
    fprintf(stream, "%s", (char*)ptr);
#ifdef DEBUG
    printf("Got response from SMS gateway: %s\n", (char*)ptr);
#endif

    if (strncmp((char*)ptr, "OK: 0", 5) == 0) {
        strncpy(smsglobal_id.smsglobal_msg_id, (char*)(ptr+63), 16);
        smsglobal_id.smsglobal_msg_id[16] = '\0';
        status = 0;   /* success */
        if (smsglobal_id.r_id > 0)
            write_smsglobal_id();
    } else if (strncmp((char*)ptr, "ERROR", 5) == 0) {
    	strncpy(buffer, (char*)(ptr+7), 3);
    	if ((status = atoi(buffer)) == 0) status = -1;
    } else {
        status = -1;  /* failure */
    }
    return (size * nmemb);
}

int smsglobal_sendsms(char *msg, char *dest, char *sender_id, int r_id) {
    CURL *curl;
#ifndef SMSTEST
    CURLcode res;
#endif
    FILE *outputfp;
    char time_string[128];
    struct tm *tmnow;
    time_t now;
    char *encoded1;
    char *encoded2;

    struct curl_httppost *formpost=NULL;
    struct curl_httppost *lastptr=NULL;
    struct curl_slist *headerlist=NULL;
    static const char buf[] = "Expect:";

    smsglobal_id.r_id = r_id;

#ifdef DEBUG
    printf("smsglobal.c: message: %s, destination: %s\n", msg, dest);
#endif

    curl = curl_easy_init();

    curl_formadd(&formpost,
        &lastptr,
        CURLFORM_COPYNAME, "action",
        CURLFORM_COPYCONTENTS, "sendsms",
        CURLFORM_END);
    curl_formadd(&formpost,
        &lastptr,
        CURLFORM_COPYNAME, "user",
        CURLFORM_COPYCONTENTS, SMSGLOBAL_SMS_USER,
        CURLFORM_END);
    curl_formadd(&formpost,
        &lastptr,
        CURLFORM_COPYNAME, "password",
        CURLFORM_COPYCONTENTS, SMSGLOBAL_SMS_PASS,
        CURLFORM_END);
    curl_formadd(&formpost,
        &lastptr,
        CURLFORM_COPYNAME, "to",
        CURLFORM_COPYCONTENTS, dest,
        CURLFORM_END);
    curl_formadd(&formpost,
        &lastptr,
        CURLFORM_COPYNAME, "maxsplit",
        CURLFORM_COPYCONTENTS, "10",
        CURLFORM_END);
    encoded1 = curl_easy_escape(curl, msg, 0);
    encoded2 = curl_easy_escape(curl, encoded1, 0);
    curl_formadd(&formpost,
        &lastptr,
        CURLFORM_COPYNAME, "text",
        CURLFORM_COPYCONTENTS, encoded2,
        CURLFORM_END);
    curl_free(encoded1);
    curl_free(encoded2);
    curl_formadd(&formpost,
    	&lastptr,
    	CURLFORM_COPYNAME, "from",
    	CURLFORM_COPYCONTENTS, sender_id,
    	CURLFORM_END);

    /* initalize custom header list (stating that Expect: 100-continue is not wanted */
    headerlist = curl_slist_append(headerlist, buf);
    if (curl) {
        /* Set options */
        curl_easy_setopt(curl, CURLOPT_URL, SMSGLOBAL_SMS_URL);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headerlist);
        curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, SMSGLOBAL_SMS_CHECK_CERT);
        curl_easy_setopt(curl, CURLOPT_HTTPPOST, formpost);

        /* This callback will both write to the SMS log and parse the output
           for the SMS ID, which is written to MySQL   */        
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, parse_smsglobal_output);
        outputfp = fopen(SMSGLOBAL_SMS_LOG, "a");
        if (outputfp == NULL) {
            fprintf(stderr, "smsglobal.c: fatal: could not open file " SMSGLOBAL_SMS_LOG " for appending.\n");
            exit(-1);
        }
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, outputfp);

        /* Start log entry.  The callback function from curl will finish it */
        time(&now);
        if (!(tmnow = localtime(&now)))
            strcpy(time_string, "?");
        else
            strftime(time_string, 128, "%F %H:%M:%S", tmnow);
        fprintf(outputfp, "%s; %d; Destination: %s; Message: %s; ", 
                        time_string, r_id, dest, msg);

        /* Do it!  Unless we're just testing :) */
#ifdef SMSTEST
        fprintf(outputfp, "Test only.\n");
        status = 0;
#else
        /* Note that the callback function from curl_easy_perform will, unless
           a curl error occurs, write the log file entry and also set the
           variable 'status'  */
        res = curl_easy_perform(curl);
        if (res != 0) {
            fprintf(outputfp, "Curl error %d\n", res);
            status = -1;
        }
#endif

        /* Clean up */
        curl_easy_cleanup(curl);
        fclose(outputfp);
        curl_formfree(formpost);
        curl_slist_free_all(headerlist);
        
        /* Convert SMSGlobal status to Nudge status */
#ifdef DEBUG
		printf("SMSGlobal status %d; ", status);
#endif
		switch (status) {
			case 0: // SMS sent
				status = 10; // SMS sent
				break;
			case -1: // Curl error
				status = 22; // Request timed out
				break;
			case 1: // Message length is invalid
			case 2: // Command length is invalid
			case 3: // Invalid Command ID
			case 4: // Incorrect BIND
			case 14: // Invalid password
				status = 21; // Permanent error at SMSC
				break;
			case 5: // Already in bound state
			case 8: // System error
			case 12: // Message ID is invalid
			case 13: // Cannot bind to MeX
			case 69: // Submit SM failed
			case 400: // Send message timed-out
			case 401: // System temporarily disabled
			case 402: // No response from SMSGlobal SMSC
				status = 20; // Temporary error at SMSC
				break;
			case 88: // Exceeded allowed message limits
				status = 19; // Limits exceeded
				break;
			case 10: // Invalid source address
				status = 18; // Construction error
				break;
			case 11: // Invalid destination address
			case 102: // Destination not covered or Unknown prefix
				status = 9; // Number invalid
				break;
			default:
				status = 5; // Failed
				break;
		}
#ifdef DEBUG
		printf("send_sms returning %d\n", status);
#endif
        return status;
    } else {
        fprintf(stderr, "smsglobal.c: fatal: could not initialise curl\n");
        exit(-1);
    }
}
