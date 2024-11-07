<!DOCTYPE html>
<html>
<body>

<?php

$FW4F = "https://fw4free.com/view.php?id=2225";

 if (isset($_POST["link"])) $link = $_POST["link"]; else $link = "";
 if (isset($_POST["link_manual"]) && $_POST["link_manual"] !== "") $link = $_POST["link_manual"];
 
 	echo '<!DOCTYPE html>
	<html lang="th">
	<head>
	<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
      <!--Import Google Icon Font-->
      <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
      <!--Import materialize.css-->
      <link type="text/css" rel="stylesheet" href="/materialize/css/materialize.min.css"  media="screen,projection"/>
      <!--Let browser know website is optimized for mobile-->
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
	</head>
	<body>
	    <div class="container">
		  <nav>
<div class="elementor-widget-container">
<style>
h2 {text-align: center;}

</style>
			<h2 class="elementor-heading-title elementor-size-default">สร้าง w3u จากเว็บ</h2>		</div>
		  </nav>		
	<br>
	<form action="'.$_SERVER['REQUEST_URI'].'" method="POST">
      <div class="row">
        <div class="col s1">
		<label for="link" class="thick">website:</label>
		</div>
        <div class="col s5">
	<select name="link" id="link" class="browser-default">
           <option value='.$FW4F.' '; if ($link==$FW4F) echo 'selected="selected"'; echo '>fw4free.com - สร้าง w3u ซีรี่ย์</option>

	</select>
		</div>
        <div class="col s6">
	      <button class="btn waves-effect waves-light" type="submit" name="sumbit" value="1">Submit</button>
	    </div>
	 </div>
      <div class="row">
        <div class="col s1">
			<label for="link" class="thick">item:</label>
		</div>
		<div class="input-field col s8">
			<input type="text" name = "link_manual">
		</div>
	 </div>
	<span class="blue-text text-darken-2">ใส่ลิ้งค์ใน item เช่น   https://fw4free.com/view.php?id=2225 </span>
	<br>


';

if ($link !== '') {
	if (isset($_POST["source"]) && $_POST["source"] !== '') {
		$html = 	$_POST["source"];
	} else {
		
	$link_1 =$link;
	$html = file_get_contents($link);
	$result = htmlspecialchars($html, ENT_NOQUOTES, "UTF-8");
#	$html = curl_get_contents($link);
	
	}
    $dom = new DOMDocument;
    $internalErrors = libxml_use_internal_errors(true);
    #$dom->loadHTML($html);
    $dom->loadHTML('<?xml encoding="utf-8" ?>' . $html);
    $xpath = new DOMXPath($dom);

    
 if (strpos($link, "fw4free.com") !== false) {

            preg_match('/<h5>(.*?)<\/h5>/',$html, $matches);
            $name = $matches[1];

            $pattern = "/href=\"javascript:Play\('(\d+)','(\d+)'\);/";
            preg_match($pattern, $html , $matches);
			$iframeSrc = "https://fw4free.com/player2.php?channel=$matches[1]&id=$matches[2]";				

    $iframeHTML = "
        <div id='playerContainer'>
            <iframe 
                src='{$iframeSrc}' 
                width='100%' 
                height='700px' 
                allow='autoplay; fullscreen' 
                frameborder='0'>
            </iframe>
        </div>
    ";
    echo '<center><span style="background:#d0ff14"><font style="font-size:26px">'.$name.'</span</center>';
    echo '<br><br>';
    echo $iframeHTML;

 }
}   




?>







</body>
</html>
