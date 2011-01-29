/*

   SMSGlobal SMS gateway API using libcurl

   Copyright 2009 Nudge Pty Ltd
   Author: Mark Parncutt

*/

/* SMSGlobal gateway details */
#define SMSGLOBAL_SMS_URL "https://www.smsglobal.com/http-api.php"
#define SMSGLOBAL_SMS_USER "robogals"
#define SMSGLOBAL_SMS_PASS "f83gsr4"

/* Check SSL certificate of gateway? */
#define SMSGLOBAL_SMS_CHECK_CERT 1

/* Where to log outgoing messages */
#define SMSGLOBAL_SMS_LOG "/home/myrobogals/var/sms.log"

typedef struct {
    char smsglobal_msg_id[17];
    int r_id;
} smsglobal_id_t;

int smsglobal_smsinit();
void smsglobal_smsclose();
int smsglobal_sendsms(char *msg, char *dest, char *sender_id, int r_id);
