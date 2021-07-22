<?php
//Function LDAPPSU Version 1.0.0
//Author : Jatuporn Chuchuay ISD CC PSU (Tel.2082)
//Update : 22/12/2014
// The LDAP server

// Authenticate the against server the domain\username and password combination.
function authenticate($server,$basedn,$domain,$username,$password)
{
 $auth_status = false;
 $i=0;
 while(($i<count($server))&&($auth_status==false)){
 $ldap = ldap_connect("ldap://".$server[$i]) or 
 $auth_status = false;
 ldap_set_option($ldap, LDAP_OPT_REFERRALS, 0);
 ldap_set_option($ldap, LDAP_OPT_PROTOCOL_VERSION, 3);
 $ldapbind = ldap_bind($ldap, $username."@".$domain,$password);
 if($ldapbind){
 if(empty($password)){
 $auth_status = false;
 }else{
 $result[0] = true;
 //Get User Info
 $result[1] = get_user_info($ldap,$basedn,$username);
 }
 }else{
 $result[0] = false;
 }
 ldap_close($ldap);
 $i++;
 }
 return $result;
}

function get_user_info($ldap,$basedn,$username)
{
 $user['cn'] = "";
 $user['dn'] = "";
 $user['accountname'] = "";
 $user['personid'] = "";
 $user['citizenid'] = "";
 $user['campus'] = "";
 $user['campusid'] = "";
 $user['department'] = "";
 $user['departmentid'] = "";
 $user['workdetail'] = "";
 $user['positionid'] = "";
 $user['description'] = "";
 $user['displayname'] = "";
 $user['detail'] = "";
 $user['title'] = "";
 $user['titleid'] = "";
 $user['firstname'] = "";
 $user['lastname'] = "";
 $user['sex'] = "";
 $user['mail'] = "";
 $user['othermail'] = "";
 $sr=ldap_search($ldap, $basedn, 
 "(&(objectClass=user)(objectCategory=person)(sAMAccountName=".$username."))", 
 array("cn", "dn", "samaccountname", "employeeid", "citizenid", "company",
 "campusid", "department", "departmentid", "physicaldeliveryofficename", "positionid", 
 "description", "displayname", "title", "personaltitle", "personaltitleid", "givenname", 
 "sn", "sex", "userprincipalname","mail"));
 $info = ldap_get_entries($ldap, $sr);

 $user['cn'] = $info[0]["cn"][0];
 $user['dn'] = $info[0]["dn"];
 $user['accountname'] = $info[0]["samaccountname"][0];
 $user['personid'] = $info[0]["employeeid"][0];
 $user['citizenid'] = $info[0]["citizenid"][0];
 $user['campus'] = $info[0]["company"][0];
 $user['campusid'] = $info[0]["campusid"][0];
 $user['department'] = $info[0]["department"][0];
 $user['departmentid'] = $info[0]["departmentid"][0];
 $user['workdetail'] = $info[0]["physicaldeliveryofficename"][0];
 $user['positionid'] = $info[0]["positionid"][0];
 $user['description'] = $info[0]["description"][0];
 $user['displayname'] = $info[0]["displayname"][0];
 $user['detail'] = $info[0]["title"][0];
 $user['title'] = $info[0]["personaltitle"][0];
 $user['titleid'] = $info[0]["personaltitleid"][0];
 $user['firstname'] = $info[0]["givenname"][0];
 $user['lastname'] = $info[0]["sn"][0];
 $user['sex'] = $info[0]["sex"][0];
 $user['mail'] = $info[0]["userprincipalname"][0];
 $user['othermail'] = $info[0]["mail"][0];
 return $user;
}
