
<?php

/*
   
    Tufin'den alınan NAT tablosunu veritabanına yazar
   (c) Samet Atalar

*/
error_reporting(E_ALL);
date_default_timezone_set('Europe/Istanbul');
global $allowedIP;
global $dbUser;
global $dbPass;
global $dbName;
$dbUser = "yourDBUsername";
$dbPass = 'yourDBPassword';
$dbName = "yourDBName";
$allowedIP = array("yourallowdIPlist");
if (in_array($_SERVER['REMOTE_ADDR'],$allowedIP)) {
    header("Content-Type: application/json; charset=UTF-8");
    $connection = new mysqli("localhost",$dbUser,$dbPass,$dbName);
    
    function getNATIP($ip) {
        #tek bir IPyi getirir
        global $connection;
        $resultArray=array();
        $result = $connection->query("select * from natip where privateip='$ip' or internetip='$ip' or f5node like '%ip%'") or die(json_encode(array("err"=>mysqli_error($connection))));
        if ($result->num_rows>0) {
            $resultArray = $result->fetch_array(MYSQLI_NUM);
            return $resultArray;
        }
        else return null;
    }

    function insertDB($internetip,$privateip) {
        global $dbUser;
        global $dbPass;
        global $dbName;
        global $connection;
        
        //$connection = new mysqli("localhost",$dbUser,$dbPass,$dbName) or die(json_encode(array("err"=>$connection->connection_error)));
            /*
                $internetip = dış ip
                $privateip = iç ip (private)
            */
            $simdiTarih = date("Y-m-d h:i:s");
            $checkDuplicate = $connection->query("SELECT * from natip where internetip='$internetip'") or die(json_encode(array("err"=>mysqli_error($connection))));
            if ($checkDuplicate->num_rows<1){
            /* $connection->query("INSERT INTO webservices(hostname,ip,folder,file,Appname,IPRestrictionInIIS,fullurl) 
                VALUES('$hostname','$ip','$folder','$file','$appname','$iprestriction','$fullurl')") or die(json_encode(array("err"=>mysqli_error($connection))));*/
                $stmt = $connection->prepare("INSERT INTO natip(internetip,privateip,created) VALUES(?,?,?)");
                $stmt->bind_param("sss",$internetip,$privateip,$simdiTarih);
                $stmt->execute();

                if ($connection){
                    echo json_encode(array("msg"=>"SUCCESS"));
                }
            
                else {
                    echo json_encode(array("msg"=>"ERROR! $internetip cannot insert to DB"));
                }
            }
            else {
                /*echo json_encode(array("err"=>"duplicate","msg"=>$internetip ." is duplicate"));*/

            $checkIP = getNATIP($internetip);
            if ($checkIP != null) {
                if ($checkIP[2]!=$privateip) {
                    //Tanımda değişiklik var güncelleniyor
                    updateDB($internetip,$privateip);
                }
                else echo json_encode(array("msg"=>"NOTICE: $internetip already defined to $privateip"));
            }
            else echo json_encode(array("msg"=>"NOTICE: $internetip is not exists nothing happened"));
            // if (strlen(checkIP["ip"])>1) updateDB($internetip,$privateip);
            }
        // $connection->close();
            
    }

    function updateDB($internetip,$privateip) {
        global $connection;
        //$intAccessStatus = (int)$accessStatus;
        $guncelTarih = date("Y-m-d h:i:s");
        //echo "Tarih:".$guncelTarih;
        //if (is_int($accessStatus)) {
        if (strlen($privateip)>2) {
            $checkpip=$connection->query("SELECT * from natip where privateip='$privateip'") or die(json_encode(array("err"=>mysqli_error($connection))));
            $checkpublicip=$connection->query("SELECT * from natip where internetip='$internetip'") or die(json_encode(array("err"=>mysqli_error($connection))));
            if($checkpip->num_rows>0) {
                if (isset($_POST["f5update"])) {
                    $f5node = htmlentities($_POST["f5node"]); // dizi olarak yazılacak
                    $connection->query("update natip set f5node='$f5node', updateddate='$guncelTarih' where privateip='$privateip'") or die(json_encode(array("err"=>mysqli_error($connection))));
                    echo json_encode(array("msg"=>"SUCCESS"));
                }
                else {
                    echo json_encode(array("msg"=>"NOTICE: Everything same for $internetip"));
                }
            }
            elseif ($checkpublicip->num_rows>0)  {
                    //sadece private ip değişiyor. python scriptinde private ip'nin eskisiyla aynı olup olmadığı kontrol ediliyor
                    $connection->query("update natip set privateip='$privateip', updateddate = '$guncelTarih' where internetip='$internetip'") or die(json_encode(array("err"=>mysqli_error($connection))));
                    if($connection) echo json_encode(array("msg"=>"SUCCESS: $internetip updated to $privateip"));
                    else echo json_encode(array("err"=>"ERROR: update $internetip has failed $privateip"));
            }
            else echo json_encode(array("err"=>"PUBLIC IP $internetip and private ip $privateip not found in database. therefore nothing happened"));
        }
        else echo json_encode(array("err"=>"ERROR: Missing parameter: Private ip was null"));
    }

    function getNATTable($start,$stop,$whichIP) {
        #$whichIP: Çıktı olarak ne isteniyor
        global $connection;
        if ($whichIP == "internetip") $result = $connection->query("select internetip from natip limit $start,$stop") or die(json_encode(array("err"=>mysqli_error($connection))));
        elseif ($whichIP == "privateip") $result = $connection->query("select privateip from natip limit $start,$stop") or die(json_encode(array("err"=>mysqli_error($connection))));
        else $result = $connection->query("select * from natip limit $start,$stop") or die(json_encode(array("err"=>mysqli_error($connection))));
        $natList = array();
        $i=0;
        while ($row = $result->fetch_row()) {
            $natList[$i] = $row;
            $i++;
        }
        
        echo json_encode(array("msg"=>"SUCCESS","nat"=>$natList));
    }

    function deleteIP($ip) {
        //veritabanındaki IP, yeni konfigürasyonda bulunmamışsa veritabanında o public IP silinir.
        global $connection;
        $delete = $connection->query("delete from natip where internetip='$ip'") or die(json_encode(array("err"=>mysqli_error($connection))));
        if($delete) echo json_encode(array("msg"=>"SUCCESS: deleted $ip"));
        else echo json_encode(array("err"=>"ERROR: COULD NOT DELETED: $ip"));
    }

    if ($connection->connect_errno) {
        echo json_encode(array("err"=>$connection->connect_error));
        exit();
    }
    else {
        if (isset($_POST['add']) && isset($connection)) {
            insertDB(
                htmlentities($_POST['internetip']),
                htmlentities($_POST['privateip']));
            //echo json_encode(array("msg"=>"ok"));
        }
        elseif (isset($_POST["update"])) {
            updateDB(
                htmlentities($_POST['internetip']),
                htmlentities($_POST['privateip']));
        }
        elseif (isset($_POST['geturl'])) {
            getNATTable(htmlentities($_POST['startlimit']),htmlentities($_POST['stoplimit']),htmlentities($_POST['whichip']));
        }
        elseif (isset($_POST['singleip']) && strlen($_POST["ip"])>4) {
            getNATIP(htmlentities($_POST["ip"]));
        }
        elseif (isset($_POST['deleteip']) && strlen($_POST["ip"])>4) {
            deleteIP(htmlentities($_POST["ip"]));
        }
        else {
            echo json_encode(array("err"=>"parameter missing","msg"=>"request was incomplete"));
        }
    }
}
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
}

?>
