<?php

// This information has been pulled out of index.php to make the template more readible.
//
// This data goes between the <head></head> tags of the template
// 
// 

$this->addStylesheet($this->baseurl."/templates/".$this->template."/css/template.css");
$this->addStylesheet($this->baseurl."/templates/".$this->template."/css/header-".$header_style.".css");
$this->addStylesheet($this->baseurl."/templates/".$this->template."/css/body-".$body_style.".css");
$this->addStylesheet($this->baseurl."/templates/".$this->template."/css/typography.css");
$this->addStylesheet($this->baseurl."/templates/system/css/system.css");
$this->addStylesheet($this->baseurl."/templates/system/css/general.css");
$this->addStylesheet($this->baseurl."/templates/".$this->template."/css/menu-".$mtype.".css");
if (JRequest::getVar('option') == 'com_k2') :
	$this->addStylesheet($this->baseurl."/templates/".$this->template."/css/k2.css");
endif;

$inlinestyle = "
	div.wrapper { ".$template_width."padding:0;}
	body { min-width:".$template_real_width."px;}
	#inset-block-left { width:".$leftinset_width."px;padding:0;}
	#inset-block-right { width:".$rightinset_width."px;padding:0;}
	#maincontent-block { margin-right:".$rightinset_width."px;margin-left:".$leftinset_width."px;}
	
	.s-c-s .colmid { left:".$leftcolumn_width."px;}
	.s-c-s .colright { margin-left:-".($leftcolumn_width + $rightcolumn_width)."px;}
	.s-c-s .col1pad { margin-left:".($leftcolumn_width + $rightcolumn_width)."px;}
	.s-c-s .col2 { left:".$rightcolumn_width."px;width:".$leftcolumn_width."px;}
	.s-c-s .col3 { width:".$rightcolumn_width."px;}
	
	.s-c-x .colright { left:".$leftcolumn_width."px;}
	.s-c-x .col1wrap { right:".$leftcolumn_width."px;}
	.s-c-x .col1 { margin-left:".$leftcolumn_width."px;}
	.s-c-x .col2 { right:".$leftcolumn_width."px;width:".$leftcolumn_width."px;}
	
	.x-c-s .colright { margin-left:-".$rightcolumn_width."px;}
	.x-c-s .col1 { margin-left:".$rightcolumn_width."px;}
	.x-c-s .col3 { left:".((rok_isIe(6)) ? $rightcolumn_width + 20 : $rightcolumn_width)."px;width:".$rightcolumn_width."px;}";
$this->addStyleDeclaration($inlinestyle);
?>

<?php if (rok_isIe()) :?>
<!--[if IE 8]>
<style type="text/css">
#horizmenu-surround {width: auto !important;}
</style>
<![endif]-->
<!--[if IE 7]>
<link href="<?php echo $this->baseurl; ?>/templates/<?php echo $this->template?>/css/template_ie7.css" rel="stylesheet" type="text/css" />	
<![endif]-->	
<?php endif; ?>
<?php if (rok_isIe(6)) :?>
<!--[if lte IE 6]>
<link href="<?php echo $this->baseurl; ?>/templates/<?php echo $this->template?>/css/template_ie6.css" rel="stylesheet" type="text/css" />
<script src="<?php echo $this->baseurl; ?>/templates/<?php echo $this->template?>/js/DD_belatedPNG.js"></script>
<script type="text/javascript">
	var pngClasses = ['.png', '#logo', '#horiz-menu', '#footer .readon1-l', '#footer .readon1-m', '#footer .readon1-r', '#showcase-section .readon1-l', '#showcase-section .readon1-m', '#showcase-section .readon1-r', '#rocket', '.module-top', '.module-top2', '.module-top3', '.module-inner', '.module-bottom', '.module-bottom2', '.module-bottom3', '.fusion-pill-l', '.fusion-pill-r', 'span.tabtext', '.feature-circles-sub', '.feature-circles .active', '.feature-block-top', '.feature-block-top2', '.feature-block-top3', '.feature-block-inner', '.feature-block-bottom', '.feature-block-bottom2', '.feature-block-bottom3'];
	
	window.addEvent('domready', function() {
	pngClasses.each(function(fixMePlease) {
		DD_belatedPNG.fix(fixMePlease);
	});
	});
</script>
<style type="text/css">
.round .module-surround5, .round2 .module-surround5, .round3 .module-surround5, .round4 .module-surround5, .round5 .module-surround5 {
right: expression((this.offsetParent.offsetWidth % 2) ? '-2px' : '-1px');
bottom: expression((this.offsetParent.offsetHeight % 2) ? '-2px' : '-1px');
}
.round .module-surround3, .round2 .module-surround3, .round3 .module-surround3, .round4 .module-surround3, .round5 .module-surround3, .module-surround5 {
right: expression((this.offsetParent.offsetWidth % 2) ? '-2px' : '-1px');
}
.round .module-surround4, .round2 .module-surround4, .round3 .module-surround4, .round4 .module-surround4, .round5 .module-surround4, .module-surround4 {
bottom: expression((this.offsetParent.offsetHeight % 2) ? '-2px' : '-1px');
}
</style>
<![endif]-->
<?php endif; ?>
<?php
/* Javascript Hooks for base uri */
	$tmpl_folder = "
		window.templatePath = '$template_path';
		window.uri = '{$this->baseurl}';
		window.currentStyle = '$tstyle';
	";
	$this->addScriptDeclaration($tmpl_folder);
?>
<?php 
if($enable_fontspans=="true") :
    $this->addScript($this->baseurl."/templates/".$this->template."/js/rokfonts.js");
    $rokfonts = 
    "window.addEvent('domready', function() {
		var modules = ['side-mod', 'showcase-panel', 'moduletable', 'article-rel-wrapper'];
		var header = ['h3','h2','h1'];
		RokBuildSpans(modules, header);
	});";
    $this->addScriptDeclaration($rokfonts);
endif;
if($clientside_date == "true" and $js_compatibility=="false") :
    $this->addScript($this->baseurl."/templates/".$this->template."/js/rokdate.js");
endif;
if(rok_isIe(6) and $enable_ie6warn=="true" and $js_compatibility=="false") : 
    $this->addScript($this->baseurl."/templates/".$this->template."/js/rokie6warn.js");
endif;
$this->addScript($this->baseurl."/templates/".$this->template."/js/rokutils.js");
if($enable_inputstyle == "true" and $js_compatibility=="false" and !rok_isIe(6)) :
    $this->addScript($this->baseurl."/templates/".$this->template."/js/rokutils.inputs.js");
	$exclusionList = "InputsExclusion.push($inputs_exclusion)";
	$this->addScriptDeclaration($exclusionList);
endif;