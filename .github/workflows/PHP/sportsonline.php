<?php
$url = "https://sportsonline.gl/prog.txt";

$text = file_get_contents($url);

// Regular expression to match the pattern (time, event, URL)
$pattern = '/(\d{2}:\d{2})\s+(.*?)\s+\|\s+(https?:\/\/[^\s]+)/';

// Extract matches
preg_match_all($pattern, $text, $matches, PREG_SET_ORDER);

// Create an array to store results
$result = [];

date_default_timezone_set("Asia/Bangkok");

foreach ($matches as $match) {
    // Parse the time and add 7 hours
    $original_time = $match[1];
    $newTime = date("H:i", strtotime($original_time . " +7 hours"));
    
    // Create the updated name with the new time
    $updatedName = $newTime . " " . $match[2];
    
    $result[] = [
        'name' => $updatedName,
        'image' => 'https://static.thairath.co.th/media/dFQROr7oWzulq5Fa5LJEXNHgK8Nkou0mFfNIBOUFttbzB1Odu55E3VaV0f8gNyuUy8L.jpg',
        'url' => $match[3]
    ];
}

// Convert the array to JSON
$json = json_encode($result, JSON_PRETTY_PRINT);

// Output the JSON
echo '{ "name": "<a href='.$url .' target=_blank>sportsonline</a>",<br>';
echo '"image": "https://static.thairath.co.th/media/dFQROr7oWzulq5Fa5LJEXNHgK8Nkou0mFfNIBOUFttbzB1Odu55E3VaV0f8gNyuUy8L.jpg",<br>';
echo '"author": "' . 'update' . ' ' . date("d/m/Y H:i") . '",<br>';
echo '"url": "", <br> "stations":  <br>';
// Output the JSON
echo $json;
echo '}';
?>

