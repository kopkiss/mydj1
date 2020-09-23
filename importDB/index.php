<?php
    // include ('../connect_db.php');
    // session_start();
    // --- Check LDAP ----//
        $user = $argv[1];
        $pass = $argv[2];
        // echo ($user);
        // echo ($pass );
        if(isset($user)){
          // echo ("in if"); 
          //Include PHPLDAP Class File
          require "ldappsu.php";
          //DC1(VM),2(RACK),7(VM)-Hatyai,DC3(RACK)-Pattani,DC5(RACK)-Surat,DC6(RACK)-Trang
          $server = array("dc2.psu.ac.th","dc7.psu.ac.th","dc1.psu.ac.th");
          $basedn = "dc=psu,dc=ac,dc=th";
          $domain = "psu.ac.th";
          $username = $user;
          $password = $pass;
          //Call function authentication
          error_reporting(0);
          $ldap = authenticate($server,$basedn,$domain,$username,$password);
          echo $ldap[0]; 
          echo ",";
          echo $ldap[1]['personid'];
          // if($ldap[0]==1){
          //   echo "<br/>>> User Profile <<<br/>";
          //   echo "Account Name : ".$ldap[1]['accountname']."<br/>";
          //   echo "Employee ID/Student ID : ".$ldap[1]['personid']."<br/>";
          //   echo "Citizen ID : ".$ldap[1]['citizenid']."<br/>";
          //   echo "CN : ".$ldap[1]['cn']."<br/>";
          //   echo "DN : ".$ldap[1]['dn']."<br/>";
          //   echo "Campus : ".$ldap[1]['campus']."(".$ldap[1]['campusid'].")<br/>";
          //   echo "Department : ".$ldap[1]['c']."(".$ldap[1]['departmentid'].")<br/>";
          //   echo "Work Detail : ".$ldap[1]['workdetail']."<br/>";
          //   echo "Position ID : ".$ldap[1]['positionid']."<br/>";
          //   echo "Description : ".$ldap[1]['description']."<br/>";
          //   echo "Display Name : ".$ldap[1]['displayname']."<br/>";
          //   echo "Detail : ".$ldap[1]['detail']."<br/>";
          //   echo "Title Name : ".$ldap[1]['title']."(".$ldap[1]['titleid'].")<br/>";
          //   echo "First Name : ".$ldap[1]['firstname']."<br/>";
          //   echo "Last Name : ".$ldap[1]['lastname']."<br/>";
          //   echo "Sex : ".$ldap[1]['sex']."<br/>";
          //   echo "Mail : ".$ldap[1]['mail']."<br/>";
          //   echo "Other Mail : ".$ldap[1]['othermail']."<br/>";
          // }
      }
     // --- Check LDAP ----//
?>
