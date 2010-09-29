<?php
/**
 * RokBox System Plugin
 *
 * @package		Joomla
 * @subpackage	RokBox System Plugin
 * @copyright Copyright (C) 2009 RocketTheme. All rights reserved.
 * @license http://www.gnu.org/copyleft/gpl.html GNU/GPL, see RT-LICENSE.php
 * @author RocketTheme, LLC
 *
 * RokBox System Plugin includes:
 * ------------
 * SWFObject v1.5: SWFObject is (c) 2007 Geoff Stearns and is released under the MIT License:
 * http://www.opensource.org/licenses/mit-license.php
 * -------------
 * JW Player: JW Player is (c) released under CC by-nc-sa 2.0:
 * http://creativecommons.org/licenses/by-nc-sa/2.0/
 * 
 */
 
// Check to ensure this file is included in Joomla!
defined('_JEXEC') or die();
?>

1. Copyright and disclaimer
----------------


2. Changelog
------------
This is a non-exhaustive (but still near complete) changelog for
the RocketTheme phpBB3 bridge, including alpha, beta and release 
candidate versions.

Legend:

* -> Security Fix
# -> Bug Fix
+ -> Addition
^ -> Change
- -> Removed
! -> Note


----------- 2.1 Release [24-Jun-2009] ------------

24-Jun-2009
# auto-fix of height limits was still in for remote images.

----------- 2.0 Release [18-Jun-2009] ------------

18-Jun-2009 Djamil Legato
# PDF fix for all IE versions: the new Acrobat Reader was causing rendering issues.
# Fixed RokBox hiding out of the top margin when the image was higher than the browser window.
# RokBox doesn't auto-fix the height of images taller than the browser window (that wasn't a good idea after all).
# Fixed the captions animation calculation for when captions are empty.
^ New RegExp for YouTube! You can now just use YouTube links with all the options you want, RokBox takes care of it! (check out the demo).
- Removed High Quality option as now this is doable via the URI passed.
+ RokBox now handles remote images sizes for you! You don't have to specify those anymore!
+ The so desired and dreamed built-in FLV player is now truth, thanks to JW-Player (http://www.longtailvideo.com/players/jw-flv-player/)
+ RokBox now handles images not found and will let the user know with a nice graphic.

----------- 1.3 Release [18-Feb-2009] ------------

18-Feb-2008 Djamil Legato
+ Module support, you can load an element from the page with a specific id right into RokBox (<a rel="rokbox[module=login] ..>)
+ Fullscreen support, you can make RokBox going fullscreen by specifying the word "fullscreen" as size ({rokbox size=|fullscreen|}{/rokbox}
+ Percentages support, you can make RokBox calculating its size in percentages relative to the browser window ({rokbox size=|50% 30%|}{/rokbox})
# Opera position issue is now fixed, as well with many other minor fixes for it
+ Added support for videos m4v and audios m4a
^ RokBox now only renders when the doctype is HTML (note: this is for J! 1.5 only)
+ Added a new HD quality option for YouTube, you can enable or disable it from the System - RokBox options
^ All the supported video sharng have now a default size, if you don't specify it it will be used it, overriding the default RokBox size setting (note: You can still specify your own size as preferred)
^ Changed the default YouTube size according to its new format, now it is by default: 640x385 
# Fixed the Key Events. They now work. Previous, Next and ESC keys allow you to go backward and forward from an album and ESC to exit RokBox.

----------- 1.0 Release [05-Jun-2008] ------------

05-Jun-2008 Djamil Legato
# Fallback issue that had to be the IFrame.
# Bug in the captioning where the first time you opened RokBox it didn't fire correctly the caption causing it not showing up.
# Album names now support uppercase letters and number, not lowercase only.
# Issue in the Close button not hiding when closing rokbox.
# IE JS error in IE when closing RokBox with Explode or QuickSilver animations.
# Minor CSS issues in Themes that fix Explode animation.
# BackgroundColor parameter for Audio Objects was missing and causing display issues.
# Local URIs now works correctly and get loaded via IFrame instead of Ajax.
# More media formats support, the complete list is now:
	! Images: Links ending with .gif, .jpg, .jpeg, .png or .bmp
	! Generic Videos: Links ending with .mov, .qt, .mpeg, .divx, .avi, .xvid, .wmv, .wma, .wax, .wvx, .asx, .asf
	! Video Sharing Services: YouTube, DailyMotion, Metacafe, Google Video, Vimeo, Simple .swf files
	! Audio: Links ending with: .mp3, .wav
	! Local and Remote URIs
+ PDF Support
+ You can now avoid to specify sizes for: Generic Videos [320 x 240], Video Sharing Services (YouTube [425 x 344], DailyMotion [420 x 339], Metacafe [400 x 345], Google Video [400 x 325], Vimeo [400 x 225]), Audio [320 x 45] and images (LOCAL ONLY). The default sizes for those are built-in RokBox and would be used if you don't specify one. By setting your own size via "size=|width height|", you overwrite the built-in sizes.

----------------------- 1.0 Beta Release [13-May-2008] -----------------------

13-May-2008 Djamil Legato
! Initial release. 
 
------------ Initial Changelog Creation ------------
