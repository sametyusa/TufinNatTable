# tufinnattable
Gathers NAT Table from Tufin Securetrack. If private ip is a F5 pool VIP scripts gets pool members.
<h2>Structure</h2>
<ul>
<li><b>get-TufinNATIP.py</b>: This scripts accesses to Tufin API and posts data to NatIPUploader.php You must edit device id list in this file. This script will be the first to run</li>
<li><b>get-F5PoolMember.py</b>: This script gathers virtual IP list from F5 bigip load balancers if you have any and post data to NatIPUploader.py You must edit device id list in this file. </li>
<li><b>NatIPUploader.php</b>: This script listens from python scripts and updates database. You must upload this to a webserver and  edit database credentials in this file.</li>
<li><b>natService.php</b>: this file delivers data to natadmin.php You must upload this to a webserver and  edit database credentials in this file.</li>
<li><b>natadmin.php</b>: This file is admin panel. Calls natService.php for required data. You must upload this to a webserver and  edit database credentials in this file.</li>
</ul>
<h2>Installation</h2>
<p>Add IP and credentials in scripts. Create database  Upload NATIPUploader.php to a webserver</p>
<p>MYSQL DB schema: natip </p>
<p>f5node will be comma seperated list</p>
<pre>
+-------------+--------------+------+-----+---------+----------------+
| Field       | Type         | Null | Key | Default | Extra          |
+-------------+--------------+------+-----+---------+----------------+
| id          | int(64)      | NO   | PRI | NULL    | auto_increment |
| internetip  | varchar(64)  | NO   |     | NULL    |                |
| privateip   | varchar(64)  | YES  |     | NULL    |                |
| f5node      | varchar(512) | YES  |     | NULL    |                |
| created     | datetime     | YES  |     | NULL    |                |
| updateddate | datetime     | YES  |     | NULL    |                |
+-------------+--------------+------+-----+---------+----------------+
</pre>
<p>MYSQL DB Schema: natadmin</p>
<p>note: Values in aduser column will be sha-256 hash of active directory usernames which granted access to the NAT admin page. You must add them manually</p>
<pre>
+--------+--------------+------+-----+---------+----------------+
| Field  | Type         | Null | Key | Default | Extra          |
+--------+--------------+------+-----+---------+----------------+
| id     | int(11)      | NO   | PRI | NULL    | auto_increment |
| aduser | varchar(512) | YES  |     | NULL    |                |
+--------+--------------+------+-----+---------+----------------+
</pre>
<p>Copy python scripts to a computer can access to the Tufin Securetrack. Run them regulary</p>

<h2>NAT Admin page</h2>
<p>NAT admin panel files are natService.php and natadmin.php. Edit LDAP server and database credentials both files then copy them to a webserver after you created and filed values into database. that's it</p>
<p>You will have to find a html5 template for nat admin panel</p>
