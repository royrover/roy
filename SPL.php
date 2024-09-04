<?php
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, "https://sportsonline.gl/prog.txt");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$link = "https://sportsonline.gl/prog.txt";
$result = curl_exec($ch);

curl_close($ch);
#echo $result;

$DAY = array();
$url1 = array();


date_default_timezone_set("Asia/Bangkok");

   preg_match_all('/\n((S|M|T|W|F).+)/', $result,$titles);
  $DAY = $titles[0];   

   $pattern = '/SUNDAY|MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY/';		
   $url1 = preg_split($pattern, $result);	

echo  '{ "name": "<a href="'.$link.'" target=_blank>sportsonline</a>",<br> "image": "https://i.xtemus.com/file/4219.jpg",<br> 
"url": "", <br> "author": "'."update ".date("d/m/Y H:i").'",<br> "stations":  [<br>';
	
for ($i = 0; $i<count($DAY); $i++) {
	
	$day = $DAY[$i];
	$h1 = $url1[$i+1];
	preg_match_all('/(\d{2}:\d{2}.+)(\s+\|)/',$h1, $matches);
    $title = $matches[1];
	preg_match_all('/(https.+.php)/',$h1, $matches);
    $url_0 = $matches[0];	
 
//echo $day;	
//echo $h1;
//print_r($time);
//echo '<br><br>'; 
//print_r($title);
//echo '<br><br>';
//print_r($url_0);
//print_r($title_final);
//echo '<br><br>';
//print_r($url_final);

echo ' {<br>"name": "<span style="background:#d0ff14"><font style="font-size:20px">'.'SCHEDULE '.$day.'</font></span>",<br>
"image": "https://i.xtemus.com/file/4219.jpg",<br>
"url": "",<br>
"import": false<br>
},<br>
';	
for ($j = 0; $j<count($title); $j++) {
      $star_piece = $title[$j];
	  $time_1 = substr($star_piece,0,5);
      $d=date_create($time_1);
      date_add($d,date_interval_create_from_date_string("+6 Hours"));				
	  $tot =  date_format($d,"H:i");
      $name_group = $tot.' '.substr($star_piece,6);
	  $piece = $url_0[$j];

if(strpos($name_group, " F1") !== false) { 
  $img = 'https://static.thairath.co.th/media/dFQROr7oWzulq5Fa6rBWfbuBQreka9qj61nu9h8JNa7t5oflhTYa838cNbnpfUAcqQs.jpg';
 }elseif(strpos($name_group, " Moto") !== false) {
  $img = 'https://w0.peakpx.com/wallpaper/592/604/HD-wallpaper-moto-gp-2022-motogp-2022-games-games.jpg';
 }elseif(strpos($name_group, " Tennis") !== false) {
  $img = 'https://images.sbs.com.au/dims4/default/db8a225/2147483647/strip/true/crop/3179x1788+0+273/resize/1280x720!/quality/90/?url=http%3A%2F%2Fsbs-au-brightspot.s3.amazonaws.com%2Fdrupal%2Fnews%2Fpublic%2Fdylan_alcott_3.jpg';  
 }elseif(strpos($name_group, " Boxing") !== false) {
  $img = 'https://wallpapersmug.com/download/1280x720/6fed2b/boxing-glove-sports.jpg';  
 }else{
  $img = 'https://static.thairath.co.th/media/dFQROr7oWzulq5Fa5LJEXNHgK8Nkou0mFfNIBOUFttbzB1Odu55E3VaV0f8gNyuUy8L.jpg';
 }


echo  '{ "name": "<span style="color:blue;font-weight:light">'.$name_group.'</span>",<br> "image": "'.$img.'",<br>"url": "'.$piece.'",<br>"userAgent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14","isHost": "true"},<br>';
}

}
echo ']<br>},<br>';

?>
