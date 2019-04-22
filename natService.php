<?php
//Admin paneline veri gönderir

error_reporting(E_ERROR);
global $allowedIP;
global $dbUser;
global $dbPass;
global $dbName;
$dbUser = "yourDBUsername";
$dbPass = 'yourDBPassword';
$dbName = "yourDBName";
//$allowedIP = array("yourallowdIPlist");
//if (in_array($_SERVER['REMOTE_ADDR'],$allowedIP)) {
    $connection = new mysqli("localhost",$dbUser,$dbPass,$dbName);
function getNATTableForPanel($start,$stop,$whichIP) {
    global $dbUser;
    global $dbPass;
    global $dbName;
    global $connection;
    
    if ($whichIP == "internetip") $result = $connection->query("select internetip from natip limit $start,$stop") or die(json_encode(array("err"=>mysqli_error($connection))));
    elseif ($whichIP == "privateip") $result = $connection->query("select privateip from natip limit $start,$stop") or die(json_encode(array("err"=>mysqli_error($connection))));
    else { $result = $connection->query("select * from natip limit $start,$stop") or die(json_encode(array("err"=>mysqli_error($connection))));}
    $natList = array();
    $i=0;
    while ($row = $result->fetch_row()) {
        $natList[$i] = $row;
        $i++;
    }
    
    return $natList;
}
    function getLast24Hour($change){
        global $dbUser;
        global $dbPass;
        global $dbName;
        global $connection;
        if ($change=="updated") {
            $result = $connection->query("SELECT * FROM natip WHERE updateddate > (NOW() - INTERVAL 24 HOUR)") or die(json_encode(array("err"=>mysqli_error($connection))));
        }
        elseif ($change=="created") {
            $result = $connection->query("SELECT * FROM natip WHERE created > (NOW() - INTERVAL 24 HOUR)") or die(json_encode(array("err"=>mysqli_error($connection))));
        }
    
        $natList = array();
        $i=0;
        while ($row = $result->fetch_row()) {
            $natList[$i] = $row;
            $i++;
        }
        return $natList;
    }
function countF5Pools() {
    global $dbUser;
    global $dbPass;
    global $dbName;
    global $connection;
    $result = $connection->query("select * from natip where f5node is not null") or die(json_encode(array("err"=>mysqli_error($connection))));
    return $result->num_rows;
}
    function AuthUsers($username) {
        //Kullanıcı oturum açabilir mi?
        global $dbUser;
        global $dbPass;
        global $dbName;
        global $connection;
        $huser=hash("SHA256",htmlentities($username));
        $result=$connection->query("select * from natadmin where aduser='$huser'") or die(mysqli_error($connection));
      //  $stmt->bind_param("s",$huser);
        //$stmt->execute();
        if($result->num_rows>0) return 1; 
        else return 0;
    }

    if (isset($_POST["nattable"])) {
        $start=htmlentities($_POST["start"]);
        $stop=htmlentities($_POST["stop"]);
        $nattable = getNATTableForPanel($start,$stop,1);
        echo json_encode($nattable);

    }
/*}
else {
    echo "
    <html>
    <head>
    <style type='text/css'>body { background-color: black; } </style>
    <title>Nothing to See Here</title>
    </head>
    <body>
    <p align='center'><img src='nothingtoSee.jpg' style='background-color:#FFFFFF;max-height:700px;margin:0 auto; align:center;'></p>
    </body>
    </html>
    ";
}*/
?>