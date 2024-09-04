<?php
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, "https://sportsonline.gl/prog.txt");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$result = curl_exec($ch);

curl_close($ch);
echo $result;
?>
