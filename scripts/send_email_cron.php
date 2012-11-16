#!/usr/bin/php
<?php
/*
	myRobogals send email script
	
	The "send email" page in myRobogals actually just adds outgoing
	email to a queue in MySQL; this script does the actual sending.
	It should be running on a cron job in the background on the server.
*/

set_time_limit(0);
date_default_timezone_set('UTC');

// kill script if alredy running
if ($fp = @fopen("/tmp/robogals-cron-email-lock", 'r')) die();

// create lockfile
$fp = fopen("/tmp/robogals-cron-email-lock", 'w');
fclose($fp);

require_once "Mail.php";

$params = array(
	'host' => '127.0.0.1',
	'port' => 25,
	'auth' => false,
	'persist' => false
);

//do {
	$dbh = mysql_connect('localhost', 'myrobogals', 'myrobogals');
//	sleep(1);
//} while (!$dbh);
mysql_select_db('myrobogals');

//while (1) {

	// Ensure connection hasn't dropped
//	if (!mysql_ping($dbh)) {
//		do {
//			$dbh = mysql_connect('localhost', 'myrobogals', 'myrobogals');
//			sleep(1);
//		} while (!$dbh);
//		mysql_select_db('myrobogals');
//	}

	$sql = "SELECT * FROM rgmessages_emailmessage WHERE `status` = 0 ORDER BY `date` DESC";
	$result = mysql_query($sql);
	
	while($msg = mysql_fetch_assoc($result)) {
	
		$mailer = Mail::factory('smtp', $params);
		
		$headers = array(
			'From' => sprintf("%s <%s>", $msg['from_name'], $msg['from_address']),
			'Subject' => $msg['subject'],
			'Reply-To' => $msg['reply_address']
		);
		if ($msg['from_address'] == 'media-bounces@robogals.org') {
			$headers['List-Unsubscribe'] = 'media-unsubscribe@robogals.org';
			$headers['Precedence'] = 'bulk';
		}
		
		if ($msg['html'] == 1) {
			$uniqid = uniqid();
			$headers['Content-Type'] = "multipart/alternative; boundary=robogals{$uniqid}";
		}

		$sql = sprintf("SELECT * FROM rgmessages_emailrecipient WHERE `message_id` = %d AND `status` = 0 AND `scheduled_date` < NOW()", $msg['id']);
		$result2 = mysql_query($sql);
		
		while ($recipient = mysql_fetch_assoc($result2)) {
	
			$headers['To'] = sprintf("%s <%s>", $recipient['to_name'], $recipient['to_address']);
			$to = $recipient['to_address'];
			
			if ($msg['html'] == 1) {
				$body = "--robogals{$uniqid}
Content-Type: text/html; charset=\"utf-8\"
Content-Transfer-Encoding: base64

";
				$now = time();
				$beg = strtotime("2001-01-01");
				$datediff = $now - $beg;
				$ts = floor($datediff/(60*60*24));
				$unicd = sha1(sprintf("%s%s", $recipient['user_id'], $ts));
				$unicode = "";
				for ($i = 0; $i < strlen($unicd); $i = $i + 2) {
					$unicode = $unicode.$unicd[$i];
				}
				$uniqurl = sprintf('<a href="https://my.robogals.org/unsubscribe/%s/%s-%s/1/">unsubscribe<a>', base_convert($recipient['user_id'], 10, 36), base_convert($ts, 10, 36), $unicode);
				$body .= chunk_split(base64_encode(str_replace('{{to_name}}', $recipient['to_name'], str_replace('{{email_id}}', $recipient['id'], str_replace('{{unsubscribe}}', $uniqurl, $msg['body'])))));
				$body .= "

--robogals{$uniqid}--
";
			} else {
				$body = $msg['body'];
			}

			$mail_result = $mailer->send($to, $headers, $body);
			
			if (PEAR::isError($mail_result)) {
				
				switch ($mail_result->getCode()) {
					
					case PEAR_MAIL_SMTP_ERROR_CREATE:
						die("Couldn't create a Net_SMTP object");
					
					case PEAR_MAIL_SMTP_ERROR_CONNECT:
						// Error connecting to SMTP - try again
						$status = 0;
						break;
					
					case PEAR_MAIL_SMTP_ERROR_AUTH:
						die("SMTP authentication failed");
					
					case PEAR_MAIL_SMTP_ERROR_FROM:
						// No 'From' address - permanent failure
						$status = 3;
						break;
					
					case PEAR_MAIL_SMTP_ERROR_SENDER:
						// Invalid 'From' address - permanent failure
						$status = 4;
						break;
					
					case PEAR_MAIL_SMTP_ERROR_RECIPIENT:
						// Invalid 'To' address - permanent failure
						$status = 5;
						break;
					
					case PEAR_MAIL_SMTP_ERROR_DATA:
						// Failed to send message data - try again
						$status = 0;
						break;

					default:
						$status = 0;
						break;
				}
					
			} else {
				// Sent
				$status = 1;				
			}

			$sql = sprintf("UPDATE rgmessages_emailrecipient SET `status` = %d WHERE `id` = %d", $status, $recipient['id']);
			mysql_query($sql);

			sleep(0.1);
		}
		
		unset($mailer);
		
		mysql_free_result($result2);
		
		$sql = sprintf("SELECT COUNT(*) FROM rgmessages_emailrecipient WHERE `message_id` = %d AND `status` = 0", $msg['id']);
		$result2 = mysql_query($sql);
		$count = mysql_fetch_row($result2);
		if (intval($count[0]) == 0) {
			$sql = sprintf("UPDATE rgmessages_emailmessage SET `status` = 1 WHERE `id` = %d", $msg['id']);
			mysql_query($sql);
		}
		mysql_free_result($result2);

	}
	mysql_free_result($result);


	// remove lock file
	unlink("/tmp/robogals-cron-email-lock");
	
	// Wait 0.5 seconds before looking in the database again
//	sleep(0.5);
//}
?>
