function updateTextBoxCounter() {

   var w = ("abcdefghijklmnopqrstuvwxyz"
       + "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@$_ !#%&()*+,-./:;<=>?\"\'");
   var whash = {};
   for (var i = 0; i < w.length; i++)
       whash[w.charAt(i)] = true;

   var unicodeFlag = 0;
   var extraChars = 0;
   var msgCount = 0;

   var msg = document.forms.fm_sendsms.body.value;
   var agent = navigator.userAgent.toLowerCase()
   if(agent.indexOf('firefox') > 0)
		msg = msg.replace(/\n/g, "\r\n");
   if(agent.indexOf('safari') > 0)  {
		msg = msg.replace(/\n$/g, "");
		msg = msg.replace(/\n/g, "\r\n");
   }
   var m = msg.length;
   for(i=0; i<m && !unicodeFlag; i++) {
      if (whash[msg.charAt(i)]) {
      }
      else if (msg.charCodeAt(i) == 0xA3) {
      }
      else if (msg.charCodeAt(i) == 0xA5) {
      }
      else if (msg.charCodeAt(i) == 0xE8) {
      }
      else if (msg.charCodeAt(i) == 0xE9) {
      }
      else if (msg.charCodeAt(i) == 0xF9) {
      }
      else if (msg.charCodeAt(i) == 0xEC) {
      }
      else if (msg.charCodeAt(i) == 0xF2) {
      }
      else if (msg.charCodeAt(i) == 0xC7) {
      }
      else if (msg.charCodeAt(i) == 0x0A) {
      }
      else if (msg.charCodeAt(i) == 0x0D) {
      }
      else if (msg.charCodeAt(i) == 0xD8) {
      }
      else if (msg.charCodeAt(i) == 0xF8) {
      }
      else if (msg.charCodeAt(i) == 0xC5) {
      }
      else if (msg.charCodeAt(i) == 0xE5) {
      }
      else if (msg.charCodeAt(i) == 0x394) {
      }
      else if (msg.charCodeAt(i) == 0x3A6) {
      }
      else if (msg.charCodeAt(i) == 0x393) {
      }
      else if (msg.charCodeAt(i) == 0x39B) {
      }
      else if (msg.charCodeAt(i) == 0x3A9) {
      }
      else if (msg.charCodeAt(i) == 0x3A0) {
      }
      else if (msg.charCodeAt(i) == 0x3A8) {
      }
      else if (msg.charCodeAt(i) == 0x3A3) {
      }
      else if (msg.charCodeAt(i) == 0x398) {
      }
      else if (msg.charCodeAt(i) == 0x39E) {
      }
      else if (msg.charCodeAt(i) == 0xC6) {
      }
      else if (msg.charCodeAt(i) == 0xE6) {
      }
      else if (msg.charCodeAt(i) == 0xDF) {
      }
      else if (msg.charCodeAt(i) == 0xC9) {
      }
      else if (msg.charCodeAt(i) == 0xA4) {
      }
      else if (msg.charCodeAt(i) == 0xA1) {
      }
      else if (msg.charCodeAt(i) == 0xC4) {
      }
      else if (msg.charCodeAt(i) == 0xD6) {
      }
      else if (msg.charCodeAt(i) == 0xD1) {
      }
      else if (msg.charCodeAt(i) == 0xDC) {
      }
      else if (msg.charCodeAt(i) == 0xA7) {
      }
      else if (msg.charCodeAt(i) == 0xBF) {
      }
      else if (msg.charCodeAt(i) == 0xE4) {
      }
      else if (msg.charCodeAt(i) == 0xF6) {
      }
      else if (msg.charCodeAt(i) == 0xF1) {
      }
      else if (msg.charCodeAt(i) == 0xFC) {
      }
      else if (msg.charCodeAt(i) == 0xE0) {
      }
      else if (msg.charCodeAt(i) == 0x391) {
      }
      else if (msg.charCodeAt(i) == 0x392) {
      }
      else if (msg.charCodeAt(i) == 0x395) {
      }
      else if (msg.charCodeAt(i) == 0x396) {
      }
      else if (msg.charCodeAt(i) == 0x397) {
      }
      else if (msg.charCodeAt(i) == 0x399) {
      }
      else if (msg.charCodeAt(i) == 0x39A) {
      }
      else if (msg.charCodeAt(i) == 0x39C) {
      }
      else if (msg.charCodeAt(i) == 0x39D) {
      }
      else if (msg.charCodeAt(i) == 0x39F) {
      }
      else if (msg.charCodeAt(i) == 0x3A1) {
      }
      else if (msg.charCodeAt(i) == 0x3A4) {
      }
      else if (msg.charCodeAt(i) == 0x3A5) {
      }
      else if (msg.charCodeAt(i) == 0x3A7) {
      }
      else if (msg.charAt(i) == '^') {
         extraChars++;
      }
      else if (msg.charAt(i) == '{') {
         extraChars++;
      }
      else if (msg.charAt(i) == '}') {
         extraChars++;
      }
      else if (msg.charAt(i) == '\\') {
         extraChars++;
      }
      else if (msg.charAt(i) == '[') {
         extraChars++;
      }
      else if (msg.charAt(i) == '~') {
         extraChars++;
      }
      else if (msg.charAt(i) == ']') {
         extraChars++;
      }
      else if (msg.charAt(i) == '|') {
         extraChars++;
      }
      else if (msg.charCodeAt(i) == 0x20AC) {
         extraChars++;
      }
      else {
         unicodeFlag = 1;
      }
   }

   msgCount = m + extraChars;
   if (unicodeFlag) {
      if (m <= 80) {
         msgCount = 1;
         document.getElementById('InfoCharCounter').innerHTML = "" + (m) + " unicode characters, " + msgCount + " SMS message";
      }
      else {
         document.getElementById('InfoCharCounter').innerHTML = "" + (m) + " unicode characters - too long! Please reduce length!";
      }
   }
   else {
      if (msgCount <= 160) {
         msgCount = 1;
         document.getElementById('InfoCharCounter').innerHTML = "" + (m + extraChars) + " characters, " + msgCount + " SMS message";
      }
      else if (msgCount <= 1530) {
         msgCount += (153-1);
         msgCount -= (msgCount % 153);
         msgCount /= 153;
         document.getElementById('InfoCharCounter').innerHTML = "" + (m + extraChars) + " characters, " + msgCount + " SMS messages";
      } else {
         document.getElementById('InfoCharCounter').innerHTML = "" + (m + extraChars) + " characters - too long! Please reduce length!";
      }
   }
}
