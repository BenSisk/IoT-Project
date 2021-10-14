<?php
$data = file_get_contents("php://input");
$events = json_decode($data, true);

$result = getPos();
$lat = $result[0];
$long = $result[1];
$location = getCountry($lat, $long);
if ($events["name"] == "Alexa")
{
	sendWebhook($location);
}

function sendWebhook($event)
{
    $url = "https://maker.ifttt.com/trigger/returnToIFTTT/json/with/key/cr8iY6hqRPL8POTSdQWSR4";
	$headers = [ 'Content-Type: application/json; charset=utf-8' ];
	$POST = [$event];

	$ch = curl_init();
	curl_setopt($ch, CURLOPT_URL, $url);
	curl_setopt($ch, CURLOPT_POST, true);
	curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
	curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($POST));
	$response = curl_exec($ch);
}

function getPos()
{
	$url = "http://api.open-notify.org/iss-now.json";
	$ch = curl_init();
	curl_setopt($ch, CURLOPT_URL, $url);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	$response = curl_exec($ch);
	curl_close($ch);
	$temp = json_decode($response, true);
	$lat = $temp["iss_position"]["latitude"];
	$long = $temp["iss_position"]["longitude"];
	return array($lat, $long);
}

function getCountry($lat, $long)
{
	$apikey = file_get_contents("key.txt");
	$url = "https://maps.googleapis.com/maps/api/geocode/json?latlng={$lat},{$long}&sensor=false&key={$apikey}";
	$ch = curl_init();
	curl_setopt($ch, CURLOPT_URL, $url);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	$response = curl_exec($ch);
	curl_close($ch);
	$temp = json_decode($response, true);
	$components = $temp["results"][1]["address_components"];
	$location = "The location of the International Space Station is currently unavailable";
	foreach ($components as $c)
	{
		if (in_array("country", $c["types"]) or in_array("natural_feature", $c["types"]))
		{
			$location = "The International Space Station is currently located above {$c["long_name"]}";
		}
	}
	echo $location;
	return $location;
}
?>