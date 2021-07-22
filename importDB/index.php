<?php
    // include ('../connect_db.php');
    // session_start();
    // --- Check LDAP ----//
        // error_reporting(0);

        # ป้องกันการ SQL Injection 
        # โดยการใช้ $mysqli -> real_escape_string( ) เป็นฟังก์ชันสำหรับเลี่ยงการใช้ตัวอักขระพิเศษในคำสั่ง sql เช่น เครื่องหมาย " เครื่องหมาย ' เป็นต้น 
        $mysqli = new mysqli("localhost","root","");
        $user = $mysqli -> real_escape_string($argv[1]);
        $pass = $mysqli -> real_escape_string($argv[2]);
        
        
        if(isset($user)){
                
          //Include PHPLDAP Class File
          require "ldappsu.php"; # เรียก ldapp ของระบบ psu Passport เพื่อ ตรวจสอบ password และ user

          //DC1(VM),2(RACK),7(VM)-Hatyai,DC3(RACK)-Pattani,DC5(RACK)-Surat,DC6(RACK)-Trang
          $server = array("dc2.psu.ac.th","dc7.psu.ac.th","dc1.psu.ac.th");
          $basedn = "dc=psu,dc=ac,dc=th";
          $domain = "psu.ac.th";
          
          //Call function authentication
        //   error_reporting(0);
          $ldap = authenticate($server,$basedn,$domain,$user,$pass);
          echo($ldap);
          # echo ข้อมูลที่จะเอาไปใช้ ใน Django เพราะว่า Django ดักข้อมูล ที่ผ่านการ echo ใน php ได้
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
