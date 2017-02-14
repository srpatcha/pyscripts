#!/bin/sh
set -e
 
#Creating a Log file for QL010D unit test.   
touch /adp/bin/secureDms/pyscripts/unittest_files/ql_unitest.log
if [ $? -eq 0 ]
then
    QLulog=/adp/bin/secureDms/pyscripts/unittest_files/ql_unitest.log
else
    touch /adp/logs/ql_unitest.log
    QLulog=/adp/logs/ql_unitest.log
fi

echo "unit test log file created in location : $QLulog" >  $QLulog

echo "System information"                      >> $QLulog
echo "User $USER on machine name : $HOSTNAME " >> $QLulog
date                                           >> $QLulog

function Unit_test_status(){
if [ $1 -eq 1 ]
then
    echo "realtimeupdate.sh error to update Telnet switch ." >> $QLulog
	exit 1;
elif [ $1 -eq 0 ]
then
    echo "telnet to SSH unit test switch is working well!" >> $QLulog
	exit 0;
fi
} 

#testing OF component code update
echo "testing OF036<= component calling realtime update from LaunchConfig_LaunchConfigService.setConfiguredValue() by setting status with ZL010D" >> $QLulog

function set_telnet_status(){
#/adp/bin/secureDms/realtimeupdate.sh "TelnetService" "$?" >> $QLulog
script72="/adp/bin/secureDms/setconnstatus.sh"
	
if [ $1 -eq 1 ]
then
    $script72  1 ; >> $QLulog   #turn off telnet and SSH on
	
 elif [ $1 -eq 2 ]
 then
    $script72  2 ; >> $QLulog  #turn on telnet and SSH off
	
 elif [ $1 -eq 3 ]
 then
    $script72  3 ; >> $QLulog  #turn on telnet and SSH on
fi

}
   
telnet_state()
{ checkconf_status=`/sbin/chkconfig --list telnet | awk '{print $2}'`

 if [[ ("$checkconf_status" = "off" ) ]]; then
    echo "$HOSTNAME: telnet is off" >> $QLulog
 else
    echo "$HOSTNAME: telnet is on" >> $QLulog
 fi
}


#checking SQL databse value of telnet status.
DB_telnet_value()
{
sql23="select configured_value
from wi.wi_portal_configuration_value
where portal_configuration_value_code='TelnetService'";
database_value=`psql -U adp_apps -d adp_dms -c "$sql23" | sed -n '3p'|xargs` 
}


#setting telnet status in databse value to work with DRIVE UI.
DB_telnet_value	
if [ "$database_value" = "TRUE" ]
    then
	    echo "Telnet service is running. DB value is $database_value"  >> $QLulog
	    echo "trying to set telnet off "                               >> $QLulog
        set_telnet_status '1'                                          >> $QLulog
	    telnet_state 
		DB_telnet_value
		if [ "$database_value" = "TRUE" ]
		then
				echo "The Telnet turn off failed in this test." >> $QLulog
				Unit_test_status '1'
		else
				echo "setting telnet status back to DB value : TRUE"  >> $QLulog
		        set_telnet_status '3'                                 >> $QLulog
				DB_telnet_value
				Unit_test_status '0'
		fi	
        
elif [ "$database_value" = "FALSE" ]
    then
        echo "Telnet service is not running. DB value is $database_value"  >> $QLulog
	    echo "trying to set telnet on and SSH off"                         >> $QLulog
        set_telnet_status '2'                                              >> $QLulog
	    telnet_state
	    DB_telnet_value
		if [ "$database_value" = "FALSE" ]
		then
			echo "The value is not set TRUE failed in this test. realtimeupdate.sh error" >> $QLulog
			Unit_test_status '1'
		else
			echo "setting telnet status back to DB value : $database_value" >> $QLulog
			set_telnet_status '2'                                           >> $QLulog
			/sbin/chkconfig --list sshd                                     >> $QLulog
			Unit_test_status '0';
		fi	
        
fi
set_telnet_status '2' 
#END of unit test script for QL010D
