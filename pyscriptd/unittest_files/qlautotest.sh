#!/bin/sh
set -e

unset QLalog
#Creating a Log file for QL010D automation test.
touch /adp/bin/secureDms/pyscripts/unittest_files/ql_autotest.log
if [ $? -eq 0 ]
then
  echo "Successfully created log file"
  QLalog=/adp/bin/secureDms/pyscripts/unittest_files/ql_autotest.log
else
  touch /adp/logs/ql_autotest.log
  QLalog=/adp/logs/ql_autotest.log
fi

echo "ZL automation log file created path: $QLalog"


# #Tracking values for test results.
errors_value=0
results_value=0


function system_info(){

echo "DMS information_"                           > $QLalog
echo "User :$USER on machine Cnumber : $HOSTNAME" >> $QLalog
date                                             >> $QLalog
RUNELVL=`/sbin/runlevel | awk '{print $2}'`
echo "System RunLevel :$RUNELVL"                 >> $QLalog
/sbin/service sshd status                        >> $QLalog
/sbin/chkconfig --list sshd                      >> $QLalog   # SSH servcies on/off in DMS
#echo "Before test pass result values: $results_value and error_ values: $errors_value" >> $QLalog
BZ_MSI=`find /adp/3party/sda/sdmImports/BZ_SDM*  -iname  CDK_Terminal_Emulator_Patch2.msi`
 if [ -e $BZ_MSI ] ;
 then
     echo "Bluezone 6.2.3 delivered in this DMS " >> $QLalog
     results_value=`expr $results_value + 1`
 else
      echo "Bluezone 6.2.3 patch does not exists in this DMS. Test failed " >> $QLalog
      echo "May be Bluezone 6.2.3 installted from artifactory " >> $QLalog
      echo "BZ6.2.3 should be installted in PC machine else error in PC." >> $QLalog
      errors_value=`expr $errors_value + 1`
 fi

#verify putty registry key exists
 if [ -f /adp/home/www_serv/htdocs/paris/putty_winja.reg ] ;
  then
     echo "putty registry key generated in DMS " >> $QLalog
     results_value=`expr $results_value + 1`
  else
      echo "Test failed: putty registry key doesn't generated  " >> $QLalog
      errors_value=`expr $errors_value + 1`
  fi


}


system_info  # start information_ in log

#checking SQL databse value of Telnet status.
DB_telnet_value()
{
sql23="select configured_value
from wi.wi_portal_configuration_value
where portal_configuration_value_code='TelnetService'";
database_value=`psql -U adp_apps -d adp_dms -c "$sql23" | sed -n '3p'|xargs`
}

#checking SQL databse value of SSH status.
DB_SSH_value()
{
sql23s="select configured_value
from wi.wi_portal_configuration_value
where portal_configuration_value_code='SecureTerminalEmulator'";
database_sshvalue=`psql -U adp_apps -d adp_dms -c "$sql23s" | sed -n '3p'|xargs`
}

#get the telnet status.
telnet_state()
{ check_telnet_status=`/sbin/chkconfig --list telnet | awk '{print $2}'`

 if [[ ("$check_telnet_status" = "off" ) ]]; then
    echo "$HOSTNAME: telnet is off"           >> $QLalog
    DB_telnet_value
    echo "DB telnet value: $database_value"   >> $QLalog
 else
    echo "$HOSTNAME: telnet is on"            >> $QLalog
    DB_telnet_value
    echo "DB telnet value: $database_value"   >> $QLalog

 fi
}


#get the SSH status.
SSH_status()
{ check_SSH_status=`/sbin/service sshd status`

 if [[ $check_SSH_status = "running" ]]; then
        echo "$HOSTNAME: openssh-daemon SSH is running"    >> $QLalog
        DB_SSH_value
        echo "DB SSH value: $database_sshvalue"            >> $QLalog
 else
        echo "$HOSTNAME: openssh-daemon SSH is turned OFF" >> $QLalog
        DB_SSH_value
        echo "DB SSH value : $database_sshvalue"
 fi
}

#sotre the values in temp variables
telnet_state
SSH_status
Telnet_ORG=$database_value
SSH_ORG=$database_sshvalue

function set_telnet_SSH_status(){
#/adp/bin/secureDms/realtimeupdate.sh "TelnetService" "$?" >> $QLalog
script72="/adp/bin/secureDms/setconnstatus.sh"

if [ $1 -eq 1 ]
then
    $script72  1 ; >> $QLalog   #turn off telnet and SSH on
    results_value=`expr $results_value + 1`

 elif [ $1 -eq 2 ]
 then
    $script72  2 ; >> $QLalog  #turn on telnet and SSH off
    results_value=`expr $results_value + 1`
 elif [ $1 -eq 3 ]
 then
    $script72  3 ; >> $QLalog  #turn on telnet and SSH on
    results_value=`expr $results_value + 1`
fi

}


#checking SQL databse value of telnet status.

#result back
function Automation_test_status(){
if [ $1 -eq 1 ]
then
    echo "realtimeupdate.sh error_ to update Telnet switch" >> $QLalog
    errors_value=`expr $errors_value + 1`
    
elif [ $1 -eq 0 ]
then
    echo "Telnet <--> SSH switch is working well!"          >> $QLalog
fi
}


#setting telnet status in databse value to work with DRIVE UI.
DB_telnet_value
if [ "$database_value" = "TRUE" ]
    then
            echo "Telnet service is running. DB value is $database_value"      >> $QLalog
            echo "trying to set telnet off "                                   >> $QLalog
            set_telnet_SSH_status '1'                                          >> $QLalog
            telnet_state
                if [ "$database_value" = "TRUE" ]
                then
                                echo "The Telnet turn off failed in this test."       >> $QLalog
                                Automation_test_status '1'
                                errors_value=`expr $errors_value + 1`
                else
                                echo "setting telnet status back to DB value : TRUE"  >> $QLalog
                                set_telnet_SSH_status '3'                             >> $QLalog
                                DB_telnet_value
                                Automation_test_status '0'
                                results_value=`expr $results_value + 1`
                fi

elif [ "$database_value" = "FALSE" ]
    then
        echo "Telnet service is not running. DB value is $database_value"  >> $QLalog
        echo "trying to set telnet on and SSH off"                         >> $QLalog
        set_telnet_SSH_status '2'                                          >> $QLalog
        telnet_state
        SSH_status
                if [ "$database_value" = "FALSE" ]
                then
                                echo "The value is not set TRUE failed in this test. realtimeupdate.sh Error_in" >> $QLalog
                                Automation_test_status '1'
                                errors_value=`expr $errors_value + 1`
                else
                                echo "setting telnet status back to DB value : $database_value" >> $QLalog
                                set_telnet_SSH_status '3'                                       >> $QLalog
                                /sbin/chkconfig --list sshd                                     >> $QLalog
                                Automation_test_status '0';
                                results_value=`expr $results_value + 1`
                fi

fi


# reverting back to orignal setup of telnet and SSH Data base values in DMS


echo "Reverting back to orignal setup for telnet and SSH in Drive"  >> $QLalog
if [ "$Telnet_ORG" = "FALSE" ]
then
        set_telnet_SSH_status '1'    #turn off telnet and SSH on
        results_value=`expr $results_value + 1`
elif [ "$Telnet_ORG" = "TRUE" ]
then
        set_telnet_SSH_status '2'   #turn on telnet and SSH off
        results_value=`expr $results_value + 1`
elif [ "$Telnet_ORG" = "$SSH_ORG" ]
then
        set_telnet_SSH_status '3'   #turn on telnet and SSH on
        results_value=`expr $results_value + 1`
fi



if [ $errors_value -ne 0 ]
   then
        SSH_status
        telnet_state
        echo "Tests failed result :$errors_value and Tests passed results:$results_value "   >> $QLalog
        echo "Tests failed: $errors_value  and  Tests Passed: $results_value  "
elif [ $results_value -gt 0 ]
    then
        SSH_status
        telnet_state
        echo "Test Passed results:$results_value  and  Tests failed result :$errors_value        "   >> $QLalog
        echo "Tests Passed: $results_value  and  Tests failed: $errors_value"
fi

#END of automation test script for QL010D
