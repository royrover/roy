<!DOCTYPE html>
<html>
<body>


<?php
$link = "https://www.sports-stream.info/schedule.php";	 
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL,($link));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);


$title = array();
$date = array();
$url = array();
date_default_timezone_set("Asia/Bangkok");

$result = curl_exec($ch);
    

preg_match_all('(((\d{2}:\d{2})(<\/span>)( .+?))(<a href=")(.+?id=\d{1,3}))', $result,$titles);
$title = $titles[1];

preg_match_all('(\d{2}:\d{2})', $result,$times);
$time = $times[0];
	
preg_match_all('(\/ch.php\?id=\d{1,3})', $result,$urls);
$url = $urls[0];


//echo $result;
//print_r($title);
//echo '<br><br>';
//print_r($time);
//echo '<br><br>';
//print_r($url);
//echo '<br><br>';
//print_r($file);


 $img = "https://www.totalsportal.com/wp-content/uploads/2021/12/Sports-Pictures.jpg";  

curl_close($ch);
echo '<div id="goodContent">';

echo  '{ "name": "<a href="'.$link.'" target=_blank>sports-stream.info</a>",<br> "image": "'.$img.'",<br> "url" : "", <br> "author": "'.'update'.' '.date("d/m/Y H:i").'",<br>  "stations": [<br>';

for($i=0;$i<count($title); $i++);
for($i=0;$i<count($time); $i++);
for($i=0;$i<count($url); $i++)
{    
    $time_1 = substr($title[$i],0,5);
    $d=date_create($time_1);
    date_add($d,date_interval_create_from_date_string("+4 Hours"));				
	$tot =  date_format($d,"H:i");
    $name = $tot.' '.substr($title[$i],13);
//    $piece = 'https://www.sports-stream.site'.$url[$i];    
    $piece = 'https://www.sports-stream.info'.str_replace('ch.php?id=','ch/ch',$url[$i]).'.php';
    $star = file_get_contents($piece);

    preg_match('/((<iframe src="\/)(.+ch=.+?)")/',$star, $matches);    
    $url_piece = "https://www.sports-stream.info/".$matches[3];
				
	 
    echo '{ "name": "<span style="color:blue;font-weight:light">'.substr($name,0,-3).'</span>",<br> "image":"'.$img.'", "url": "'.$url_piece.'", "referer": "https://www.sports-stream.info","userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36","playInNatPlayer": "true"},<br>';
  
}


    echo ']<br>},<br>';


?>
<div class="box">
<center><button class="button-85" type="button" role="button" onclick="copyEvent('goodContent')"><a style="text-align: center;"><span style="color: #1f9dc4;">Copy</span></a></center>
</div>
</div>


<script>
    function copyEvent(id)
    {
        var str = document.getElementById(id);
        window.getSelection().selectAllChildren(str);
        document.execCommand("Copy")
    }
</script>



</span>
</body>
</html>
